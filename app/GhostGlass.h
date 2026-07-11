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
#pragma once
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

    void setPanes (std::vector<juce::Rectangle<int>> p, int m)
    {
        panes = std::move (p);
        mode = m;
        setVisible (mode != off && ! panes.empty());
        repaint();
    }

    // host clock drives the breath — repaint ONLY the panes. This overlay spans the
    // whole window (always-on-top, transparent), so a bare repaint() here re-rastered
    // EVERY component beneath it 30x/s for the entire proposal lifetime — the
    // main-thread saturation Chezy felt as "everything is laggy" (LAG DOSSIER v2 #1).
    // setPanes() still full-repaints on geometry change, so old pane areas clear.
    void tick()
    {
        if (! isVisible()) return;
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
        if (mode == off) return;
        const auto tint = mode == composing ? theme::accentB
                        : mode == pending   ? theme::accent : theme::good;
        const double t = (double) juce::Time::getMillisecondCounter();
        const float breath = 0.5f + 0.5f * (float) std::sin (t * 2.0 * juce::MathConstants<double>::pi / 1600.0);

        for (auto& pr : panes)
        {
            auto r = pr.toFloat().reduced (1.0f);
            if (r.isEmpty()) continue;
            // HEARING is already told by the solid preview (canvas follows ears) —
            // milky bodies stacked on bright audition lanes read as a GLITCH
            // (Chezy live 2026-07-06, untitled_11 x4 lanes). Edge + mark only.
            if (mode != hearing)
            {
                // frosted body - the take is BEHIND glass, not applied
                // (alpha FROZEN mid-breath: the body is outside the tick's edge
                //  dirty rects, so an animated alpha would tear across regions)
                g.setColour (juce::Colours::white.withAlpha (0.037f));
                g.fillRoundedRectangle (r, 7.0f);
                g.setColour (tint.withAlpha (0.050f));
                g.fillRoundedRectangle (r, 7.0f);
                // top sheen - glass, not fog
                auto sheen = r.withHeight (juce::jmin (16.0f, r.getHeight() * 0.35f));
                g.setGradientFill ({ juce::Colours::white.withAlpha (0.07f), sheen.getTopLeft(),
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
        }
    }

private:
    std::vector<juce::Rectangle<int>> panes;
    int mode = off;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (GhostGlass)
};
