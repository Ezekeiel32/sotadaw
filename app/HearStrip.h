// HearStrip — the sound tensor, visible (#38): a mel×time heatmap of a render.
// Shells tools/hear.py --json in the background and paints the grid — low
// frequencies at the bottom, time left to right, brand-heat colors, onset
// ticks underneath. The agent's eyes, now the human's too.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{

class HearStrip : public juce::Component, private juce::Thread
{
public:
    // click the tensor to navigate: 0..1 across the render
    std::function<void (double)> onSeekNormalized;
    HearStrip() : juce::Thread ("hear") {}
    ~HearStrip() override
    {   // NEVER let stopThread escalate to pthread_cancel while run() is blocked
        // in child I/O — the forced unwind hits a noexcept frame and the WHOLE
        // APP aborts ("terminate called without an active exception"; gdb-proven
        // on the time-machine repro, 2026-07-11). Kill the child FIRST: its EOF
        // unblocks readAllProcessOutput and the thread exits on its own feet.
        signalThreadShouldExit();
        {
            juce::ScopedLock sl (dataLock);
            if (activeChild != nullptr) activeChild->kill();
        }
        stopThread (4000);
    }

    // transport presence: the tensor shows WHERE you are (host clock feeds
    // 0..1 while playing, <0 when stopped). Two thin columns repaint, never
    // the whole strip — the seek affordance finally has a position answer.
    void setPlayheadNorm (double n)
    {
        if ((n < 0 && playNorm < 0) || std::abs (n - playNorm) < 5e-4) return;
        {
            juce::ScopedLock sl (dataLock);
            if (grid.empty()) { playNorm = n; return; }
        }
        auto beamCol = [this] (double v)
        {
            if (v < 0 || getWidth() <= 12) return;
            repaint ((int) (6.0 + v * (getWidth() - 12.0)) - 4, 0, 9, getHeight());
        };
        const double old = playNorm;
        playNorm = n;
        beamCol (old);
        beamCol (n);
    }

    // direct injection: in-process analysis (and the paint harness) feed the
    // tensor without shelling hear.py — same fields the JSON path fills
    void setTensor (std::vector<std::vector<int>> g, std::vector<int> ons,
                    double durSec, double bpm, const juce::String& labelText)
    {
        {
            juce::ScopedLock sl (dataLock);
            grid = std::move (g);
            onsets = std::move (ons);
            durS = durSec;
            barBpm = bpm;
            label = labelText;
        }
        repaint();
    }

    // fire-and-forget: analyze this wav (background), repaint when ready
    void loadWav (const juce::File& wav, double bpm, const juce::String& labelText,
                  const juce::File& repoRoot)
    {
        if (! wav.existsAsFile()) return;
        {
            juce::ScopedLock sl (dataLock);   // run() reads these under the same lock
            pendingWav = wav;
            pendingBpm = bpm;
            root = repoRoot;
        }
        label = labelText;
        if (! isThreadRunning())
            startThread();
    }

    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        g.setColour (theme::inset);                              // the tensor lives in a well
        g.fillRoundedRectangle (r, 6.0f);
        g.setGradientFill ({ juce::Colours::black.withAlpha (0.35f), r.getTopLeft(),
                             juce::Colours::black.withAlpha (0.0f),
                             { r.getX(), r.getY() + 8.0f }, false });
        g.fillRoundedRectangle (r, 6.0f);
        g.setColour (theme::accentB.withAlpha (0.18f));
        g.drawRoundedRectangle (r.reduced (0.5f), 6.0f, 1.0f);
        juce::ScopedLock sl (dataLock);
        if (grid.empty())
        {
            g.setColour (juce::Colours::white.withAlpha (0.28f));
            g.setFont (juce::Font (juce::FontOptions (10.5f)));
            g.drawText ("hear: the sound tensor appears here after a proposal or export",
                        getLocalBounds(), juce::Justification::centred);
            return;
        }
        const int rows = (int) grid.size();
        const int cols = (int) grid[0].size();
        auto area = getLocalBounds().reduced (6, 4);
        auto onsetArea = area.removeFromBottom (5);
        auto labelArea = area.removeFromTop (11);
        {   // identity chip: what you're seeing, chip-labelled like everything else
            const auto f = theme::caps (7.5f);
            const float lw = theme::measure (f, label) + 24.0f;
            theme::chip (g, { (float) labelArea.getX(), (float) labelArea.getY() - 1.0f,
                              juce::jmin (lw, (float) labelArea.getWidth()), 12.0f },
                         theme::accentB, label, f, 0.14f, 0.0f);
        }
        const float cw = area.getWidth() / (float) cols;
        const float ch = area.getHeight() / (float) rows;
        for (int rI = 0; rI < rows; ++rI)
            for (int c = 0; c < cols; ++c)
            {
                const int v = grid[(size_t) rI][(size_t) c];      // 0..9
                if (v <= 0) continue;
                const float t = v / 9.0f;
                // brand heat: deep blue -> electric violet -> hot white
                auto col = t < 0.5f
                    ? juce::Colour (0xff2437c8).interpolatedWith (juce::Colour (0xff8a4dff), t * 2.0f)
                    : juce::Colour (0xff8a4dff).interpolatedWith (juce::Colour (0xffffe9ff), (t - 0.5f) * 2.0f);
                g.setColour (col.withAlpha (0.25f + 0.75f * t));
                // row 0 = lowest band -> bottom of the strip
                g.fillRect (area.getX() + c * cw,
                            area.getBottom() - (rI + 1) * ch, cw - 0.5f, ch - 0.5f);
            }
        g.setColour (juce::Colour (0xffffc24d).withAlpha (0.8f));
        for (int c = 0; c < cols && c < (int) onsets.size(); ++c)
            if (onsets[(size_t) c] > 4)
                g.fillRect (onsetArea.getX() + c * cw, (float) onsetArea.getY(), cw - 0.5f, 4.0f);
        if (durS > 0.5 && barBpm > 0)
        {   // bar grid: the tensor gets the same orientation the lanes have
            const double barSec = 4.0 * 60.0 / barBpm;
            const int nBars = (int) (durS / barSec);
            if (nBars >= 1 && nBars <= 400)
                for (int b = 1; b <= nBars; ++b)
                {
                    const float x = area.getX() + (float) (b * barSec / durS) * area.getWidth();
                    if (x >= area.getRight()) break;
                    g.setColour (juce::Colours::white.withAlpha (b % 4 == 0 ? 0.20f : 0.075f));
                    g.drawVerticalLine ((int) x, (float) area.getY(), (float) onsetArea.getBottom());
                }
        }
        if (playNorm >= 0)
        {   // the beam: you are HERE in the sound
            const float x = 6.0f + (float) playNorm * ((float) getWidth() - 12.0f);
            g.setColour (juce::Colours::white.withAlpha (0.10f));
            g.fillRect (x - 2.0f, (float) area.getY(), 5.0f, (float) (onsetArea.getBottom() - area.getY()));
            g.setColour (juce::Colours::white.withAlpha (0.85f));
            g.drawVerticalLine ((int) x, (float) area.getY(), (float) onsetArea.getBottom());
        }
    }

    void mouseDown (const juce::MouseEvent& e) override
    {
        juce::ScopedLock sl (dataLock);
        if (! grid.empty() && onSeekNormalized != nullptr && getWidth() > 12)
            onSeekNormalized (juce::jlimit (0.0, 1.0, (e.x - 6.0) / (getWidth() - 12.0)));
    }

private:
    void run() override
    {
        while (! threadShouldExit())
        {
            juce::File wav;
            double bpm = 0;
            {
                juce::ScopedLock sl (dataLock);
                if (pendingWav == juce::File()) break;
                wav = pendingWav; bpm = pendingBpm;
                pendingWav = juce::File();
            }
            auto base = root.exists() ? root : juce::File::getCurrentWorkingDirectory();
            juce::StringArray cmd { sotadaw::pythonExe(),
                                    base.getChildFile ("tools/hear.py").getFullPathName(),
                                    wav.getFullPathName(), "--json" };
            if (bpm > 0) { cmd.add ("--bpm"); cmd.add (juce::String (bpm)); }
            juce::ChildProcess cp;
            {   // register BEFORE start: a kill between start and registration
                // would strand the read (kill on a not-started child = no-op)
                juce::ScopedLock sl (dataLock);
                activeChild = &cp;
            }
            const bool started = cp.start (cmd);
            const auto out = started ? cp.readAllProcessOutput() : juce::String();
            {
                juce::ScopedLock sl (dataLock);
                activeChild = nullptr;
            }
            if (! started) break;
            if (threadShouldExit()) return;   // killed mid-read: leave quietly
            cp.waitForProcessToFinish (20000);
            auto v = juce::JSON::parse (out.fromFirstOccurrenceOf ("{", true, false));
            if (auto* ga = v.getProperty ("grid", juce::var()).getArray())
            {
                std::vector<std::vector<int>> ng;
                for (auto& row : *ga)
                {
                    std::vector<int> nr;
                    if (auto* ra = row.getArray())
                        for (auto& cell : *ra) nr.push_back ((int) cell);
                    ng.push_back (std::move (nr));
                }
                std::vector<int> no;
                if (auto* oa = v.getProperty ("onsets", juce::var()).getArray())
                    for (auto& o : *oa) no.push_back ((int) o);
                {
                    juce::ScopedLock sl (dataLock);
                    grid = std::move (ng);
                    onsets = std::move (no);
                    durS = (double) v.getProperty ("dur_s", 0.0);
                    barBpm = (double) v.getProperty ("bpm", 0.0);
                }
                juce::MessageManager::callAsync ([sp = juce::Component::SafePointer<HearStrip> (this)]
                                                 { if (sp != nullptr) sp->repaint(); });
            }
        }
    }

    juce::CriticalSection dataLock;
    juce::ChildProcess* activeChild = nullptr;   // run()-local child, killable from outside
    juce::File pendingWav;
    juce::File root;
    double pendingBpm = 0;
    juce::String label;
    double playNorm = -1;                // transport position, 0..1 (<0 = hidden)
    double durS = 0, barBpm = 0;         // bar-grid truth from the analysis JSON
    std::vector<std::vector<int>> grid;
    std::vector<int> onsets;
};

} // namespace sotadaw
