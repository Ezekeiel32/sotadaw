// GhostGlass.h - PHANTOM GLASS: agent state as MATERIAL, never prose.
// While the agent composes / a proposal pends / you listen to the ghost take,
// translucent glass panes float exactly over the lanes being changed - frosted
// body, top sheen, a breathing tinted edge, and THE AGENT'S MARK: a glass corner
// tab holding the agent's 4-point spark glyph (never a bare dot - a naked 5px
// circle read as "weird random bubbles", Chezy live 2026-07-06). The project underneath
// stays fully visible and fully playable (mouse passes straight through); the
// ruler and the bottom story are never covered. Tint IS the mode:
//   violet = composing (diff growing live) - blue = pending (accept/reject)
//   green = you are HEARING the ghost take. No banner. No words.
//
// THE ACCEPTAL MADE LIQUID (2026-07-12): the tint CROSSFADES between modes (no
// snap), the milky body fades OUT as you enter HEARING (the solid preview tells it
// then), and a decision LANDS with a one-shot on the very panes that changed -
// ACCEPT sweeps a light across them as the take settles into the project, REJECT
// dissolves them red as the take drops away. Wave 2 (2026-07-13): a pane NEW to
// the glass (a ghost lane materializing mid-compose, a fresh take's first batch)
// BLOOMS in over PANE_MS instead of popping; birth holds the target tint steady
// (arrival is an alpha event, never a hue slide). Wall-clock eased, driven by the
// host tick(); snapshot cameras jump to the settled frame.
#pragma once
#include <cstdlib>
#include <map>
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class GhostGlass : public juce::Component
{
public:
    enum Mode { off = 0, composing = 1, pending = 2, hearing = 3 };

    GhostGlass()
    {
        setInterceptsMouseClicks (false, false);
        setAlwaysOnTop (true);
    }

    void setPanes (std::vector<juce::Rectangle<int>> p, int m, juce::StringArray keys = {})
    {
        if (m != mode) { prevMode = mode; modeT0 = nowMs(); }   // tint/body crossfade
        // A pane NEW to the glass = its LANE just joined the take (a ghost lane
        // materializing, a first batch landing on a quiet track): it BLOOMS in
        // instead of popping. Identity is the lane's NAME — panes insert mid-list
        // in lane order, so position would bloom the WRONG pane; moves/resizes
        // (scroll, clay rows, fold) keep their key and track INSTANTLY: the glass
        // may never lag the lanes it dresses, only its arrival is eased. A key
        // that leaves the take is forgotten — rejoining later is a fresh arrival.
        {
            const auto t = nowMs();
            std::map<juce::String, juce::uint32> keep;
            for (const auto& k : keys)
            {
                const auto it = paneBorn.find (k);
                keep[k] = it != paneBorn.end() ? it->second : t;
            }
            paneBorn.swap (keep);
        }
        panes = std::move (p);
        paneKeys = std::move (keys);
        mode = m;
        setVisible ((mode != off && ! panes.empty()) || ! flashPanes.empty());
        repaint();
    }

    // A DECISION LANDS on the glass: ACCEPT (true) sweeps a light across the changed
    // panes as the take settles in; REJECT dissolves them red as it drops away. Fire
    // this BEFORE the proposal state is torn down (the panes are captured by value).
    void flash (bool accept)
    {
        if (settled() || panes.empty()) return;   // no visible arrange panes -> the deck
        flashPanes = panes;                        // carries the feedback instead
        flashAccept = accept;
        flashT0 = nowMs();
        flashDur = accept ? 470 : 380;
        setVisible (true);
        toFront (false);
        repaint();
    }

    // host clock drives the breath — repaint ONLY the panes. This overlay spans the
    // whole window (always-on-top, transparent), so a bare repaint() here re-rastered
    // EVERY component beneath it 30x/s for the entire proposal lifetime — the
    // main-thread saturation Chezy felt as "everything is laggy" (LAG DOSSIER v2 #1).
    // setPanes() still full-repaints on geometry change, so old pane areas clear.
    void tick()
    {
        ticked = true;   // ...and it proves we are ON a clock (see settled())
        if (! isVisible()) return;
        const auto t = nowMs();
        // FLASH lifecycle: full-pane repaints while the one-shot plays, then retire
        if (! flashPanes.empty())
        {
            if (t - flashT0 >= (juce::uint32) flashDur)
            {
                flashPanes.clear();
                if (mode == off || panes.empty()) { setVisible (false); return; }
            }
            else
                for (auto& p : flashPanes) repaint (p.expanded (10));
        }
        if (mode == off) { if (flashPanes.empty()) setVisible (false); return; }
        // MODE CROSSFADE: body + tint blend over MODE_MS -> full-pane repaints
        if (mode != prevMode && t - modeT0 < (juce::uint32) MODE_MS && ! instant())
        {
            for (auto& p : panes) repaint (p.expanded (2));
            return;
        }
        // PANE ARRIVAL: a materializing lane's pane blooms -> full repaints for
        // THAT pane only (the rest of the glass stays on the edge-dirty diet)
        if (! instant())
            for (size_t pi = 0; pi < panes.size(); ++pi)
                if (paneAlpha (pi, t) < 0.995f)
                    repaint (panes[pi].expanded (2));
        // WAVE 4 (profiled): only the edge ring + corner tab breathe — the body's
        // 1.4% alpha swing was invisible, yet full-pane repaints re-rastered every
        // lane beneath 30x/s (paint = 60% of process CPU while a take pended over
        // playback). 10Hz reads identical at the 1.6s period; body alpha is frozen
        // in paint() so edge-only dirty rects can never tear it.
        if (++breathTick % 3 != 0) return;
        for (auto& p : panes)
        {
            const auto r = p.expanded (2);
            const int e = 5;
            repaint (r.withHeight (juce::jmin (20, r.getHeight())));   // top edge + tab
            repaint (r.withTrimmedTop (juce::jmax (0, r.getHeight() - e)));
            repaint (r.withWidth (e));
            repaint (r.withTrimmedLeft (juce::jmax (0, r.getWidth() - e)));
        }
    }

    int breathTick = 0;
    void paint (juce::Graphics& g) override
    {
        const auto t = nowMs();
        // ---- decision one-shots ride ON TOP of everything, on the captured panes ----
        if (! flashPanes.empty())
        {
            const float k = juce::jlimit (0.0f, 1.0f,
                (float) (t - flashT0) / (float) juce::jmax (1, flashDur));
            paintFlash (g, k);
        }
        if (mode == off) return;
        const double tau = 2.0 * juce::MathConstants<double>::pi;
        const float breath = 0.5f + 0.5f * (float) std::sin ((double) t * tau / 1600.0);
        // MODE TINT CROSSFADE + BODY FADE (hearing has no milky body -> fade it out).
        // BIRTH holds the TARGET tint steady (prevMode==off would slide blue->violet
        // under the arrival bloom — arrival is an ALPHA event, never a hue event).
        const float mk = settled() ? 1.0f : smooth01 ((float) (t - modeT0) / (float) MODE_MS);
        const auto tint = (prevMode == off ? tintOf (mode) : tintOf (prevMode))
                              .interpolatedWith (tintOf (mode), mk);
        const float bodyPrev = (prevMode == hearing) ? 0.0f : 1.0f;
        const float bodyNew  = (mode == hearing)     ? 0.0f : 1.0f;
        const float bodyMix  = bodyPrev + (bodyNew - bodyPrev) * mk;

        for (size_t pi = 0; pi < panes.size(); ++pi)
        {
            auto r = panes[pi].toFloat().reduced (1.0f);
            if (r.isEmpty()) continue;
            // ARRIVAL BLOOM: a pane new to the glass fades + settles in (a ghost lane
            // materializing mid-compose no longer POPS). A transparency layer carries
            // body, edge, tab and glyph in as ONE object — the proven chip law: alpha
            // on the colour args alone leaves full-alpha strokes flashing first.
            const float ak = paneAlpha (pi, t);
            const bool blooming = ak < 0.995f;
            if (blooming) { r = r.reduced ((1.0f - ak) * 3.0f); g.beginTransparencyLayer (ak); }
            // HEARING is already told by the solid preview (canvas follows ears) —
            // milky bodies stacked on bright audition lanes read as a GLITCH
            // (Chezy live 2026-07-06, untitled_11 x4 lanes). The body CROSSFADES to
            // nothing as you enter hearing, rather than blinking off.
            if (bodyMix > 0.001f)
            {
                // frosted body - the take is BEHIND glass, not applied
                // (alpha FROZEN mid-breath: the body is outside the tick's edge
                //  dirty rects, so an animated alpha would tear across regions)
                g.setColour (juce::Colours::white.withAlpha (0.037f * bodyMix));
                g.fillRoundedRectangle (r, 7.0f);
                g.setColour (tint.withAlpha (0.050f * bodyMix));
                g.fillRoundedRectangle (r, 7.0f);
                // top sheen - glass, not fog
                auto sheen = r.withHeight (juce::jmin (16.0f, r.getHeight() * 0.35f));
                g.setGradientFill ({ juce::Colours::white.withAlpha (0.07f * bodyMix), sheen.getTopLeft(),
                                     juce::Colours::white.withAlpha (0.0f),  sheen.getBottomLeft(), false });
                g.fillRoundedRectangle (sheen, 7.0f);
            }
            // breathing edge - alive while the agent is, and LEGIBLE as a pane
            // (a=0.20 vanished on busy lanes; only the old naked dot survived ->
            //  "WEIRD RANDOM BUBBLES", Chezy live 2026-07-06)
            g.setColour (tint.withAlpha (0.26f + 0.26f * breath));
            g.drawRoundedRectangle (r, 7.0f, 1.5f);
            // THE AGENT'S MARK: a glass corner tab holding the agent's spark glyph —
            // anchored to the pane it belongs to, identifiable as the agent's hand
            // (the same 4-point signature as the wordmark). Never a bare circle.
            if (r.getWidth() > 60.0f && r.getHeight() > 20.0f)
            {
                juce::Rectangle<float> tab (r.getRight() - 24.0f, r.getY() + 1.0f, 23.0f, 15.0f);
                juce::Path tp;   // rounded on the pane's corner side + the inner corner
                tp.addRoundedRectangle (tab.getX(), tab.getY(), tab.getWidth(), tab.getHeight(),
                                        6.0f, 6.0f, false, true, true, false);
                g.setColour (tint.withAlpha (0.22f + 0.12f * breath));
                g.fillPath (tp);
                g.setColour (tint.withAlpha (0.55f));
                g.strokePath (tp, juce::PathStrokeType (1.0f));
                auto sp = tab.withSizeKeepingCentre (9.0f, 9.0f);
                theme::spark (g, sp.expanded (2.5f), tint.withAlpha (0.35f + 0.30f * breath));
                theme::spark (g, sp, juce::Colours::white.withAlpha (0.92f));
            }
            if (blooming) g.endTransparencyLayer();
        }
    }

private:
    void paintFlash (juce::Graphics& g, float k)
    {
        const auto col = flashAccept ? theme::good : theme::bad;
        for (auto& pr : flashPanes)
        {
            auto r = pr.toFloat().reduced (1.0f);
            if (r.isEmpty()) continue;
            if (flashAccept)
            {   // CONFIRM: the take LANDS — the glass glows and a light sweeps across
                g.setColour (col.withAlpha ((1.0f - k) * 0.16f));
                g.fillRoundedRectangle (r, 7.0f);
                g.setColour (col.withAlpha ((1.0f - k) * 0.80f));
                g.drawRoundedRectangle (r, 7.0f, 1.5f);
                const float sweepX = r.getX() + k * r.getWidth();
                const float bandA = std::sin (k * juce::MathConstants<float>::pi) * 0.55f;   // peaks mid-travel
                juce::Rectangle<float> band (sweepX - 24.0f, r.getY(), 48.0f, r.getHeight());
                juce::ColourGradient cg (col.withAlpha (0.0f), band.getX(), r.getCentreY(),
                                         col.withAlpha (0.0f), band.getRight(), r.getCentreY(), false);
                cg.addColour (0.5, juce::Colours::white.withAlpha (bandA));
                juce::Graphics::ScopedSaveState s (g);
                g.reduceClipRegion (r.getSmallestIntegerContainer());
                g.setGradientFill (cg);
                g.fillRect (band);
            }
            else
            {   // DISSOLVE: the take drops away — red tint, shrinks inward + sinks + fades
                auto rr = r.reduced (k * juce::jmin (r.getWidth(), r.getHeight()) * 0.16f)
                           .translated (0.0f, k * 6.0f);
                g.setColour (col.withAlpha ((1.0f - k) * 0.15f));
                g.fillRoundedRectangle (rr, 7.0f);
                g.setColour (col.withAlpha ((1.0f - k) * 0.60f));
                g.drawRoundedRectangle (rr, 7.0f, 1.4f);
            }
        }
    }

    static juce::uint32 nowMs()   { return juce::Time::getMillisecondCounter(); }
    static float smooth01 (float t) { t = juce::jlimit (0.0f, 1.0f, t); return t * t * (3.0f - 2.0f * t); }
    static bool instant()
    {
        static const bool b = std::getenv ("SOTADAW_SNAPSHOT") != nullptr
                           || std::getenv ("SOTADAW_SNAP_GHOST") != nullptr
                           || std::getenv ("SOTADAW_SNAP_AUDSTREAM") != nullptr;
        return b;
    }
    // NEVER TICKED => PAINT SETTLED. uismoke builds a GhostGlass, calls setPanes()
    // and shoots the png WITHOUT a clock: a crossfade keyed off wall-time alone would
    // freeze at k=0 and paint the COMPOSING glass with the previous mode's tint
    // (violet -> blue) in the pixel proof. Motion only for surfaces being driven.
    bool settled() const { return instant() || ! ticked; }
    float paneAlpha (size_t pi, juce::uint32 t) const
    {
        if (settled() || pi >= (size_t) paneKeys.size()) return 1.0f;
        const auto it = paneBorn.find (paneKeys[(int) pi]);
        if (it == paneBorn.end()) return 1.0f;
        return smooth01 ((float) (t - it->second) / (float) PANE_MS);
    }
    static juce::Colour tintOf (int m)
    {
        return m == composing ? theme::accentB
             : m == hearing   ? theme::good
                              : theme::accent;   // pending / fallback
    }
    enum { MODE_MS = 220, PANE_MS = 200 };

    std::vector<juce::Rectangle<int>> panes;
    juce::StringArray paneKeys;                       // pane i belongs to lane paneKeys[i]
    std::map<juce::String, juce::uint32> paneBorn;    // lane name -> arrival stamp
    int mode = 0, prevMode = 0;
    juce::uint32 modeT0 = 0;
    std::vector<juce::Rectangle<int>> flashPanes;
    juce::uint32 flashT0 = 0;
    int flashDur = 0;
    bool flashAccept = false;
    bool ticked = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (GhostGlass)
};
