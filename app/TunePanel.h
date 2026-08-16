// TunePanel.h - THE TUNE LAB: CONTEXT-TUNE (V45) as touchable hardware.
// A bottom drawer for the selected vocal/audio track: style chips (transparent →
// t-pain), strength, DRY/WET ears (harvest vs fcpe), guide-melody picker, region
// from the loop brace, one TUNE button (deterministic, zero tokens, undoable) —
// then the per-note WHY report rendered as rows: sung → target, cents bar, reason.
// LIVE chip = drop fx_retune on the track (the chord-following realtime insert).
// Same law as everything here: the panel edits song.json; agent and hands share one door.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class TunePanel : public juce::Component
{
public:
    std::function<void (const juce::String& style, float strength, bool wetEars,
                        const juce::String& guide, bool useRegion)> onTune;
    std::function<void (bool on, float amount, float retuneMs)> onLive;
    std::function<void (double)> onSeekBeat;   // click a WHY row = hear that correction
    std::function<void()> onClose;

    TunePanel() { setWantsKeyboardFocus (false); }

    // ---------------------------------------------------------------- host -> panel
    void setTarget (const juce::String& trackName, bool clips,
                    const juce::StringArray& noteTracks, const juce::String& regionText,
                    bool liveNow, bool takeCarriesTuning = false)
    {
        track = trackName; hasClips = clips; guides = noteTracks;
        region = regionText; liveOn = liveNow; takeTuned = takeCarriesTuning;
        if (guideSel >= guides.size()) guideSel = -1;
        repaint();
    }
    void setBusy (bool b)                 { busy = b; repaint(); }
    void setReport (const juce::var& v)   { report = v; repScroll = 0; repaint(); }
    int repScroll = 0;   // WHY-report scroll offset (wheel; public: the rig asserts the clamp)
    bool isBusy() const                   { return busy; }
    void tick()                            // host clock: the busy state BREATHES
    {
        if (! busy) return;
        phase += 0.030f;
        if (phase >= 1.0f) phase -= 1.0f;
        repaint (reportR().expanded (2, 2));
        repaint (tuneR().expanded (3, 3));
    }

    // ---------------------------------------------------------------- geometry
    static constexpr int idealHeight = 236;

    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat();
        theme::panelV (g, r, theme::panel, 10.0f);
        g.setColour (theme::line); g.drawRoundedRectangle (r.reduced (0.5f), 10.0f, 1.0f);

        auto area = getLocalBounds().reduced (14, 10);
        auto head = area.removeFromTop (20);
        g.setColour (theme::text);
        g.setFont (juce::Font (juce::FontOptions (14.0f, juce::Font::bold)));
        g.drawText ("TUNE LAB", head.removeFromLeft (86), juce::Justification::centredLeft);
        g.setColour (theme::textDim);
        g.setFont (juce::Font (juce::FontOptions (12.0f)));
        g.drawText (track + (hasClips ? "" : "  -  (no audio clip on this track)"),
                    head, juce::Justification::centredLeft);
        g.setColour (theme::textMute);
        g.drawText ("x", closeR(), juce::Justification::centred);

        // style chips
        static const char* styleLabels[4] = { "TRANSPARENT", "NATURAL", "HARD", "T-PAIN" };
        for (int i = 0; i < 4; ++i)
            chip (g, styleR (i), styleLabels[i],
                  i == styleSel, styleSel == 3 && i == 3 ? theme::warn : theme::accent);

        // strength (with a live % readout — the hand knows what it set)
        auto sr = strengthR();
        g.setColour (theme::textMute);
        g.setFont (juce::Font (juce::FontOptions (10.0f)));
        auto srHead = sr.removeFromTop (11);
        g.drawText ("STRENGTH", srHead, juce::Justification::centredLeft);
        g.setFont (theme::mono (9.0f, juce::Font::bold));
        g.setColour (theme::textDim);
        g.drawText (juce::String ((int) std::lround (strength * 100)) + "%",
                    srHead, juce::Justification::centredRight);
        auto bar = sr.reduced (0, 5);
        g.setColour (theme::inset); g.fillRoundedRectangle (bar.toFloat(), 3.0f);
        auto fill = bar.toFloat(); fill.setWidth (fill.getWidth() * strength);
        g.setGradientFill (theme::brand (fill)); g.fillRoundedRectangle (fill, 3.0f);

        chip (g, earsR(),  wetEars ? "EARS: WET (fcpe)" : "EARS: DRY", wetEars, theme::accentB);
        chip (g, guideR(), guideSel < 0 ? "GUIDE: chords" : "GUIDE: " + guides[guideSel],
              guideSel >= 0, theme::accentB);
        chip (g, regionR(), region.isEmpty() ? "WHOLE TAKE" : "REGION " + region,
              region.isNotEmpty(), theme::accent);

        // TUNE + LIVE
        auto tr = tuneR().toFloat();
        if (busy)
        {   // ALIVE while it works: the brand breathes, never a frozen tile
            const float breath = 0.5f + 0.5f * std::sin (phase * juce::MathConstants<float>::twoPi);
            theme::glowRing (g, tr, theme::accentB, 7.0f, 2.0f + 1.5f * breath);
            g.setGradientFill (theme::brand (tr, 0.45f + 0.30f * breath));
            g.fillRoundedRectangle (tr, 7.0f);
        }
        else { g.setGradientFill (theme::brand (tr)); g.fillRoundedRectangle (tr, 7.0f); }
        g.setColour (busy ? juce::Colours::white.withAlpha (0.85f) : juce::Colour (0xff0a0b10));
        g.setFont (juce::Font (juce::FontOptions (13.0f, juce::Font::bold)));
        g.drawText (busy ? "TUNING" : "TUNE", tuneR(), juce::Justification::centred);
        if (takeTuned)                       // this take CARRIES tuning: the chip wears a halo
            theme::glowRing (g, liveR().toFloat(), theme::good, 7.0f, 2.5f);
        chip (g, liveR(), liveOn ? "LIVE ON (fx_retune)" : "LIVE", liveOn || takeTuned, theme::good);

        // report
        auto rep = reportR();
        g.setColour (theme::inset); g.fillRoundedRectangle (rep.toFloat(), 6.0f);
        if (busy)
        {   // the scan beam sweeps the well while the kernel listens
            const float bx = (float) rep.getX() + phase * (float) rep.getWidth();
            juce::ColourGradient beam (theme::accentB.withAlpha (0.0f), bx - 70.0f, 0.0f,
                                       theme::accentB.withAlpha (0.0f), bx + 70.0f, 0.0f, false);
            beam.addColour (0.5, theme::accentB.withAlpha (0.13f));
            g.setGradientFill (beam);
            g.fillRoundedRectangle (rep.toFloat(), 6.0f);
        }
        auto rr = rep.reduced (10, 6);
        g.setFont (juce::Font (juce::FontOptions (11.0f)));
        if (! report.isObject())
        {
            if (busy)
            {
                g.setColour (theme::textMute);
                g.drawText ("listening, segmenting, choosing targets from the arrangement...",
                            rr, juce::Justification::centred);
                return;
            }
            // DORMANT REPORT (material, not prose): the WHY rows sleep in their own
            // geometry — beat stub, sung->target stub, the signed cents spine — so
            // TUNE wakes them in place. No sentence does the UI's job.
            auto ghost = rr;
            ghost.removeFromTop (4);
            for (int i = 0; i < 3 && ghost.getHeight() >= 15; ++i)
            {
                auto line = ghost.removeFromTop (15);
                const float a = 0.26f - 0.06f * (float) i;             // rows recede to sleep
                g.setColour (theme::textMute.withAlpha (a));
                g.fillRoundedRectangle (line.removeFromLeft (44).reduced (4, 5).toFloat(), 2.0f);
                g.fillRoundedRectangle (line.removeFromLeft (150).reduced (4, 5)
                                            .withTrimmedRight (34 + 12 * i).toFloat(), 2.0f);
                auto barR = line.removeFromLeft (110).reduced (0, 5).toFloat();
                g.setColour (theme::grid.withAlpha (0.9f));            // the spine waits
                g.fillRect (barR.withWidth (1.0f).withX (barR.getCentreX()));
                const float w = i == 0 ? 26.0f : i == 1 ? -17.0f : 9.0f;
                g.setColour (theme::textMute.withAlpha (a + 0.04f));
                if (w >= 0) g.fillRoundedRectangle ({ barR.getCentreX(), barR.getY(), w, barR.getHeight() }, 2.0f);
                else        g.fillRoundedRectangle ({ barR.getCentreX() + w, barR.getY(), -w, barR.getHeight() }, 2.0f);
                g.setColour (theme::textMute.withAlpha (a - 0.04f));
                g.fillRoundedRectangle (line.removeFromLeft (46).reduced (4, 5).toFloat(), 2.0f);
                line.removeFromLeft (2);
                g.fillRoundedRectangle (line.removeFromLeft (58 - 14 * i).reduced (0, 5).toFloat(), 2.0f);
            }
            return;
        }
        auto stats = report.getProperty ("stats", juce::var());
        g.setColour (theme::textDim);
        g.drawText (juce::String ("notes ") + stats.getProperty ("corrected", 0).toString()
                    + "/" + stats.getProperty ("events", 0).toString()
                    + "   median off " + stats.getProperty ("median_abs_cents_off", 0).toString() + "c"
                    + "   vocoder touched " + stats.getProperty ("resynth_pct", 0).toString()
                    + "% (rest bit-exact)",
                    rr.removeFromTop (14), juce::Justification::centredLeft);
        rr.removeFromTop (2);
        auto* notes = report.getProperty ("notes", juce::var()).getArray();
        if (notes == nullptr) return;
        // biggest moves first
        juce::Array<juce::var> rows;
        for (auto& n : *notes) rows.add (n);
        std::sort (rows.begin(), rows.end(), [] (const juce::var& a, const juce::var& b)
                   { return std::abs ((double) a.getProperty ("cents_moved", 0.0))
                          > std::abs ((double) b.getProperty ("cents_moved", 0.0)); });
        const int rowH = 15;
        rowHits.clear();
        const int fits = juce::jmax (0, rr.getHeight() / rowH);
        const int shown = rows.size() > fits ? fits - 1 : rows.size();   // reserve the tail line
        repScroll = juce::jlimit (0, juce::jmax (0, rows.size() - shown), repScroll);
        for (int i = 0; i < shown && rr.getHeight() >= rowH; ++i)
        {
            auto n = rows[repScroll + i];
            const double cents = (double) n.getProperty ("cents_moved", 0.0);
            auto line = rr.removeFromTop (rowH);
            rowHits.push_back ({ line, (double) n.getProperty ("beat0", 0.0) });
            if (line.contains (getMouseXYRelative()))                    // row hover: seekable
            {
                g.setColour (theme::accent.withAlpha (0.07f));
                g.fillRoundedRectangle (line.toFloat(), 3.0f);
            }
            const auto reason = n.getProperty ("reason", "").toString();
            juce::Colour c = std::abs (cents) < 15 ? theme::textMute
                            : std::abs (cents) < 60 ? theme::accent : theme::warn;
            if (reason == "guide") c = theme::accentB;
            if (reason.startsWith ("held")) c = theme::textMute;
            g.setColour (theme::textDim);
            g.drawText ("b" + juce::String ((double) n.getProperty ("beat0", 0.0), 1),
                        line.removeFromLeft (44), juce::Justification::centredLeft);
            g.setColour (theme::text);
            g.drawText (n.getProperty ("sung", "").toString() + "  ->  "
                        + n.getProperty ("target_name", "").toString(),
                        line.removeFromLeft (150), juce::Justification::centredLeft);
            // cents bar (signed)
            auto barR = line.removeFromLeft (110).reduced (0, 4).toFloat();
            g.setColour (theme::grid); g.fillRect (barR.withWidth (1.0f).withX (barR.getCentreX()));
            const float w = (float) juce::jlimit (-1.0, 1.0, cents / 150.0) * (barR.getWidth() * 0.5f);
            g.setColour (c);
            if (w >= 0) g.fillRoundedRectangle ({ barR.getCentreX(), barR.getY(), w, barR.getHeight() }, 2.0f);
            else        g.fillRoundedRectangle ({ barR.getCentreX() + w, barR.getY(), -w, barR.getHeight() }, 2.0f);
            g.setColour (c);
            g.drawText (juce::String (cents > 0 ? "+" : "") + juce::String (cents, 0) + "c",
                        line.removeFromLeft (46), juce::Justification::centredLeft);
            g.setColour (theme::textMute);
            g.drawText (reason, line, juce::Justification::centredLeft);
        }
        if (rows.size() > shown && rr.getHeight() >= 12)   // overflow SPEAKS - and the wheel reaches it
        {
            g.setColour (theme::textMute);
            g.setFont (theme::caps (8.0f));
            const int below = rows.size() - shown - repScroll;
            g.drawText ((repScroll > 0 ? juce::String (repScroll) + " ABOVE / " : juce::String())
                        + juce::String (juce::jmax (0, below))
                        + " BELOW (WHEEL SCROLLS, BIGGEST FIRST)  -  CLICK A ROW TO HEAR IT",
                        rr.removeFromTop (12), juce::Justification::centredLeft);
        }
    }

    void mouseDown (const juce::MouseEvent& e) override
    {
        const auto p = e.getPosition();
        if (closeR().contains (p)) { if (onClose) onClose(); return; }
        for (int i = 0; i < 4; ++i)
            if (styleR (i).contains (p))
            {
                styleSel = i;
                strength = i == 0 ? 0.6f : i == 1 ? 0.85f : 1.0f;   // style defaults
                repaint(); return;
            }
        if (strengthR().contains (p)) { dragStrength (e); return; }
        if (earsR().contains (p))   { wetEars = ! wetEars; repaint(); return; }
        if (guideR().contains (p))  { cycleGuide(); return; }
        if (tuneR().contains (p) && ! busy && hasClips)
        {
            if (onTune) onTune (styleName (styleSel), strength, wetEars,
                                guideSel >= 0 ? guides[guideSel] : juce::String(),
                                region.isNotEmpty());
            return;
        }
        if (liveR().contains (p))
        {
            liveOn = ! liveOn;
            if (onLive) onLive (liveOn, 1.0f, styleSel >= 2 ? 4.0f : 40.0f);
            repaint(); return;
        }
        for (auto& [rct, beat] : rowHits)                 // WHY row = a door to the moment
            if (rct.contains (p))
            {
                if (onSeekBeat) onSeekBeat (beat);
                return;
            }
    }
    void mouseMove (const juce::MouseEvent&) override
    {
        if (report.isObject() && ! rowHits.empty()) repaint (reportR());   // hover follows
    }
    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (strengthR().contains (e.getMouseDownPosition())) dragStrength (e);
    }
    void mouseWheelMove (const juce::MouseEvent& e, const juce::MouseWheelDetails& w) override
    {   // hidden WHY rows are one wheel away, never lost
        if (! report.isObject() || w.deltaY == 0 || ! reportR().contains (e.getPosition())) return;
        repScroll = juce::jmax (0, repScroll + (w.deltaY < 0 ? 3 : -3));   // paint clamps the top
        repaint (reportR());
    }

private:
    juce::String styleName (int i) const
    { return i == 0 ? "transparent" : i == 1 ? "natural" : i == 2 ? "hard" : "tpain"; }

    void chip (juce::Graphics& g, juce::Rectangle<int> r, const juce::String& label,
               bool on, juce::Colour c)
    {
        g.setColour (on ? c.withAlpha (0.18f) : theme::inset);
        g.fillRoundedRectangle (r.toFloat(), 6.0f);
        g.setColour (on ? c : theme::line);
        g.drawRoundedRectangle (r.toFloat().reduced (0.5f), 6.0f, 1.0f);
        g.setColour (on ? theme::text : theme::textDim);
        g.setFont (juce::Font (juce::FontOptions (10.5f, on ? juce::Font::bold : juce::Font::plain)));
        g.drawText (label, r, juce::Justification::centred);
    }
    void dragStrength (const juce::MouseEvent& e)
    {
        auto r = strengthR();
        strength = juce::jlimit (0.0f, 1.0f, (float) (e.position.x - r.getX()) / (float) r.getWidth());
        repaint();
    }
    void cycleGuide()
    {
        guideSel = guideSel + 1 >= guides.size() ? -1 : guideSel + 1;
        repaint();
    }

    // layout map (fixed drawer; report gets the rest)
    juce::Rectangle<int> closeR()  const { return { getWidth() - 30, 8, 20, 20 }; }
    juce::Rectangle<int> styleR (int i) const { return { 14 + i * 96, 36, 88, 24 }; }
    juce::Rectangle<int> strengthR() const { return { 14, 66, 170, 26 }; }
    juce::Rectangle<int> earsR()   const { return { 196, 70, 116, 22 }; }
    juce::Rectangle<int> guideR()  const { return { 320, 70, 150, 22 }; }
    juce::Rectangle<int> regionR() const { return { 478, 70, 120, 22 }; }
    juce::Rectangle<int> tuneR()   const { return { getWidth() - 210, 36, 120, 30 }; }
    juce::Rectangle<int> liveR()   const { return { getWidth() - 210, 70, 120, 22 }; }
    juce::Rectangle<int> reportR() const { return { 14, 98, getWidth() - 28, getHeight() - 108 }; }

    juce::String track, region;
    juce::StringArray guides;
    juce::var report;
    std::vector<std::pair<juce::Rectangle<int>, double>> rowHits;   // WHY row -> beat0
    bool hasClips = false, busy = false, wetEars = false, liveOn = false, takeTuned = false;
    int styleSel = 1, guideSel = -1;
    float strength = 0.85f, phase = 0.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TunePanel)
};
