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
//
// THE ACCEPTAL MADE LIQUID (2026-07-12): every state change EASES, never cuts.
// The deck breathes on the SAME wall-clock 1600ms sine as GhostGlass (one body),
// crossfades its mode tint, fades + rises on birth, and fades OUT on decide so the
// stage never jumps 44px on every verdict (onExitDone reclaims the strip only once
// the fade lands). The EARS cluster settles in from the right, the reject-WHY strip
// reveals, and the edge shimmers while a commit is in flight. All motion is
// wall-clock (frame-rate independent) on the existing 30Hz host tick(); snapshot
// cameras (SOTADAW_SNAP*) jump to the end so the pixel rigs stay deterministic.

#include <cstdlib>
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class ProposalDeck : public juce::Component
{
public:
    struct TakeChip { juce::String text; juce::Colour col; };

    ProposalDeck (juce::Component& badge, juce::Component& audition,
                  juce::Component& explain,
                  juce::Component& accept, juce::Component& reject,
                  juce::Component& cherryBar)
        : badgeC (badge), auditionC (audition), explainC (explain), acceptC (accept),
          rejectC (reject), barC (cherryBar)
    {
        setInterceptsMouseClicks (false, true);   // the glass never eats the stage
        addChildComponent (badgeC);
        addChildComponent (explainC);             // P78: the take explains itself
        addChildComponent (auditionC);
        addChildComponent (acceptC);
        addChildComponent (rejectC);
        addChildComponent (barC);
        // REJECT SPEAKS: the first Reject arms this strip — one line of WHY
        // teaches the producer-agent; Esc keeps deciding, Enter (or Reject
        // again) sends. Exists only while armed (no idle text-state).
        addChildComponent (reasonBox);
        reasonBox.setTextToShowWhenEmpty ("give it a note - one line teaches the producer; "
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
        armT0 = nowMs();                         // the WHY strip reveals, never snaps
        setInterceptsMouseClicks (true, true);   // the strip's chips are clickable
        reasonBox.setVisible (true);
        if (! settled()) reasonBox.setAlpha (0.0f);
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
        reasonBox.setAlpha (1.0f);
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

    // fired ONCE when the exit fade lands: the host reclaims the deck's strip so the
    // stage rises only after the deck is gone (no 44px jump the instant you decide).
    std::function<void()> onExitDone;

    void setMode (int m)              // GhostGlass::Mode values (0 off / 1 composing
    {                                 //  / 2 pending / 3 hearing)
        if (m == 0) { beginExit(); return; }   // leaving is a FADE, not a cut
        if (mode == m && ! exiting) return;
        exiting = false; exitReported = false;   // a fresh take cancels any exit
        if (mode == 0)                           // BIRTH: fade + rise in
        {
            aliveT0 = nowMs();
            if (! settled()) { setAlpha (0.0f); curAlpha = 0.0f; }
        }
        if (mode != m) { prevMode = mode; modeT0 = nowMs(); }   // tint crossfade
        mode = m;
        if (mode != 2) disarmReject();   // the question only exists while pending
        resized();   // decision hardware visibility changes with the mode — a
                     // stale PENDING layout left "Listen: LIVE" parked over the
                     // EARS cluster on the next composing take (2026-07-11)
        repaint();
    }
    void beginExit()                  // the take is decided/gone: fade out, then retire
    {
        if (mode == 0 || exiting) return;
        exiting = true; exitReported = false; exitT0 = nowMs();
        disarmReject();
        if (settled()) retireNow();
        else repaint();
    }
    bool alive() const                { return mode != 0; }
    void finishExitNow()              // teardown that must land THIS frame (rig shots run
    {                                 // the whole camera list in ONE callback — no timer
        if (exiting) retireNow();     // ever advances the fade, so a begun exit would
    }                                 // reserve a dead 48px band in every later face)
    bool layoutAlive() const          { return mode != 0 || exiting; }   // host: reserve
    int neededHeight() const          { return 44 + (barC.isVisible() ? 22 : 0); }
    void setBusy (bool b)             { if (busy != b) { busy = b; if (! b) busyT0 = 0; else busyT0 = nowMs(); repaint(); } }

    void setTake (int addedN, int removedN, int propsN,
                  std::vector<TakeChip> tracks, juce::StringArray sectionNames)
    {
        const bool grew = addedN != added || removedN != removed
                        || propsN != props || tracks.size() != chips.size();
        added = addedN; removed = removedN; props = propsN;
        chips = std::move (tracks);
        sections = std::move (sectionNames);
        if (grew && ! settled()) { chipGlow = 1.0f; chipT0 = nowMs(); }   // the newest info glows, then settles
        repaint();
    }
    void clearTake()                  { setTake (0, 0, 0, {}, {}); clearEars(); }

    // THE DECK'S EARS: the sidecar renders + analyzes every take — the verdict
    // belongs ON the decision surface, not in a chat card across the room.
    void setEars (double peakDb, int clippedN, double lufsV)
    {
        if (! hasEars) earsT0 = nowMs();   // first arrival slides + fades in from the right
        hasEars = true; earsStale = false;
        peak = peakDb; clipped = clippedN; lufs = lufsV;
        repaint();
    }
    void staleEars()                  { if (hasEars && ! earsStale) { earsStale = true; staleT0 = nowMs(); repaint(); } }
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

    void tick()                       // host 30Hz clock: ease transitions, breathe while alive
    {
        ticked = true;   // ...and it proves we are ON a clock (see settled())
        if (! isVisible()) return;
        const auto t = nowMs();
        // ENTRANCE / EXIT alpha (component-level — the panel and its children fade as one)
        float wa = 1.0f;
        if (exiting)
        {
            const float k = span (t, exitT0, EXIT_MS);
            wa = 1.0f - k;
            if (k >= 1.0f) { retireNow(); return; }
        }
        else if (mode != 0 && t - aliveT0 < (juce::uint32) ENTER_MS && ! settled())
            wa = span (t, aliveT0, ENTER_MS);
        if (std::abs (wa - curAlpha) > 0.004f) { curAlpha = wa; setAlpha (wa); }
        // the reject-WHY editor fades in with its strip
        if (armed && ! settled())
        {
            const float ak = span (t, armT0, ARM_MS);
            if (reasonBox.getAlpha() < ak - 0.02f || ak >= 1.0f) reasonBox.setAlpha (ak);
        }
        // chip glow decays after each streamed update
        if (chipGlow > 0.0f) chipGlow = juce::jlimit (0.0f, 1.0f, 1.0f - (float) (t - chipT0) / (float) CHIP_MS);
        if (! alive() && ! exiting) return;
        // repaint EVERY frame while a transition is live; otherwise 10Hz breath is
        // plenty for a 1.6s glow (WAVE 4 profiled the full-strip raster storm)
        if (transitioning (t)) { repaint(); return; }
        if (++deckTick % 3 != 0) return;
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
        place (explainC, 74);                // P78: the walk-through door
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
        if (! alive() && ! exiting) return;
        const auto t = nowMs();
        // ONE BREATH: the exact wall-clock sine GhostGlass uses (1600ms) — deck and
        // glass now pulse in unison, one organism, never two out-of-phase clocks.
        const float br = 0.5f + 0.5f * (float) std::sin ((double) t * 2.0 * juce::MathConstants<double>::pi / 1600.0);
        // MODE TINT CROSSFADE: blend the previous mode's colour into the new one
        const float mk = settled() ? 1.0f : span (t, modeT0, MODE_MS);
        const auto tint = tintOf (prevMode).interpolatedWith (tintOf (mode), mk);
        // BIRTH RISE: the painted body lifts a few px into place under the fade
        const float ek = (mode != 0 && ! exiting && ! settled()) ? span (t, aliveT0, ENTER_MS) : 1.0f;
        juce::Graphics::ScopedSaveState save (g);
        if (ek < 1.0f) g.addTransform (juce::AffineTransform::translation (0.0f, (1.0f - ek) * 5.0f));

        auto full = getLocalBounds().toFloat().reduced (0.5f);
        g.setColour (theme::panel.withAlpha (0.82f));   // pass 4: fuller glass presence
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

        // BUSY SHIMMER: a travelling catch-light rides the top edge while the commit
        // is in flight (Accept -> the sidecar round-trip). No prose "Accepting..." glow.
        if (busy)
        {
            const float ph = (float) std::fmod ((double) t / 850.0, 1.0);
            const float sx = full.getX() + ph * full.getWidth();
            juce::Rectangle<float> blob (sx - 34.0f, full.getY() - 2.0f, 68.0f, 6.0f);
            juce::ColourGradient cg (juce::Colours::transparentWhite, blob.getX(), blob.getCentreY(),
                                     juce::Colours::transparentWhite, blob.getRight(), blob.getCentreY(), false);
            cg.addColour (0.5, theme::good.withAlpha (0.55f));
            g.setGradientFill (cg);
            g.fillRoundedRectangle (blob, 3.0f);
        }

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
        {   // the reason strip owns the band while armed: a bad-tinted edge asks WHY.
            // it REVEALS (the edge + chips fade in) rather than snapping into being.
            const float rk = settled() ? 1.0f : span (t, armT0, ARM_MS);
            g.setColour (theme::bad.withAlpha ((0.30f + 0.25f * br) * rk));
            g.drawRoundedRectangle (full, 9.0f, 1.2f);
            const auto f = theme::ui (9.0f, juce::Font::bold);
            const auto ps = reasonPresets();
            {   // the preset chips SLIDE + FADE in as one (a transparency layer fades
                // chip body AND label together — chip()'s label is full-alpha otherwise)
                juce::Graphics::ScopedSaveState s2 (g);
                g.addTransform (juce::AffineTransform::translation ((1.0f - rk) * 10.0f, 0.0f));
                if (rk < 0.995f) g.beginTransparencyLayer (rk);
                for (int i = 0; i < (int) presetRects.size() && i < ps.size(); ++i)
                    theme::chip (g, presetRects[(size_t) i].toFloat(), theme::bad,
                                 ps[i], f, 0.12f, 0.8f);
                if (rk < 0.995f) g.endTransparencyLayer();
            }
            return;
        }
        // THE EARS CLUSTER: LUFS / dBTP / clipped, right-anchored in the chip band.
        // Red = clipping, amber = hot peak, dim = a newer take streamed past this
        // render (stale). On first arrival it SETTLES in — a short slide from the
        // right under a fade; going stale CROSSFADES to mute, never snaps dark.
        if (hasEars)
        {
            const float esK = settled() ? 1.0f : span (t, earsT0, EARS_MS);      // arrival
            const float stK = (earsStale && ! settled()) ? span (t, staleT0, STALE_MS) : (earsStale ? 1.0f : 0.0f);
            auto ez = row.removeFromRight (192).reduced (0, 7);
            juce::Graphics::ScopedSaveState s3 (g);
            if (esK < 1.0f) g.addTransform (juce::AffineTransform::translation ((1.0f - esK) * 12.0f, 0.0f));
            const bool bad = clipped > 0, hot = peak > -0.95;
            const auto live = bad ? theme::bad : hot ? theme::warn : theme::good;
            const auto base = live.interpolatedWith (theme::textMute, stK);       // stale crossfade
            const float a = (0.95f - 0.50f * stK) * esK;
            g.setColour (theme::inset.withAlpha (0.6f * esK));
            g.fillRoundedRectangle (ez.toFloat(), 8.0f);
            g.setColour (base.withAlpha (0.35f * a));
            g.drawRoundedRectangle (ez.toFloat().reduced (0.5f), 8.0f, 1.0f);
            auto tz = ez.reduced (9, 2);
            {   // instrument furniture: a real LED ladder speaks the loudness
                // before any number does (meterLo->meterHi, stale-dimmed with
                // the cluster; -30..-8 LUFS spans the ladder)
                auto lad = tz.removeFromLeft (40).reduced (0, 4).toFloat();
                const float frac = juce::jlimit (0.0f, 1.0f, (float) ((lufs + 30.0) / 22.0));
                theme::ledMeter (g, lad, frac * esK * (1.0f - 0.45f * stK),
                                 theme::meterLo, theme::meterHi, false);
                tz.removeFromLeft (6);
            }
            g.setColour (base.withAlpha (a));
            g.setFont (theme::mono (10.5f));
            g.drawText (juce::String (lufs, 1) + " LUFS", tz.removeFromLeft (66),
                        juce::Justification::centredLeft);
            g.setColour (theme::textDim.interpolatedWith (theme::textMute, stK).withAlpha (a));
            g.setFont (theme::mono (9.0f));
            g.drawText (juce::String (peak, 1) + " pk", tz.removeFromLeft (50),
                        juce::Justification::centredLeft);
            const float dy = (float) tz.getCentreY();
            g.setColour (base.withAlpha (a));
            g.fillEllipse ((float) tz.getX() + 2.0f, dy - 3.5f, 7.0f, 7.0f);
            g.setFont (theme::mono (9.0f));
            g.drawText (clipped > 0 ? juce::String (clipped) : juce::String ("0"),
                        tz.withTrimmedLeft (13), juce::Justification::centredLeft);
        }
        // take chips: counts first, then the touched tracks, then the shape. The
        // newest streamed info carries a decaying glow so a growing take reads alive.
        const auto f = theme::ui (9.5f, juce::Font::bold);
        const float glow = chipGlow;
        auto chip = [&g, &row, &f, glow] (const juce::String& t, juce::Colour c, float bgA, float fgA)
        {
            const int w = (int) theme::measure (f, t) + 26;   // room for chip()'s own inset
            if (row.getWidth() < w + 4) return;
            auto cr = row.removeFromLeft (w).reduced (0, 9);
            theme::chip (g, cr.toFloat(), c, t, f,
                         bgA + 0.10f * glow, juce::jmin (1.0f, fgA + 0.12f * glow));
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
    // ----- motion kernel (wall-clock, frame-rate independent) -----
    static juce::uint32 nowMs()       { return juce::Time::getMillisecondCounter(); }
    static float smooth (float t)     { t = juce::jlimit (0.0f, 1.0f, t); return t * t * (3.0f - 2.0f * t); }
    static float span (juce::uint32 now, juce::uint32 t0, int ms)   // eased 0..1 over ms
    { return smooth ((float) (now - t0) / (float) juce::jmax (1, ms)); }
    static bool instant()             // snapshot cameras jump to the settled frame
    {
        static const bool b = std::getenv ("SOTADAW_SNAPSHOT") != nullptr
                           || std::getenv ("SOTADAW_SNAP_GHOST") != nullptr
                           || std::getenv ("SOTADAW_SNAP_AUDSTREAM") != nullptr;
        return b;
    }
    // NEVER TICKED => PAINT SETTLED. A surface that paints without a clock (offscreen
    // pixel proofs build components, poke them, and shoot) would otherwise freeze at
    // frame 0 of every ease — an entrance would render the deck at alpha 0, i.e. GONE.
    // Motion is only ever a thing for surfaces that are actually being driven.
    bool settled() const { return instant() || ! ticked; }
    static juce::Colour tintOf (int m)
    {
        return m == 1 ? theme::accentB          // composing: violet
             : m == 3 ? theme::good             // hearing: green
                      : theme::accent;          // pending / fallback: blue
    }
    bool transitioning (juce::uint32 t) const
    {
        return exiting || busy || chipGlow > 0.01f
            || (mode != 0 && t - aliveT0 < (juce::uint32) ENTER_MS)
            || (mode != prevMode && t - modeT0 < (juce::uint32) MODE_MS)
            || (armed && t - armT0 < (juce::uint32) ARM_MS)
            || (hasEars && t - earsT0 < (juce::uint32) EARS_MS)
            || (earsStale && t - staleT0 < (juce::uint32) STALE_MS);
    }
    void retireNow()                  // exit fade landed: hand the strip back to the host
    {
        exiting = false; mode = 0; prevMode = 0;
        curAlpha = 1.0f; setAlpha (1.0f);
        if (! exitReported) { exitReported = true; if (onExitDone) onExitDone(); }
    }
    enum { MODE_MS = 220, ENTER_MS = 230, EXIT_MS = 160, EARS_MS = 280,
           ARM_MS = 200, STALE_MS = 200, CHIP_MS = 340 };

    juce::Component &badgeC, &auditionC, &explainC, &acceptC, &rejectC, &barC;
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
    int deckTick = 0;
    // motion state
    int prevMode = 0;
    juce::uint32 modeT0 = 0, aliveT0 = 0, earsT0 = 0, armT0 = 0, staleT0 = 0, chipT0 = 0, exitT0 = 0, busyT0 = 0;
    float chipGlow = 0.0f, curAlpha = 1.0f;
    bool ticked = false;
    bool exiting = false, exitReported = false, busy = false;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ProposalDeck)
};
