// THE SCALPEL VERDICT chip — the sidecar scope-law result worn where Accept lives.
// Shared by the app (transport row, ui_main.cpp) and uismoke (offscreen pixel proof).
// States: green "SURGICAL: n notes · tracks" / dim "FULL REWRITE" / amber "⚠ OUT OF SCOPE: n".
//
// THE ACCEPTAL MADE LIQUID (2026-07-12): the verdict ARRIVES — it fades in and one
// light sweeps the chip (the same grammar as the accept CONFIRM sweep on the glass),
// so a scope call that changes mid-run reads as a new fact landing, not a silent
// text swap. Wall-clock eased on the host tick(); snapshot cameras jump to settled.
#pragma once
#include <cstdlib>
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{
struct SurgicalBadge : juce::Component, public juce::SettableTooltipClient
{
    juce::String label;
    juce::Colour col { theme::good };

    void paint (juce::Graphics& g) override
    {
        if (label.isEmpty()) return;
        const float k = settled() ? 1.0f
                                  : smooth01 ((float) (nowMs() - bornT0) / (float) BORN_MS);
        auto r = getLocalBounds().toFloat().reduced (0.0f, 4.0f);
        const float fade = juce::jmin (1.0f, k * 2.0f);   // the chip beats the sweep in
        if (fade < 0.995f) g.beginTransparencyLayer (fade);
        theme::chip (g, r, col, label, theme::ui (9.0f, juce::Font::bold), 0.16f, 0.55f);
        if (fade < 0.995f) g.endTransparencyLayer();
        if (k < 1.0f)
        {   // THE VERDICT LANDS: one light travels the chip, clipped to its pill
            const float sx = r.getX() + k * r.getWidth();
            const float a  = std::sin (k * juce::MathConstants<float>::pi) * 0.30f;
            juce::Rectangle<float> band (sx - 12.0f, r.getY(), 24.0f, r.getHeight());
            juce::ColourGradient cg (juce::Colours::transparentWhite, band.getX(), r.getCentreY(),
                                     juce::Colours::transparentWhite, band.getRight(), r.getCentreY(), false);
            cg.addColour (0.5, juce::Colours::white.withAlpha (a));
            juce::Path pill;
            pill.addRoundedRectangle (r, r.getHeight() * 0.5f);
            juce::Graphics::ScopedSaveState s (g);
            g.reduceClipRegion (pill);
            g.setGradientFill (cg);
            g.fillRect (band);
        }
    }

    void tick()   // host clock: only while the arrival is still playing
    {
        ticked = true;   // ...and it proves we are ON a clock (see settled())
        if (! isVisible() || label.isEmpty() || instant()) return;
        if (nowMs() - bornT0 > (juce::uint32) BORN_MS) return;
        repaint();
    }

    // The proposal event's surgical{} object -> chip state + tooltip. Returns true
    // when there is a verdict to wear (label non-empty).
    bool setVerdict (const juce::var& s)
    {
        const auto was = label;
        label.clear();
        setTooltip ({});
        if (! s.isObject()) { setVisible (false); return false; }
        auto arr = [&s] (const char* k)
        {
            juce::StringArray out;
            if (auto* a = s.getProperty (k, juce::var()).getArray())
                for (auto& v : *a) out.add (v.toString());
            return out;
        };
        const auto oos = arr ("out_of_scope");
        const auto rcs = arr ("receipts");
        const auto tks = arr ("touched_tracks");
        const int nNote = (int) s.getProperty ("note_changes", 0);
        if (! (bool) s.getProperty ("clean", true))
        {
            col = theme::warn;
            label = juce::String::fromUTF8 ("⚠ OUT OF SCOPE: ") + juce::String (oos.size());
        }
        else if ((bool) s.getProperty ("full_write", false))
        {
            col = theme::textDim;
            label = "FULL REWRITE";
        }
        else if (nNote > 0 || ! rcs.isEmpty())
        {
            col = theme::good;
            label = "SURGICAL: " + juce::String (nNote) + " note" + (nNote == 1 ? "" : "s")
                  + (tks.isEmpty() ? juce::String()
                                   : juce::String::fromUTF8 (" \xc2\xb7 ")
                                     + tks.joinIntoString ("+").substring (0, 26));
        }
        juce::String tip = rcs.joinIntoString ("\n");
        if (! oos.isEmpty())
            tip += (tip.isEmpty() ? juce::String() : juce::String ("\n"))
                 + "OUT OF SCOPE:\n" + oos.joinIntoString ("\n");
        setTooltip (tip);
        if (label.isNotEmpty() && label != was) bornT0 = nowMs();   // a NEW fact lands
        setVisible (label.isNotEmpty());
        repaint();
        return label.isNotEmpty();
    }

    int preferredWidth() const
    {
        return juce::jlimit (90, 250,
            (int) theme::measure (theme::ui (9.0f, juce::Font::bold), label) + 30);
    }

private:
    static juce::uint32 nowMs()     { return juce::Time::getMillisecondCounter(); }
    static float smooth01 (float t) { t = juce::jlimit (0.0f, 1.0f, t); return t * t * (3.0f - 2.0f * t); }
    static bool instant()
    {
        static const bool b = std::getenv ("SOTADAW_SNAPSHOT") != nullptr
                           || std::getenv ("SOTADAW_SNAP_GHOST") != nullptr
                           || std::getenv ("SOTADAW_SNAP_AUDSTREAM") != nullptr;
        return b;
    }
    // NEVER TICKED => PAINT SETTLED. uismoke builds badges, calls setVerdict() and
    // shoots the png WITHOUT a clock — an arrival keyed off wall-time alone would
    // freeze at frame 0 and render the chips INVISIBLE in the pixel proof. Motion
    // is only ever a thing for surfaces that are actually being driven.
    bool settled() const { return instant() || ! ticked; }
    enum { BORN_MS = 560 };
    juce::uint32 bornT0 = 0;
    bool ticked = false;
};
} // namespace sotadaw
