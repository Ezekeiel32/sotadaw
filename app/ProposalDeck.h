#pragma once
// THE PROPOSAL DECK — the take's decision surface lives ON THE STAGE, not in the
// chat (Chezy 2026-07-06: "the agent chat proposal cards are the wrong place").
// One glass bar under the transport, in every view, whenever a take is alive:
//   [mode jewel] [take chips: +notes/-notes, props, touched tracks, shape]
//                                [scalpel verdict] [Audition] [Accept] [Reject]
//   [cherry-pick row (PropItemsBar) when the take has >1 reviewable item]
// The deck HOSTS the existing controls (re-homed as children — wiring stays in
// MainComponent); its chips GROW live while the agent streams a take. Material
// speaks the GhostGlass language: violet composing / blue pending / green hearing.

#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class ProposalDeck : public juce::Component
{
public:
    struct TakeChip { juce::String text; juce::Colour col; };

    ProposalDeck (juce::Component& badge, juce::Component& audition,
                  juce::Component& accept, juce::Component& reject,
                  juce::Component& cherryBar)
        : badgeC (badge), auditionC (audition), acceptC (accept),
          rejectC (reject), barC (cherryBar)
    {
        setInterceptsMouseClicks (false, true);   // the glass never eats the stage
        addChildComponent (badgeC);
        addChildComponent (auditionC);
        addChildComponent (acceptC);
        addChildComponent (rejectC);
        addChildComponent (barC);
        // REJECT SPEAKS: the first Reject arms this strip — one line of WHY
        // teaches the producer-agent; Esc keeps deciding, Enter (or Reject
        // again) sends. Exists only while armed (no idle text-state).
        addChildComponent (reasonBox);
        reasonBox.setTextToShowWhenEmpty ("why? one line teaches the producer - "
                                          "Enter sends, Esc keeps deciding",
                                          theme::textMute);
        reasonBox.onReturnKey = [this] { if (onRejectCommit) onRejectCommit (reasonBox.getText()); };
        reasonBox.onEscapeKey = [this] { disarmReject(); };
    }

    // one-click WHYs — the four complaints producers actually make; click = send.
    // Typing still wins for anything specific.
    static juce::StringArray reasonPresets()
    {
        return { "too bright", "wrong groove", "too busy", "not the vibe" };
    }
    void pressPreset (int i)             // shared by the mouse path and the rig
    {
        const auto ps = reasonPresets();
        if (armed && i >= 0 && i < ps.size() && onRejectCommit)
            onRejectCommit (ps[i]);
    }

    void armReject()
    {
        if (armed) return;
        armed = true;
        setInterceptsMouseClicks (true, true);   // the strip's chips are clickable
        reasonBox.setVisible (true);
        resized();
        reasonBox.grabKeyboardFocus();
        repaint();
    }
    void disarmReject()
    {
        if (! armed) return;
        armed = false;
        setInterceptsMouseClicks (false, true);  // back to glass-over-the-stage
        reasonBox.setText ({}, juce::dontSendNotification);
        reasonBox.setVisible (false);
        resized();
        repaint();
    }
    void mouseUp (const juce::MouseEvent& e) override
    {
        if (! armed) return;
        for (int i = 0; i < (int) presetRects.size(); ++i)
            if (presetRects[(size_t) i].contains (e.getPosition()))
                { pressPreset (i); return; }
    }
    bool rejectArmed() const              { return armed; }
    juce::String rejectReason() const     { return reasonBox.getText().trim(); }
    void setReasonText (const juce::String& t) { reasonBox.setText (t); }   // rig + presets
    std::function<void (juce::String)> onRejectCommit;

    void setMode (int m)              // GhostGlass::Mode values (0 off / 1 composing
    {                                 //  / 2 pending / 3 hearing)
        if (mode == m) return;
        mode = m;
        if (mode != 2) disarmReject();   // the question only exists while pending
        resized();   // decision hardware visibility changes with the mode — a
                     // stale PENDING layout left "Listen: LIVE" parked over the
                     // EARS cluster on the next composing take (2026-07-11)
        repaint();
    }
    bool alive() const                { return mode != 0; }
    int neededHeight() const          { return 44 + (barC.isVisible() ? 22 : 0); }

    void setTake (int addedN, int removedN, int propsN,
                  std::vector<TakeChip> tracks, juce::StringArray sectionNames)
    {
        added = addedN; removed = removedN; props = propsN;
        chips = std::move (tracks);
        sections = std::move (sectionNames);
        repaint();
    }
    void clearTake()                  { setTake (0, 0, 0, {}, {}); clearEars(); }

    // THE DECK'S EARS: the sidecar renders + analyzes every take — the verdict
    // belongs ON the decision surface, not in a chat card across the room.
    void setEars (double peakDb, int clippedN, double lufsV)
    {
        hasEars = true; earsStale = false;
        peak = peakDb; clipped = clippedN; lufs = lufsV;
        repaint();
    }
    void staleEars()                  { if (hasEars && ! earsStale) { earsStale = true; repaint(); } }
    void clearEars()                  { hasEars = false; earsStale = false; repaint(); }
    bool earsPresent() const          { return hasEars; }
    bool earsAreStale() const         { return earsStale; }
    double earsLufs() const           { return lufs; }
    int earsClipped() const           { return clipped; }

    juce::String layoutTruth() const  // rig: hardware never squats on the story band
    {
        auto ok = [this] (const juce::Component& c)
        { return ! c.isVisible() || c.getX() >= chipArea.getRight(); };
        juce::String s;
        s << "chipR=" << chipArea.getRight()
          << " aud=" << (auditionC.isVisible() ? juce::String (auditionC.getX()) : juce::String ("off"))
          << " acc=" << (acceptC.isVisible() ? juce::String (acceptC.getX()) : juce::String ("off"))
          << " rej=" << (rejectC.isVisible() ? juce::String (rejectC.getX()) : juce::String ("off"))
          << " ok=" << ((ok (auditionC) && ok (acceptC) && ok (rejectC)) ? 1 : 0);
        return s;
    }

    void tick()                       // host 30Hz clock: breathe only while alive
    {
        if (! alive() || ! isVisible()) return;
        if (++deckTick % 3 != 0) return;   // WAVE 4: 10Hz — a 1.6s glow needs no
        breath += 0.15f;                   // 30Hz full-strip raster (profiled storm)
        if (breath > juce::MathConstants<float>::twoPi)
            breath -= juce::MathConstants<float>::twoPi;
        repaint();
    }

    void resized() override
    {
        auto r = getLocalBounds();
        auto row = r.removeFromTop (44).reduced (8, 6);
        // right side: the decision hardware (only visible children take space)
        auto place = [&row] (juce::Component& c, int w)
        {
            if (c.isVisible())
                c.setBounds (row.removeFromRight (w).reduced (2, 2));
        };
        place (rejectC, armed ? 100 : 72);   // "Reject anyway" needs its room
        place (acceptC, 76);
        place (auditionC, 104);
        if (badgeC.isVisible())
        {
            const int bw = juce::jmin (240, juce::jmax (90, badgeC.getWidth() > 0
                                                              ? badgeC.getWidth() : 150));
            badgeC.setBounds (row.removeFromRight (bw).reduced (2, 4));
        }
        chipArea = row;               // the rest is the take's story (painted)
        presetRects.clear();
        auto rb = armed ? chipArea.reduced (2, 6) : juce::Rectangle<int>();
        if (armed)
        {   // preset chips claim the strip's right side; the editor keeps the rest
            const auto f = theme::ui (9.0f, juce::Font::bold);
            auto ps = reasonPresets();
            for (int i = ps.size(); --i >= 0;)
            {
                const int w = (int) theme::measure (f, ps[i]) + 20;
                presetRects.insert (presetRects.begin(),
                                    rb.removeFromRight (w).reduced (0, 2));
                rb.removeFromRight (5);
            }
        }
        reasonBox.setBounds (rb);
        if (barC.isVisible())
            barC.setBounds (r.removeFromTop (22).reduced (14, 1));
    }

    void paint (juce::Graphics& g) override
    {
        if (! alive()) return;
        const float br = 0.5f + 0.5f * std::sin (breath);
        const auto tint = mode == 1 ? theme::accentB          // composing: violet
                        : mode == 2 ? theme::accent           // pending: blue
                                    : theme::good;            // hearing: green
        auto full = getLocalBounds().toFloat().reduced (0.5f);
        g.setColour (theme::panel.withAlpha (0.72f));
        g.fillRoundedRectangle (full, 9.0f);
        g.setColour (tint.withAlpha (0.05f + 0.02f * br));
        g.fillRoundedRectangle (full, 9.0f);
        {   // sheen: the glass is lit from above
            auto sheen = full.withHeight (full.getHeight() * 0.45f);
            g.setGradientFill ({ juce::Colours::white.withAlpha (0.06f), sheen.getTopLeft(),
                                 juce::Colours::white.withAlpha (0.0f), sheen.getBottomLeft(), false });
            g.fillRoundedRectangle (sheen, 9.0f);
        }
        g.setColour (tint.withAlpha (0.28f + 0.30f * br));    // breathing edge
        g.drawRoundedRectangle (full, 9.0f, 1.2f);

        // mode jewel
        auto ja = juce::Rectangle<float> ((float) chipArea.getX() - 0.0f,
                                          full.getCentreY() - 22.0f, 0, 0);
        auto row = chipArea;
        auto jewel = row.removeFromLeft (18).toFloat();
        const float jy = jewel.getCentreY(), jx = jewel.getCentreX();
        g.setColour (tint.withAlpha (0.25f + 0.45f * br));
        g.fillEllipse (jx - 5.5f, jy - 5.5f, 11.0f, 11.0f);
        g.setColour (tint);
        g.fillEllipse (jx - 2.5f, jy - 2.5f, 5.0f, 5.0f);
        juce::ignoreUnused (ja);

        if (armed)
        {   // the reason strip owns the band while armed: a bad-tinted edge asks WHY
            g.setColour (theme::bad.withAlpha (0.30f + 0.25f * br));
            g.drawRoundedRectangle (full, 9.0f, 1.2f);
            const auto f = theme::ui (9.0f, juce::Font::bold);
            const auto ps = reasonPresets();
            for (int i = 0; i < (int) presetRects.size() && i < ps.size(); ++i)
                theme::chip (g, presetRects[(size_t) i].toFloat(), theme::bad,
                             ps[i], f, 0.12f, 0.8f);
            return;
        }
        // THE EARS CLUSTER: LUFS / dBTP / clipped, right-anchored in the chip band.
        // Red = clipping, amber = hot peak, dim = a newer take streamed past this
        // render (stale — the next analysis refreshes it).
        if (hasEars)
        {
            auto ez = row.removeFromRight (176).reduced (0, 7);
            const bool bad = clipped > 0, hot = peak > -0.95;
            const auto base = earsStale ? theme::textMute
                            : bad ? theme::bad : hot ? theme::warn : theme::good;
            const float a = earsStale ? 0.45f : 0.95f;
            g.setColour (theme::inset.withAlpha (0.6f));
            g.fillRoundedRectangle (ez.toFloat(), 8.0f);
            g.setColour (base.withAlpha (0.35f * a));
            g.drawRoundedRectangle (ez.toFloat().reduced (0.5f), 8.0f, 1.0f);
            auto tz = ez.reduced (9, 2);
            g.setColour (base.withAlpha (a));
            g.setFont (theme::mono (10.5f));
            g.drawText (juce::String (lufs, 1) + " LUFS", tz.removeFromLeft (74),
                        juce::Justification::centredLeft);
            g.setColour ((earsStale ? theme::textMute : theme::textDim).withAlpha (a));
            g.setFont (theme::mono (9.0f));
            g.drawText (juce::String (peak, 1) + " pk", tz.removeFromLeft (52),
                        juce::Justification::centredLeft);
            const float dy = (float) tz.getCentreY();
            g.setColour (base.withAlpha (a));
            g.fillEllipse ((float) tz.getX() + 2.0f, dy - 3.5f, 7.0f, 7.0f);
            g.setFont (theme::mono (9.0f));
            g.drawText (clipped > 0 ? juce::String (clipped) : juce::String ("0"),
                        tz.withTrimmedLeft (13), juce::Justification::centredLeft);
        }
        // take chips: counts first, then the touched tracks, then the shape
        const auto f = theme::ui (9.5f, juce::Font::bold);
        auto chip = [&g, &row, &f] (const juce::String& t, juce::Colour c, float bgA, float fgA)
        {
            const int w = (int) theme::measure (f, t) + 26;   // room for chip()'s own inset
            if (row.getWidth() < w + 4) return;
            auto cr = row.removeFromLeft (w).reduced (0, 9);
            theme::chip (g, cr.toFloat(), c, t, f, bgA, fgA);
            row.removeFromLeft (5);
        };
        if (added + removed > 0)
            chip ("+" + juce::String (added) + " / -" + juce::String (removed),
                  tint, 0.16f, 0.95f);
        if (props > 0)
            chip (juce::String (props) + " prop", theme::textDim, 0.10f, 0.7f);
        for (auto& tc : chips)
            chip (tc.text, tc.col, 0.13f, 0.85f);
        if (! sections.isEmpty() && sections.size() <= 9)
            chip (sections.joinIntoString (" > "), theme::textMute, 0.07f, 0.6f);
    }

    int mode = 0;

private:
    juce::Component &badgeC, &auditionC, &acceptC, &rejectC, &barC;
    juce::Rectangle<int> chipArea;
    std::vector<TakeChip> chips;
    juce::StringArray sections;
    int added = 0, removed = 0, props = 0;
    bool hasEars = false, earsStale = false;
    double peak = 0.0, lufs = 0.0;
    int clipped = 0;
    juce::TextEditor reasonBox;
    bool armed = false;
    std::vector<juce::Rectangle<int>> presetRects;
    float breath = 0.0f;
    int deckTick = 0;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ProposalDeck)
};
