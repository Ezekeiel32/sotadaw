// THE SCALPEL VERDICT chip — the sidecar scope-law result worn where Accept lives.
// Shared by the app (transport row, ui_main.cpp) and uismoke (offscreen pixel proof).
// States: green "SURGICAL: n notes · tracks" / dim "FULL REWRITE" / amber "⚠ OUT OF SCOPE: n".
#pragma once
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
        theme::chip (g, getLocalBounds().toFloat().reduced (0.0f, 4.0f), col, label,
                     theme::ui (9.0f, juce::Font::bold), 0.16f, 0.55f);
    }

    // The proposal event's surgical{} object -> chip state + tooltip. Returns true
    // when there is a verdict to wear (label non-empty).
    bool setVerdict (const juce::var& s)
    {
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
        setVisible (label.isNotEmpty());
        repaint();
        return label.isNotEmpty();
    }

    int preferredWidth() const
    {
        return juce::jlimit (90, 250,
            (int) theme::measure (theme::ui (9.0f, juce::Font::bold), label) + 30);
    }
};
} // namespace sotadaw
