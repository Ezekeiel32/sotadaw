// PresetBrowser — the 4,366-sound rail, visible (#38).
// Search box + filtered list over library.json vst_presets; double-click
// applies to the selected track (the host resolves params/blob via the
// preset tools). Self-contained: ui_main hooks it with ~15 lines.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{

class PresetBrowser : public juce::Component
{
public:
    struct Entry { juce::String plugin, name, category; };
    // host callbacks: single-click auditions, double-click applies
    std::function<void (const Entry&)> onApply;
    std::function<void (const Entry&)> onAudition;
    std::function<void (const Entry&)> onApplyNew;   // right-click: land it on a NEW track

    PresetBrowser()
    {
        search.setTextToShowWhenEmpty ("search 4,366 sounds... (dark pad, BASS, Surge)",
                                       juce::Colours::white.withAlpha (0.35f));
        search.onTextChange = [this] { refilter(); };
        addAndMakeVisible (search);
        addAndMakeVisible (vp);
        vp.setViewedComponent (&content, false);
        vp.setScrollBarsShown (true, false);
        content.owner = this;
    }

    void loadLibrary (const juce::File& libraryJson)
    {
        all.clear();
        auto v = juce::JSON::parse (libraryJson.loadFileAsString());
        if (auto* arr = v.getProperty ("vst_presets", juce::var()).getArray())
            for (auto& e : *arr)
                all.push_back ({ e.getProperty ("plugin", "").toString(),
                                 e.getProperty ("name", "").toString(),
                                 e.getProperty ("category", "").toString() });
        refilter();
    }

    void resized() override
    {
        auto r = getLocalBounds().reduced (4);
        search.setBounds (r.removeFromTop (24));
        r.removeFromTop (2);
        legend = r.removeFromTop (15);
        r.removeFromTop (3);
        vp.setBounds (r);
        content.setSize (juce::jmax (60, r.getWidth() - 10), (int) shown.size() * rowH + 8);
    }

    void paint (juce::Graphics& g) override
    {
        theme::panelV (g, getLocalBounds().toFloat().reduced (1.0f), theme::panel, 10.0f);
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawRoundedRectangle (getLocalBounds().toFloat().reduced (1.0f), 10.0f, 1.0f);
        // the census strip: what the search found, coloured by plugin family
        const bool filtered = search.getText().trim().isNotEmpty();
        juce::String left = filtered
            ? juce::String (matchTotal) + (matchTotal == 1 ? " match" : " matches")
                  + (matchTotal > (int) shown.size() ? "  -  showing " + juce::String ((int) shown.size()) : "")
            : withCommas ((int) all.size()) + " sounds";
        g.setColour (juce::Colours::white.withAlpha (filtered ? 0.55f : 0.38f));
        g.setFont (juce::Font (juce::FontOptions (9.0f, juce::Font::bold)));
        g.drawText (left, legend.withTrimmedLeft (7), juce::Justification::centredLeft);
        float dx = (float) legend.getRight() - 6.0f;                    // dots read right-to-left
        static const char* fams[] = { "TAL", "Odin", "Effects", "" };   // "" = Surge (the rest)
        for (int i = 3; i >= 0; --i)
        {
            if (perPlugin[i] == 0) continue;
            const auto c = Content::colFor (fams[i]);
            const auto n = juce::String (perPlugin[i]);
            const float tw = theme::measure (theme::mono (8.5f), n);
            dx -= tw + 2.0f;
            g.setColour (c.withAlpha (0.75f));
            g.setFont (theme::mono (8.5f));
            g.drawText (n, (int) dx, legend.getY(), (int) tw + 2, legend.getHeight(),
                        juce::Justification::centredLeft);
            dx -= 7.5f;
            g.setColour (c.withAlpha (0.9f));
            g.fillEllipse (dx, (float) legend.getCentreY() - 2.25f, 4.5f, 4.5f);
            dx -= 8.0f;
        }
    }

    static constexpr int rowH = 22;

private:
    // producers ask in feelings; patch names answer in nouns (mirror of the MCP synonyms)
    static juce::StringArray moodTerms (const juce::String& q)
    {
        struct M { const char* k; const char* alts; };
        static const M moods[] = {
            { "dark",       "deep night noir shadow black" },
            { "warm",       "analog vintage tape soft" },
            { "bright",     "shine sparkle glass air crystal" },
            { "aggressive", "aggro hard dist grit acid monster rage" },
            { "dreamy",     "dream float haze cloud wash lush" },
            { "retro",      "80 vintage juno dx mks analog" } };
        juce::StringArray out;
        out.add (q);
        for (auto& m : moods)
            if (q == m.k)
                out.addTokens (juce::String (m.alts), " ", "");
        return out;
    }

    static juce::String withCommas (int n)            // 4366 -> "4,366"
    {
        return n >= 1000 ? juce::String (n / 1000) + "," + juce::String (n % 1000).paddedLeft ('0', 3)
                         : juce::String (n);
    }

    void refilter()
    {
        shown.clear();
        matchTotal = 0;
        perPlugin[0] = perPlugin[1] = perPlugin[2] = perPlugin[3] = 0;
        const auto q = search.getText().trim().toLowerCase();
        const auto terms = moodTerms (q);
        for (auto& e : all)
        {
            bool hit = q.isEmpty();
            if (! hit)
            {
                const auto hay = (e.plugin + " " + e.category + " " + e.name).toLowerCase();
                for (auto& t : terms)
                    if (hay.contains (t)) { hit = true; break; }
            }
            if (! hit) continue;
            ++matchTotal;                             // census counts EVERYTHING...
            ++perPlugin[e.plugin.contains ("TAL") ? 0 : e.plugin.contains ("Odin") ? 1
                        : e.plugin.contains ("Effects") ? 2 : 3];
            if (shown.size() < 400)                   // ...the list stays snappy
                shown.push_back (&e);
        }
        content.setSize (juce::jmax (60, vp.getWidth() - 10), (int) shown.size() * rowH + 8);
        content.repaint();
        repaint();                                    // census strip follows the query
    }

    struct Content : public juce::Component
    {
        PresetBrowser* owner = nullptr;
        int hover = -1;
        static juce::Colour colFor (const juce::String& plugin)
        {
            if (plugin.contains ("TAL"))     return juce::Colour (0xffe0b34c);
            if (plugin.contains ("Odin"))    return juce::Colour (0xff5cc8ff);
            if (plugin.contains ("Effects")) return juce::Colour (0xffb08aff);
            return juce::Colour (0xff7ddc8a);          // Surge XT
        }
        void paint (juce::Graphics& g) override
        {
            int y = 4, i = 0;
            for (auto* e : owner->shown)
            {
                const auto c = colFor (e->plugin);
                if (i == hover)
                {
                    g.setColour (c.withAlpha (0.13f));
                    g.fillRoundedRectangle (4.0f, (float) y, (float) getWidth() - 8.0f, (float) rowH, 5.0f);
                    g.setColour (c.withAlpha (0.85f));
                    g.fillRoundedRectangle (4.0f, (float) y + 4.0f, 2.5f, (float) rowH - 8.0f, 1.25f);
                }
                g.setColour (c.withAlpha (i == hover ? 0.45f : 0.25f));
                g.fillEllipse (9.5f, (float) y + 7.0f, 8.0f, 8.0f);
                g.setColour (c.brighter (i == hover ? 0.2f : 0.0f));
                g.fillEllipse (11.5f, (float) y + 9.0f, 4.0f, 4.0f);
                g.setColour (juce::Colours::white.withAlpha (i == hover ? 0.95f : 0.85f));
                g.setFont (juce::Font (juce::FontOptions (12.0f)));
                g.drawText (e->name, 25, y, getWidth() - 130, rowH, juce::Justification::centredLeft);
                g.setColour (juce::Colours::white.withAlpha (0.35f));
                g.setFont (juce::Font (juce::FontOptions (9.5f)));
                g.drawText (e->category, getWidth() - 104, y, 100, rowH, juce::Justification::centredRight);
                y += rowH; ++i;
            }
            if (owner->shown.empty())
            {
                g.setColour (juce::Colours::white.withAlpha (0.35f));
                g.setFont (juce::Font (juce::FontOptions (12.0f)));
                g.drawText ("no matches", getLocalBounds(), juce::Justification::centred);
            }
        }
        void mouseMove (const juce::MouseEvent& e) override
        {
            const int idx = (e.y - 4) / rowH;
            if (idx != hover) { hover = idx; repaint(); }
        }
        void mouseExit (const juce::MouseEvent&) override { hover = -1; repaint(); }
        void mouseDown (const juce::MouseEvent& e) override      // click = HEAR it
        {
            const int idx = (e.y - 4) / rowH;
            if (idx < 0 || idx >= (int) owner->shown.size()) return;
            const Entry en = *owner->shown[(size_t) idx];        // copy: refilter can't dangle it
            if (e.mods.isPopupMenu())                            // the row's own menu (G6)
            {
                auto* o = owner;
                juce::PopupMenu m;
                m.addSectionHeader (en.name);
                m.addItem ("Audition (click)", [o, en] { if (o->onAudition) o->onAudition (en); });
                m.addItem ("Apply to selected track (2x-click)",
                           [o, en] { if (o->onApply) o->onApply (en); });
                m.addItem ("Apply on a NEW track", o->onApplyNew != nullptr, false,
                           [o, en] { if (o->onApplyNew) o->onApplyNew (en); });
                m.showMenuAsync ({});
                return;
            }
            if (owner->onAudition)
                owner->onAudition (en);
        }
        void mouseDoubleClick (const juce::MouseEvent& e) override
        {
            const int idx = (e.y - 4) / rowH;
            if (idx >= 0 && idx < (int) owner->shown.size() && owner->onApply)
                owner->onApply (*owner->shown[(size_t) idx]);
        }
        void mouseDrag (const juce::MouseEvent& e) override      // drag a sound onto any lane
        {
            if (e.getDistanceFromDragStart() < 6) return;
            const int idx = (e.getMouseDownY() - 4) / rowH;
            if (idx < 0 || idx >= (int) owner->shown.size()) return;
            auto* en = owner->shown[(size_t) idx];
            if (auto* dnd = juce::DragAndDropContainer::findParentDragContainerFor (this))
                if (! dnd->isDragAndDropActive())
                    dnd->startDragging ("PRESETS\n" + en->plugin + "|" + en->name, this,
                                        theme::dragChip (en->name, colFor (en->plugin)));
        }
    };

    juce::TextEditor search;
    juce::Viewport vp;
    Content content;
    std::vector<Entry> all;
    std::vector<Entry*> shown;
    juce::Rectangle<int> legend;                      // the census strip under the search box
    int matchTotal = 0;
    int perPlugin[4] = { 0, 0, 0, 0 };                // TAL / Odin / Effects / Surge
    friend struct Content;
};

} // namespace sotadaw
