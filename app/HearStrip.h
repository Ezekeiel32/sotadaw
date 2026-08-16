// HearStrip — the sound tensor, visible (#38): a mel×time heatmap of a render.
// Shells tools/hear.py --json in the background and paints the grid — low
// frequencies at the bottom, time left to right, brand-heat colors, onset
// ticks underneath. The agent's eyes, now the human's too.
#pragma once
#include <cmath>
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{

class HearStrip : public juce::Component, private juce::Thread
{
public:
    // click the tensor to navigate: 0..1 across the render
    std::function<void (double)> onSeekNormalized;
    // ONE TIME COLUMN (2026-07-17): when the app hosts the strip under the lane
    // stack, cornerW reserves the header column — identity + stats live THERE and
    // the tensor maps exactly onto the lanes' time column above it (the strip's
    // playhead beam finally lines up with the canvas playhead). cornerW = 0
    // (harness, standalone) keeps the legacy full-bleed layout untouched.
    int cornerW = 0;
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
        stripTempWav.deleteFile();       // the render lane's per-instance scratch
    }

    // rig truth: has an analysis landed? (the --hear-render proof polls this)
    bool hasTensor()
    {
        juce::ScopedLock sl (dataLock);
        return ! grid.empty();
    }

    // THE ONE VERTICAL (Chezy 2026-07-17, "same vertical line like the world"):
    // the tensor is ALWAYS the whole song and wears NO zoom dressing — but the
    // beam rides the WORLD's line: this span (the arrange viewport, normalized
    // song-time) maps the beam to the exact x the canvas playhead holds above,
    // at any zoom. Full view (or unset) = whole-song beam as ever.
    void setViewSpan (double startNorm, double endNorm)
    {
        startNorm = juce::jlimit (0.0, 1.0, startNorm);
        endNorm   = juce::jlimit (0.0, 1.0, endNorm);
        if (endNorm - startNorm >= 0.999)
            startNorm = endNorm = -1.0;
        if (std::abs (startNorm - viewN0) < 5e-4 && std::abs (endNorm - viewN1) < 5e-4)
            return;
        viewN0 = startNorm;
        viewN1 = endNorm;
        repaint();
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
            if (v < 0 || timeW() <= 1.0f) return;
            const double m = beamNorm (v);          // the world's line, view-mapped
            if (m < 0.0 || m > 1.0) return;         // off the world's window: no line
            repaint ((int) (timeX0() + m * timeW()) - 4, 0, 9, getHeight());
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
            pendingWav = juce::File();
            ++epoch;                 // direct truth supersedes any in-flight analysis
        }
        repaint();
    }

    // THE STRIP FOLLOWS THE PROJECT (2026-07-17, "the previous project's bar"):
    // retargeting clears the tensor NOW — the dormant well returns wearing the
    // new identity chip — and bumps the epoch so an in-flight analysis of the
    // OLD subject publishes nowhere. A queued-but-unstarted load drops too, and
    // the in-flight child is KILLED (a doomed render must never make the next
    // project's bar wait behind it).
    void clear (const juce::String& identity)
    {
        {
            juce::ScopedLock sl (dataLock);
            grid.clear();
            onsets.clear();
            durS = barBpm = 0;
            label = identity;
            pendingWav = pendingJson = juce::File();
            viewN0 = viewN1 = -1;        // the new subject's window arrives with
            ++epoch;                     // the next applyViewport feed
            if (activeChild != nullptr) activeChild->kill();
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
            pendingJson = juce::File();
            pendingBpm = bpm;
            root = repoRoot;
            label = labelText;       // under the lock: paint() reads it there
            ++epoch;                 // this load supersedes older in-flight results
            if (activeChild != nullptr) activeChild->kill();
        }
        if (! isThreadRunning())
            startThread();
        notify();                    // a sleeping worker wakes for the fresh slot
    }

    // NO RENDER ON DISK IS NOT NO SOUND (2026-07-17, Chezy: "not fixed!" — an
    // imported record with 14 sounding tracks wore a dormant well): render the
    // SONG ITSELF through the content-addressed cache (tools/render_cache.py —
    // one real render per song state, hits are instant) and hear that. All in
    // the worker; the well stays dormant-with-identity until the truth lands.
    void loadRender (const juce::File& songJson, double bpm, const juce::String& labelText,
                     const juce::File& repoRoot)
    {
        if (! songJson.existsAsFile()) return;
        {
            juce::ScopedLock sl (dataLock);
            pendingJson = songJson;
            pendingWav = juce::File();
            pendingBpm = bpm;
            root = repoRoot;
            label = labelText;
            ++epoch;
            if (activeChild != nullptr) activeChild->kill();
        }
        if (! isThreadRunning())
            startThread();
        notify();
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
        {   // DORMANT EARS (alive wave, material-not-banners law): the sleeping
            // tensor — a ghost mel silhouette over the onset bed at rest. The well
            // SHOWS what lives here; no sentence does the UI's job. Deterministic
            // (two soft humps on a bass floor), so snapshots stay byte-stable.
            auto area = getLocalBounds().reduced (6, 4);
            if (cornerW > 6)
                paintCorner (g, area.removeFromLeft (cornerW - 6));
            auto bed = area.removeFromBottom (5);
            area.removeFromTop (4);
            const int rows = juce::jmax (3, area.getHeight() / 7);
            const int cols = juce::jmax (24, area.getWidth() / 22);
            const float cw = area.getWidth() / (float) cols;
            const float chh = area.getHeight() / (float) rows;
            for (int rI = 0; rI < rows; ++rI)
                for (int c = 0; c < cols; ++c)
                {
                    const float t = (c + 0.5f) / (float) cols;
                    const float hump = 0.42f * std::exp (-26.0f * (t - 0.30f) * (t - 0.30f))
                                     + 0.34f * std::exp (-34.0f * (t - 0.74f) * (t - 0.74f));
                    const float e = 0.30f + hump - (float) rI / (float) rows;
                    if (e <= 0.02f) continue;
                    g.setColour (theme::accentB.withAlpha (juce::jmin (0.22f, 0.05f + 0.18f * e)));
                    g.fillRect (area.getX() + c * cw, area.getBottom() - (rI + 1) * chh,
                                cw - 1.0f, chh - 1.0f);
                }
            g.setColour (theme::accentB.withAlpha (0.14f));           // the onset bed sleeps
            g.fillRect ((float) bed.getX(), (float) bed.getY() + 1.5f, (float) bed.getWidth(), 1.0f);
            if (cornerW > 6)
                ;                                                     // identity lives in the corner
            else if (label.isNotEmpty())
            {   // the sleeping well still says WHOSE ears these are — a retarget to a
                // render-less project must never read as "someone else's bar" (or as
                // nobody's): the same chip the live tensor wears, dimmed to dormant
                const auto row = getLocalBounds().reduced (6, 4);
                const auto f = theme::caps (7.5f);
                const float lw = theme::measure (f, label) + 24.0f;
                theme::chip (g, { (float) row.getX(), (float) row.getY() - 1.0f,
                                  juce::jmin (lw, (float) row.getWidth()), 12.0f },
                             theme::accentB, label, f, 0.10f, 0.0f);
            }
            else
            {
                g.setColour (theme::textMute.withAlpha (0.8f));       // engraved identity
                g.setFont (theme::caps (7.5f));
                g.drawText ("EARS", getLocalBounds().reduced (13, 6), juce::Justification::topLeft);
            }
            return;
        }
        const int rows = (int) grid.size();
        const int cols = (int) grid[0].size();
        auto area = getLocalBounds().reduced (6, 4);
        if (cornerW > 6)
            paintCorner (g, area.removeFromLeft (cornerW - 6));   // identity + stats in
        auto onsetArea = area.removeFromBottom (5);               // the header column —
        if (cornerW <= 6)                                         // the tensor gets its
        {   // legacy full-bleed: chip rides the tensor's top row  // FULL height
            auto labelArea = area.removeFromTop (11);
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
        if (playNorm >= 0 && beamNorm (playNorm) >= 0.0 && beamNorm (playNorm) <= 1.0)
        {   // THE ONE VERTICAL: the beam sits on the WORLD's line — the exact x
            // the canvas playhead holds above, whatever the zoom. The tensor
            // itself never zooms; a playhead outside the world's window draws
            // no line here either (the lanes show none).
            const float x = timeX0() + (float) beamNorm (playNorm) * timeW();
            g.setColour (juce::Colours::white.withAlpha (0.10f));
            g.fillRect (x - 2.0f, (float) area.getY(), 5.0f, (float) (onsetArea.getBottom() - area.getY()));
            g.setColour (juce::Colours::white.withAlpha (0.85f));
            g.drawVerticalLine ((int) x, (float) area.getY(), (float) onsetArea.getBottom());
        }
    }

    void mouseDown (const juce::MouseEvent& e) override
    {   // the strip's ONE gesture stays: click the whole-song tensor = seek there
        if (e.mods.isPopupMenu()) return;
        juce::ScopedLock sl (dataLock);
        if (! grid.empty() && onSeekNormalized != nullptr && timeW() > 1.0f)
            onSeekNormalized (juce::jlimit (0.0, 1.0, normAt ((float) e.x)));
    }

private:
    // the tensor's time span in local coords (corner-aware; legacy 6px insets)
    float timeX0() const { return cornerW > 6 ? (float) cornerW : 6.0f; }
    float timeW()  const { return juce::jmax (1.0f, (float) getWidth() - timeX0() - 6.0f); }
    double normAt (float x) const { return ((double) x - (double) timeX0()) / (double) timeW(); }
    double beamNorm (double songNorm) const
    {   // song-time -> the WORLD's window (identity when the view is the whole song)
        if (viewN0 >= 0.0 && viewN1 > viewN0)
            return (songNorm - viewN0) / (viewN1 - viewN0);
        return songNorm;
    }

    // the header-column corner: identity chip + one stats line (called under dataLock)
    void paintCorner (juce::Graphics& g, juce::Rectangle<int> c)
    {
        const auto f = theme::caps (7.5f);
        auto rowA = c.removeFromTop (15);
        if (label.isNotEmpty())
        {
            const float lw = theme::measure (f, label) + 24.0f;
            theme::chip (g, { (float) rowA.getX(), (float) rowA.getY() + 1.0f,
                              juce::jmin (lw, (float) rowA.getWidth() - 6.0f), 12.0f },
                         theme::accentB, label, f, grid.empty() ? 0.10f : 0.14f, 0.0f);
        }
        juce::String stats ("EARS");
        if (! grid.empty() && durS > 0.5)
        {
            const int m = (int) durS / 60, s = (int) durS % 60;
            stats = juce::String (m) + ":" + juce::String (s).paddedLeft ('0', 2);
            if (barBpm > 0)
                stats << " | " << (int) std::floor (durS * barBpm / 240.0) << " BARS";  // grid-ok: glance stat (floor: the render's tail must not mint a phantom bar), ruler owns meter truth
        }
        g.setColour (theme::textMute.withAlpha (grid.empty() ? 0.55f : 0.8f));
        g.setFont (f);
        g.drawText (stats, c.reduced (2, 1).withTrimmedRight (8), juce::Justification::topLeft);
    }

    void run() override
    {
        // persistent worker: the old loop EXITED when the slot emptied, and a
        // load racing that exit (isThreadRunning() still true while run() was
        // returning) stranded its queue forever — the strip then never filled.
        // Now the worker waits; loadWav's notify() wakes it, the dtor's
        // stopThread() signals it out.
        while (! threadShouldExit())
        {
            juce::File wav, songJson;
            double bpm = 0;
            juce::int64 myEpoch = 0;
            {
                juce::ScopedLock sl (dataLock);
                wav = pendingWav; songJson = pendingJson; bpm = pendingBpm; myEpoch = epoch;
                pendingWav = pendingJson = juce::File();
            }
            if (wav == juce::File() && songJson == juce::File()) { wait (300); continue; }
            auto base = root.exists() ? root : juce::File::getCurrentWorkingDirectory();
            // self-contained python resolver: HearStrip is compiled by uismoke too,
            // which never sees SongLoader.h (PORT_SPEC round-1 CI truth)
            auto hearPy = [&base]() -> juce::String
            {
               #if JUCE_WINDOWS
                auto venv = base.getChildFile (".venv/Scripts/python.exe");
                return venv.existsAsFile() ? venv.getFullPathName() : juce::String ("python");
               #else
                auto venv = base.getChildFile (".venv/bin/python");
                return venv.existsAsFile() ? venv.getFullPathName() : juce::String ("python3");
               #endif
            };
            if (songJson != juce::File())
            {   // THE RENDER LANE: no render on disk — make one through the
                // content-addressed cache (one real render per song state; a
                // repeat open is an instant HIT). The temp wav is per-process
                // and reused; a retarget mid-render kills this child and the
                // epoch drops whatever it produced.
                const auto outWav = stripTempWav;
                juce::StringArray rcmd { hearPy(),
                                         base.getChildFile ("tools/render_cache.py").getFullPathName(),
                                         "render", songJson.getFullPathName(),
                                         outWav.getFullPathName() };
                outWav.deleteFile();          // a FAILED render must read as missing —
                                              // never as the previous job's leftover
                juce::ChildProcess rc;
                {
                    juce::ScopedLock sl (dataLock);
                    if (myEpoch != epoch) continue;   // already retargeted: skip the render
                    activeChild = &rc;
                }
                const bool rStarted = rc.start (rcmd);
                if (rStarted) rc.readAllProcessOutput();   // drain; blocks until EOF
                {
                    juce::ScopedLock sl (dataLock);
                    activeChild = nullptr;
                }
                if (threadShouldExit()) return;
                if (! rStarted || ! outWav.existsAsFile())
                    continue;                 // render failed: dormant well stays honest
                {
                    juce::ScopedLock sl (dataLock);
                    if (myEpoch != epoch) continue;   // subject changed mid-render
                }
                wav = outWav;                 // fall through: hear the fresh truth
            }
            juce::StringArray cmd { hearPy(),
                                    base.getChildFile ("tools/hear.py").getFullPathName(),
                                    wav.getFullPathName(), "--json" };
            if (bpm > 0) { cmd.add ("--bpm"); cmd.add (juce::String (bpm)); }
            juce::ChildProcess cp;
            {   // register BEFORE start: a kill between start and registration
                // would strand the read (kill on a not-started child = no-op)
                juce::ScopedLock sl (dataLock);
                if (myEpoch != epoch) continue;   // retargeted while we rendered
                activeChild = &cp;
            }
            const bool started = cp.start (cmd);
            const auto out = started ? cp.readAllProcessOutput() : juce::String();
            {
                juce::ScopedLock sl (dataLock);
                activeChild = nullptr;
            }
            if (! started) continue;          // no python: back to the wait bench
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
                bool publish = false;
                {
                    juce::ScopedLock sl (dataLock);
                    if (myEpoch == epoch)     // the subject may have changed while
                    {                         // hear.py ran: a stale result is DROPPED,
                        grid = std::move (ng);          // never painted over the new one
                        onsets = std::move (no);
                        durS = (double) v.getProperty ("dur_s", 0.0);
                        barBpm = (double) v.getProperty ("bpm", 0.0);
                        publish = true;
                    }
                }
                if (publish)
                    juce::MessageManager::callAsync ([sp = juce::Component::SafePointer<HearStrip> (this)]
                                                     { if (sp != nullptr) sp->repaint(); });
            }
        }
    }

    juce::CriticalSection dataLock;
    juce::ChildProcess* activeChild = nullptr;   // run()-local child, killable from outside
    juce::File pendingWav;
    juce::File pendingJson;              // render-lane job: no render on disk -> make one
    const juce::File stripTempWav =      // per-instance render scratch (dtor sweeps it)
        juce::File::getSpecialLocation (juce::File::tempDirectory)
            .getChildFile ("sotadaw_strip_" + juce::Uuid().toString().substring (0, 8) + ".wav");
    juce::File root;
    juce::int64 epoch = 0;               // subject generation: publishes gate on it
    double pendingBpm = 0;
    juce::String label;
    double viewN0 = -1, viewN1 = -1;     // the world's window, 0..1 (<0 = full view)
    double playNorm = -1;                // transport position, 0..1 (<0 = hidden)
    double durS = 0, barBpm = 0;         // bar-grid truth from the analysis JSON
    std::vector<std::vector<int>> grid;
    std::vector<int> onsets;
};

} // namespace sotadaw
