// HistoryPanel.h - THE TIME MACHINE v3: history as MATERIAL, not a git log.
// Every version is a CARD carrying a FILMSTRIP - a mini lane-map of the actual
// song at that commit (kept material = track-hue density grid from
// tools/song_history.py, added notes = green, removed = red). A timeline SPINE
// with day separators runs the lineage; rejected/superseded takes hang off it
// as offshoot nodes (roads not taken). Above the list, the LIFE GRAPH: the
// song's note-mass over its whole history - dots are versions, diamonds are
// takes, click anything = time-travel (preview + audition + play, wired by
// ui_main). The NOW card pins the working state on top and is the material
// "return" while previewing - no scary Reject on a version. Arrow keys hop
// versions. ASCII only in string literals (JUCE drawText mangles the rest).
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include <map>
#include "UiTheme.h"

class HistoryPanel : public juce::Component
{
public:
    HistoryPanel() { setWantsKeyboardFocus (true); }

    struct Pt { float b = 0, l = 0.25f; int p = 60; };      // beat, len, pitch
    struct Strip                                             // one lane of the filmstrip
    {
        juce::String name;
        bool propChange = false;                             // knobs/fx moved (amber tick)
        juce::StringArray grid;                              // kept material: hex density rows
        std::vector<Pt> added, removed;                      // the diff - exact points
    };

    struct Row
    {
        juce::String sha, age, subject, song;
        juce::String path;                  // file at this commit (takes live in .takes/)
        int kind = 2;                       // 0 accept - 1 agent - 2 milestone - 3 rejected take - 4 superseded take
        int added = 0, removed = 0;         // semantic note delta vs parent commit
        juce::StringArray touched;          // track names this commit changed
        bool stats = false;                 // semantic pass landed for this row
        juce::int64 epoch = 0;              // commit time (day separators + graph order)
        float beats = 0;                    // tape length at this version
        int mass = 0;                       // total notes at this version (life graph)
        std::vector<Strip> strips;          // the filmstrip
    };

    std::function<void (const juce::String& sha, const juce::String& path)> onPreview;
    std::function<void (bool allSongs)> onScope;
    std::function<void()> onClose;

    void setRows (const std::vector<Row>& r, const juce::String& songName,
                  bool allScope, const juce::String& census,
                  const juce::StringArray& trackChips)
    {
        const bool sameTape = songName == song && allScope == all && ! rows.empty();
        rows = r; song = songName; all = allScope; censusLine = census; chips = trackChips;
        if (! chips.contains (filter)) filter.clear();
        stripCache.clear();
        rebuildLayout();
        if (! sameTape) { scrollY = 0; activeSha.clear(); }
        scrollY = juce::jlimit (0.0f, maxScroll(), scrollY);
        hoverItem = hoverDot = -1;
        repaint();
    }

    void setFilter (const juce::String& trackName)
    {
        filter = chips.contains (trackName) ? trackName : juce::String();
        rebuildLayout(); scrollY = 0; repaint();
    }

    void setActive (const juce::String& sha)                 // the version ON the transport
    {
        if (activeSha == sha) return;
        activeSha = sha;
        if (sha.isNotEmpty()) scrollToSha (sha);
        repaint();
    }

    void tick()                                              // host clock: breath + shimmer
    {
        phase += 1.0f;
        if (activeSha.isNotEmpty() || loadingVisible())
            repaint (listR());
    }

    static constexpr int idealHeight = 324;

    // ------------------------------------------------------------------ paint
    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat();
        theme::panelV (g, r, theme::panel, 10.0f);
        g.setColour (theme::line); g.drawRoundedRectangle (r.reduced (0.5f), 10.0f, 1.0f);

        paintHeader (g);
        if (! all) paintChips (g);
        if (showGraph()) paintGraph (g);
        paintList (g);
    }

    // ------------------------------------------------------------------ input
    void mouseMove (const juce::MouseEvent& e) override
    {
        const int it = itemAt (e.getPosition());
        int dot = -1;
        if (showGraph())
        {
            const auto dots = graphDots();
            dot = nearestDot (dots, e.getPosition().toFloat());
        }
        if (it != hoverItem || dot != hoverDot)
        { hoverItem = it; hoverDot = dot; repaint(); }
    }
    void mouseExit (const juce::MouseEvent&) override { hoverItem = hoverDot = -1; repaint(); }

    void mouseDown (const juce::MouseEvent& e) override
    {
        const auto p = e.getPosition();
        if (closeR().contains (p)) { if (onClose) onClose(); return; }
        if (scopeR (0).contains (p)) { if (all && onScope) onScope (false); return; }
        if (scopeR (1).contains (p)) { if (! all && onScope) onScope (true); return; }
        if (! all)
        {
            for (int i = 0; i <= visibleChips(); ++i)   // clipped chips never take clicks
                if (chipR (i).contains (p))
                {
                    const auto want = i == 0 ? juce::String() : chips[i - 1];
                    filter = filter == want ? juce::String() : want;
                    rebuildLayout(); scrollY = 0; repaint(); return;
                }
        }
        if (showGraph())                                     // life graph: click a dot = travel
        {
            const auto dots = graphDots();
            const int d = nearestDot (dots, p.toFloat());
            if (d >= 0)
            {
                const auto& row = rows[(size_t) dots[(size_t) d].rowIdx];
                scrollToSha (row.sha);
                if (onPreview) onPreview (row.sha, row.path);
                return;
            }
            if (graphR().contains (p)) return;               // graph body: no fallthrough
        }
        const int it = itemAt (p);
        if (it < 0) return;
        const auto& item = items[(size_t) it];
        if (item.type == ItemNow)
        {
            if (activeSha.isNotEmpty() && onPreview) onPreview ({}, {});   // RETURN TO NOW
            return;
        }
        if (item.type == ItemCard && ! all && onPreview)
        {
            const auto& row = rows[(size_t) item.row];
            onPreview (row.sha, row.path);
        }
    }

    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails& w) override
    {
        scrollY = juce::jlimit (0.0f, maxScroll(), scrollY - w.deltaY * 110.0f);
        repaint();
    }

    bool keyPressed (const juce::KeyPress& k) override        // flip takes like pages
    {
        if (k == juce::KeyPress::escapeKey) { if (onClose) onClose(); return true; }
        const bool up = k == juce::KeyPress::upKey, down = k == juce::KeyPress::downKey;
        if ((! up && ! down) || all || ! onPreview) return false;
        std::vector<int> cards;                              // item indices, newest first
        for (int i = 0; i < (int) items.size(); ++i)
            if (items[(size_t) i].type == ItemCard) cards.push_back (i);
        if (cards.empty()) return false;
        int cur = -1;
        for (int i = 0; i < (int) cards.size(); ++i)
            if (rows[(size_t) items[(size_t) cards[(size_t) i]].row].sha == activeSha
                && activeSha.isNotEmpty()) { cur = i; break; }
        if (down)
        {
            const int nxt = juce::jmin ((int) cards.size() - 1, cur + 1);
            if (nxt == cur) return true;
            const auto& row = rows[(size_t) items[(size_t) cards[(size_t) nxt]].row];
            onPreview (row.sha, row.path);
        }
        else
        {
            if (cur <= 0) { if (activeSha.isNotEmpty()) onPreview ({}, {}); return true; }
            const auto& row = rows[(size_t) items[(size_t) cards[(size_t) (cur - 1)]].row];
            onPreview (row.sha, row.path);
        }
        return true;
    }

    void resized() override { rebuildLayout(); }

private:
    // ------------------------------------------------------------- geometry
    enum { ItemNow = 0, ItemSep = 1, ItemCard = 2 };
    struct Item { int type; int row; int y, h; juce::String label; };

    static constexpr int cardH = 54, cardAllH = 22, sepH = 16, nowH = 30, gutterW = 26;

    juce::Rectangle<int> closeR()       const { return { getWidth() - 30, 6, 20, 20 }; }
    juce::Rectangle<int> scopeR (int i) const { return { getWidth() - 252 + i * 104, 7, 100, 19 }; }
    juce::Rectangle<int> chipsRowR()    const { return { 14, 28, getWidth() - 28, 20 }; }
    juce::Rectangle<int> graphR()       const { return { 14, 51, getWidth() - 28, 34 }; }
    juce::Rectangle<int> listR() const
    {
        const int top = all ? 30 : (showGraph() ? 88 : 51);
        return { 8, top, getWidth() - 16, getHeight() - top - 6 };
    }
    bool showGraph() const
    {
        if (all) return false;
        int mains = 0;
        for (auto& r : rows)
            if (r.stats && r.kind <= 2
                && (filter.isEmpty() || r.touched.contains (filter))) ++mains;
        return mains >= 2;
    }
    bool loadingVisible() const
    {
        if (all) return false;
        for (auto& r : rows) if (! r.stats) return true;
        return false;
    }
    float maxScroll() const { return juce::jmax (0.0f, (float) contentH - (float) listR().getHeight()); }

    juce::Colour kindColour (int kind) const
    {
        return kind == 0 ? theme::good : kind == 1 ? theme::accentB
             : kind == 3 ? theme::bad  : kind == 4 ? theme::warn : theme::textMute;
    }
    juce::Colour laneColour (const juce::String& name) const
    {
        const int i = chips.indexOf (name);
        return i >= 0 ? theme::trackColour (i) : theme::familyColour (name);
    }

    // day bucket for separators: unique per calendar day, labelled TODAY/YESTERDAY/JUL 2
    static int dayBucket (juce::int64 epoch)
    {
        if (epoch <= 0) return -1;
        return (int) ((epoch + (juce::int64) juce::Time (epoch * 1000)
                                   .getUTCOffsetSeconds()) / 86400);
    }
    static juce::String dayLabel (juce::int64 epoch)
    {
        const int b = dayBucket (epoch), today = dayBucket (juce::Time::currentTimeMillis() / 1000);
        if (b == today)     return "TODAY";
        if (b == today - 1) return "YESTERDAY";
        const juce::Time t (epoch * 1000);
        return t.getMonthName (true).toUpperCase() + " " + juce::String (t.getDayOfMonth());
    }

    juce::String cleanSubject (const Row& r) const
    {
        auto s = r.subject;
        for (auto* pre : { "accept proposal on ", "reject take on ", "revise take on " })
            if (s.startsWith (juce::String (pre) + song))
                s = s.fromFirstOccurrenceOf (":", false, false).trim();
        if (s == "(ui)" || s.isEmpty())
            s = r.kind == 0 ? "accepted from the canvas"
              : r.kind == 3 ? "a take that was let go"
              : r.kind == 4 ? "reshaped by feedback" : r.subject;
        return s;
    }

    void rebuildLayout()
    {
        items.clear();
        contentH = 4;
        auto push = [this] (int type, int row, int h, juce::String label = {})
        { items.push_back ({ type, row, contentH, h, std::move (label) }); contentH += h + 2; };
        if (! all && ! rows.empty()) push (ItemNow, -1, nowH);
        int lastDay = -2;
        for (int i = 0; i < (int) rows.size(); ++i)
        {
            const auto& r = rows[(size_t) i];
            if (! filter.isEmpty() && ! r.touched.contains (filter)) continue;
            const int day = dayBucket (r.epoch);
            if (day != lastDay && day >= 0)
            { push (ItemSep, -1, sepH, dayLabel (r.epoch)); lastDay = day; }
            push (ItemCard, i, all ? cardAllH : cardH);
        }
        contentH += 4;
        scrollY = juce::jlimit (0.0f, maxScroll(), scrollY);
    }

    bool nowSticky() const
    {
        if (all || items.empty() || items.front().type != ItemNow) return false;
        return scrollY > (float) items.front().y + 2.0f;
    }

    int itemAt (juce::Point<int> p) const
    {
        const auto lr = listR();
        if (! lr.contains (p)) return -1;
        if (nowSticky() && p.y < lr.getY() + nowH) return 0;   // the pinned NOW card
        const int y = p.y - lr.getY() + (int) scrollY;
        for (int i = 0; i < (int) items.size(); ++i)
            if (y >= items[(size_t) i].y && y < items[(size_t) i].y + items[(size_t) i].h)
                return i;
        return -1;
    }

    void scrollToSha (const juce::String& sha)
    {
        for (auto& it : items)
            if (it.type == ItemCard && rows[(size_t) it.row].sha == sha)
            {
                scrollY = juce::jlimit (0.0f, maxScroll(),
                                        (float) it.y - (float) listR().getHeight() * 0.35f);
                return;
            }
    }

    // ------------------------------------------------------------ life graph
    struct GDot { int rowIdx; float x, y; bool take; };

    std::vector<GDot> graphDots() const
    {
        std::vector<GDot> out;
        const auto gr = graphR().toFloat().reduced (10.0f, 5.0f);
        const float base = gr.getBottom() - 4.0f;
        std::vector<int> mains;                              // oldest -> newest
        int maxMass = 1, minMass = INT_MAX;
        for (int i = (int) rows.size() - 1; i >= 0; --i)
        {
            const auto& r = rows[(size_t) i];
            if (! r.stats) continue;
            if (! filter.isEmpty() && ! r.touched.contains (filter)) continue;
            if (r.kind <= 2)
            {
                mains.push_back (i);
                maxMass = juce::jmax (maxMass, r.mass);
                minMass = juce::jmin (minMass, r.mass);
            }
        }
        if (mains.empty()) return out;
        // min-max normalize: real songs hold near-constant mass - absolute scale
        // would flatline; the SHAPE of the work is the story
        const float lo = (float) minMass * 0.92f;
        const float span = juce::jmax (1.0f, (float) maxMass - lo);
        auto xOf = [&] (int k)
        { return mains.size() < 2 ? gr.getCentreX()
                                  : gr.getX() + gr.getWidth() * (float) k / (float) (mains.size() - 1); };
        for (int k = 0; k < (int) mains.size(); ++k)
        {
            const auto& r = rows[(size_t) mains[(size_t) k]];
            out.push_back ({ mains[(size_t) k], xOf (k),
                             base - (gr.getHeight() - 12.0f)
                                      * juce::jlimit (0.0f, 1.0f, ((float) r.mass - lo) / span),
                             false });
        }
        for (int i = 0; i < (int) rows.size(); ++i)          // takes hang under the axis
        {
            const auto& r = rows[(size_t) i];
            if (! r.stats || r.kind < 3) continue;
            if (! filter.isEmpty() && ! r.touched.contains (filter)) continue;
            float x = gr.getRight();
            for (int k = 0; k < (int) mains.size(); ++k)     // between its bracketing commits
                if (rows[(size_t) mains[(size_t) k]].epoch <= r.epoch)
                    x = xOf (k) + (k + 1 < (int) mains.size() ? (xOf (k + 1) - xOf (k)) * 0.5f : 6.0f);
            out.push_back ({ i, juce::jmin (x, gr.getRight()), base + 5.0f, true });
        }
        return out;
    }

    static int nearestDot (const std::vector<GDot>& dots, juce::Point<float> p)
    {
        int best = -1; float bd = 81.0f;                     // within 9px
        for (int i = 0; i < (int) dots.size(); ++i)
        {
            const float d = p.getDistanceSquaredFrom ({ dots[(size_t) i].x, dots[(size_t) i].y });
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    void paintGraph (juce::Graphics& g)
    {
        const auto gr = graphR().toFloat();
        g.setColour (theme::inset.withAlpha (0.75f));
        g.fillRoundedRectangle (gr, 5.0f);
        const float axisY = gr.reduced (10.0f, 5.0f).getBottom() - 4.0f;
        g.setColour (theme::textMute.withAlpha (0.14f));     // the axis takes hang from
        g.drawHorizontalLine ((int) axisY, gr.getX() + 6.0f, gr.getRight() - 6.0f);
        const auto dots = graphDots();
        std::vector<GDot> mains;
        for (auto& d : dots) if (! d.take) mains.push_back (d);
        if (mains.size() >= 2)
        {
            const float base = gr.reduced (10.0f, 5.0f).getBottom() - 4.0f;
            juce::Path area, lineP;
            area.startNewSubPath (mains.front().x, base);
            lineP.startNewSubPath (mains.front().x, mains.front().y);
            for (auto& d : mains) { area.lineTo (d.x, d.y); lineP.lineTo (d.x, d.y); }
            area.lineTo (mains.back().x, base);
            area.closeSubPath();
            g.setGradientFill ({ theme::accent.withAlpha (0.20f), { gr.getX(), gr.getY() },
                                 theme::accent.withAlpha (0.02f), { gr.getX(), gr.getBottom() }, false });
            g.fillPath (area);
            g.setColour (theme::accent.withAlpha (0.50f));
            g.strokePath (lineP, juce::PathStrokeType (1.2f));
            for (size_t k = 1; k < mains.size(); ++k)        // day boundaries breathe as ticks
                if (dayBucket (rows[(size_t) mains[k].rowIdx].epoch)
                    != dayBucket (rows[(size_t) mains[k - 1].rowIdx].epoch))
                {
                    const float mx = (mains[k].x + mains[k - 1].x) * 0.5f;
                    g.setColour (theme::textMute.withAlpha (0.18f));
                    g.drawVerticalLine ((int) mx, gr.getY() + 3.0f, gr.getBottom() - 3.0f);
                }
        }
        for (int i = 0; i < (int) dots.size(); ++i)
        {
            const auto& d = dots[(size_t) i];
            const auto& row = rows[(size_t) d.rowIdx];
            const auto c = kindColour (row.kind);
            const bool active = row.sha == activeSha && activeSha.isNotEmpty();
            const bool hot = i == hoverDot;
            if (d.take)                                       // roads not taken: diamonds below
            {
                juce::Path dia;
                const float s = hot ? 3.4f : 2.6f;
                dia.addQuadrilateral (d.x, d.y - s, d.x + s, d.y, d.x, d.y + s, d.x - s, d.y);
                g.setColour (c.withAlpha (hot ? 0.95f : 0.65f));
                g.fillPath (dia);
            }
            else
            {
                if (active)
                {
                    const float breathe = 4.5f + std::sin (phase * 0.18f) * 1.5f;
                    g.setColour (theme::good.withAlpha (0.30f));
                    g.drawEllipse (d.x - breathe, d.y - breathe, breathe * 2, breathe * 2, 1.4f);
                }
                g.setColour (c.withAlpha (hot || active ? 1.0f : 0.80f));
                g.fillEllipse (d.x - 2.6f, d.y - 2.6f, 5.2f, 5.2f);
                if (hot)
                { g.setColour (juce::Colours::white.withAlpha (0.85f));
                  g.drawEllipse (d.x - 4.2f, d.y - 4.2f, 8.4f, 8.4f, 1.0f); }
            }
        }
    }

    // ---------------------------------------------------------------- header
    void paintHeader (juce::Graphics& g)
    {
        auto head = getLocalBounds().reduced (14, 0).removeFromTop (26).withTrimmedTop (6);
        g.setColour (theme::text);
        g.setFont (theme::caps (12.5f));
        g.drawText ("TIME MACHINE", head.removeFromLeft (118), juce::Justification::centredLeft);
        g.setColour (theme::textDim);
        g.setFont (theme::ui (11.0f));
        g.drawText (all ? censusLine
                        : song + (filter.isEmpty() ? " - every take since day one"
                                                   : " - takes that touched '" + filter + "'"),
                    head.withTrimmedRight (250), juce::Justification::centredLeft);
        g.setColour (theme::textMute);
        g.setFont (theme::ui (12.0f));
        g.drawText ("x", closeR(), juce::Justification::centred);
        segAt (g, scopeR (0), "THIS SONG", ! all, theme::accent);
        segAt (g, scopeR (1), "ALL SONGS", all, theme::accentB);
    }

    void paintChips (juce::Graphics& g)
    {
        // counts ride the chips: how many takes touched that lane
        std::map<juce::String, int> counts;
        for (auto& r : rows)
            if (r.stats) for (auto& t : r.touched) counts[t]++;
        segAt (g, chipR (0), "ALL LANES", filter.isEmpty(), theme::accent);
        const int fit = visibleChips();
        for (int i = 0; i < fit; ++i)
        {
            const auto n = counts.count (chips[i]) ? counts[chips[i]] : 0;
            theme::chip (g, chipR (i + 1).toFloat(), laneColour (chips[i]),
                         chips[i].substring (0, 9) + (n > 0 ? " " + juce::String (n) : juce::String()),
                         theme::caps (8.5f),
                         filter == chips[i] ? 0.30f : 0.10f,
                         filter == chips[i] ? 0.95f : 0.35f);
        }
        const int lim = juce::jmin (chips.size(), 12);
        if (fit < lim)   // the tail SPEAKS: lanes that didn't fit are counted, not cut mid-chip
            theme::chip (g, chipR (fit + 1).withWidth (36).toFloat(), theme::textMute,
                         "+" + juce::String (lim - fit), theme::caps (8.5f), 0.10f, 0.45f);
    }
    int visibleChips() const          // whole chips only — the row never clips mid-body
    {
        const int lim = juce::jmin (chips.size(), 12);
        const int edge = chipsRowR().getRight();
        int fit = lim;
        for (int i = 0; i < lim; ++i)
            if (chipR (i + 1).getRight() > edge) { fit = i; break; }
        if (fit < lim)                                  // reserve room for the +N tail
            while (fit > 0 && chipR (fit).getRight() > edge - 42) --fit;
        return fit;
    }

    juce::Rectangle<int> chipR (int i) const
    {
        const auto strip = chipsRowR();
        int x = strip.getX();
        for (int k = 0; k < i; ++k) x += chipW (k) + 6;
        return { x, strip.getY(), chipW (i), 18 };
    }
    int chipW (int i) const
    {
        if (i == 0) return 74;
        const auto& n = chips[i - 1];
        return juce::jlimit (44, 108, 26 + (int) theme::measure (theme::caps (8.5f),
                                                                 n.substring (0, 9) + " 00"));
    }

    void segAt (juce::Graphics& g, juce::Rectangle<int> r, const juce::String& t,
                bool on, juce::Colour c)
    {
        g.setColour (on ? c.withAlpha (0.18f) : theme::inset);
        g.fillRoundedRectangle (r.toFloat(), 6.0f);
        g.setColour (on ? c : theme::line);
        g.drawRoundedRectangle (r.toFloat().reduced (0.5f), 6.0f, 1.0f);
        g.setColour (on ? theme::text : theme::textDim);
        g.setFont (theme::caps (8.5f));
        g.drawText (t, r, juce::Justification::centred);
    }

    // ------------------------------------------------------------------ list
    void paintList (juce::Graphics& g)
    {
        const auto lr = listR();
        if (rows.empty()) { paintEmpty (g, lr); return; }
        bool any = false;
        for (auto& it : items) if (it.type == ItemCard) { any = true; break; }
        if (! any && ! filter.isEmpty())
        {
            g.setColour (theme::textMute);
            g.setFont (theme::ui (11.0f));
            g.drawText ("no take touched '" + filter + "' - it has been stable",
                        lr, juce::Justification::centred);
            return;
        }
        g.saveState();
        g.reduceClipRegion (lr);
        const int y0 = lr.getY() - (int) scrollY;

        // THE SPINE: one line of time behind everything
        const float spineX = (float) (lr.getX() + gutterW / 2);
        g.setGradientFill ({ theme::accent.withAlpha (0.35f), { spineX, (float) lr.getY() },
                             theme::accentB.withAlpha (0.10f), { spineX, (float) lr.getBottom() }, false });
        g.fillRect (spineX - 0.5f, (float) lr.getY(), 1.0f, (float) lr.getHeight());

        for (auto& it : items)
        {
            const juce::Rectangle<int> ir { lr.getX(), y0 + it.y, lr.getWidth(), it.h };
            if (ir.getBottom() < lr.getY() || ir.getY() > lr.getBottom()) continue;
            if (it.type == ItemNow)       { if (! nowSticky()) paintNow (g, ir, spineX); }
            else if (it.type == ItemSep)  paintSep  (g, ir, it.label, spineX);
            else                          paintCard (g, ir, it, spineX);
        }
        if (nowSticky())                 // RETURN must never scroll out of reach
        {
            const juce::Rectangle<int> pin { lr.getX(), lr.getY(), lr.getWidth(), nowH };
            g.setGradientFill ({ juce::Colours::black.withAlpha (0.35f),
                                 { 0.0f, (float) pin.getBottom() },
                                 juce::Colours::transparentBlack,
                                 { 0.0f, (float) pin.getBottom() + 10.0f }, false });
            g.fillRect (pin.withHeight (pin.getHeight() + 10));
            paintNow (g, pin, spineX);
        }
        g.restoreState();

        if (contentH > lr.getHeight())                       // scroll spoor, not a scrollbar
        {
            const float frac = (float) lr.getHeight() / (float) contentH;
            const float top = scrollY / (float) contentH * (float) lr.getHeight();
            g.setColour (theme::textMute.withAlpha (0.35f));
            g.fillRoundedRectangle ((float) lr.getRight() - 3.0f, (float) lr.getY() + top,
                                    2.0f, juce::jmax (14.0f, frac * (float) lr.getHeight()), 1.0f);
        }
    }

    void paintEmpty (juce::Graphics& g, juce::Rectangle<int> lr)
    {
        const float sx = (float) (lr.getX() + gutterW / 2);  // a ghost spine, waiting
        g.setGradientFill ({ theme::accent.withAlpha (0.20f), { sx, (float) lr.getY() },
                             theme::accentB.withAlpha (0.03f), { sx, (float) lr.getBottom() }, false });
        g.fillRect (sx - 0.5f, (float) lr.getY() + 6.0f, 1.0f, (float) lr.getHeight() - 12.0f);
        for (int i = 0; i < 3; ++i)
        {
            g.setColour (theme::textMute.withAlpha (0.30f - 0.08f * (float) i));
            g.drawEllipse (sx - 3.0f, (float) lr.getY() + 16.0f + 30.0f * (float) i, 6.0f, 6.0f, 1.0f);
        }
        g.setColour (theme::textMute);
        g.setFont (theme::ui (11.0f));
        g.drawText ("no committed history yet - accepts land here automatically",
                    lr, juce::Justification::centred);
    }

    void paintNow (juce::Graphics& g, juce::Rectangle<int> ir, float spineX)
    {
        const bool previewing = activeSha.isNotEmpty();
        auto body = ir.withTrimmedLeft (gutterW).reduced (0, 1).toFloat();
        const auto tint = previewing ? theme::accent : theme::good;
        g.setColour (theme::panelHi.interpolatedWith (tint, previewing ? 0.10f : 0.05f));
        g.fillRoundedRectangle (body, 6.0f);
        g.setColour (tint.withAlpha (previewing ? 0.55f : 0.25f));
        g.drawRoundedRectangle (body.reduced (0.5f), 6.0f, 1.0f);

        const float cy = body.getCentreY();                  // the brightest node on the spine
        g.setColour (tint.withAlpha (0.25f));
        g.fillEllipse (spineX - 6.5f, cy - 6.5f, 13.0f, 13.0f);
        g.setColour (tint);
        g.fillEllipse (spineX - 3.5f, cy - 3.5f, 7.0f, 7.0f);

        auto tr = body.toNearestInt().reduced (10, 0);
        g.setColour (previewing ? theme::accent : theme::good);
        g.setFont (theme::caps (10.5f));
        g.drawText ("NOW", tr.removeFromLeft (40), juce::Justification::centredLeft);
        g.setColour (theme::textDim);
        g.setFont (theme::ui (10.5f));
        g.drawText (previewing ? "the working state - click to come back"
                               : "the working state - " + song,
                    tr, juce::Justification::centredLeft);
        if (previewing)                                      // the material RETURN affordance
        {
            auto cr = body.removeFromRight (34.0f).withSizeKeepingCentre (22.0f, 22.0f);
            const float breathe = 0.55f + 0.25f * std::sin (phase * 0.18f);
            g.setColour (theme::accent.withAlpha (breathe * 0.35f));
            g.fillEllipse (cr.expanded (3.0f));
            g.setColour (theme::accent.withAlpha (0.85f));
            g.drawEllipse (cr, 1.2f);
            juce::Path arrow;                                // <- back to now
            arrow.addArrow ({ cr.getRight() - 6.0f, cr.getCentreY(),
                              cr.getX() + 6.0f, cr.getCentreY() }, 1.6f, 6.0f, 5.0f);
            g.fillPath (arrow);
        }
    }

    void paintSep (juce::Graphics& g, juce::Rectangle<int> ir, const juce::String& label, float spineX)
    {
        g.setColour (theme::textMute.withAlpha (0.85f));
        g.setFont (theme::caps (8.0f));
        const int w = 12 + (int) theme::measure (theme::caps (8.0f), label);
        auto tr = ir.withTrimmedLeft (gutterW).withWidth (w);
        g.drawText (label, tr, juce::Justification::centredLeft);
        g.setColour (theme::line.withAlpha (0.65f));
        g.drawHorizontalLine (ir.getCentreY(), (float) tr.getRight() + 4.0f, (float) ir.getRight() - 6.0f);
        g.drawHorizontalLine (ir.getCentreY(), spineX - 4.0f, spineX + 4.0f);
    }

    void paintCard (juce::Graphics& g, juce::Rectangle<int> ir, const Item& it, float spineX)
    {
        const auto& row = rows[(size_t) it.row];
        const bool take = row.kind >= 3;
        const bool active = activeSha.isNotEmpty() && row.sha == activeSha;
        const bool hot = &it - items.data() == hoverItem;
        const auto kc = kindColour (row.kind);
        auto body = ir.withTrimmedLeft (gutterW).reduced (0, 1).toFloat();

        // node on the spine; takes are OFFSHOOTS with a stub (roads not taken)
        const float cy = body.getCentreY();
        if (take)
        {
            const float nx = spineX + 8.0f;
            g.setColour (kc.withAlpha (0.40f));
            g.drawLine (spineX, cy, nx - 3.0f, cy, 1.0f);
            juce::Path dia;
            dia.addQuadrilateral (nx, cy - 3.4f, nx + 3.4f, cy, nx, cy + 3.4f, nx - 3.4f, cy);
            g.setColour (kc.withAlpha (hot || active ? 1.0f : 0.75f));
            g.fillPath (dia);
        }
        else
        {
            g.setColour (kc.withAlpha (hot || active ? 1.0f : 0.85f));
            g.fillEllipse (spineX - 3.0f, cy - 3.0f, 6.0f, 6.0f);
            if (row.kind == 0)
            { g.setColour (kc.withAlpha (0.25f)); g.drawEllipse (spineX - 5.5f, cy - 5.5f, 11.0f, 11.0f, 1.0f); }
        }

        // card body: glass when idle, HEARING green when it is on the transport
        auto fill = hot ? theme::panelHi : theme::panel.brighter (0.02f);
        if (active) fill = fill.interpolatedWith (theme::good, 0.09f);
        if (take)   fill = fill.interpolatedWith (kc, 0.035f);
        g.setColour (fill);
        g.fillRoundedRectangle (body, 6.0f);
        g.setColour (active ? theme::good.withAlpha (0.33f)
                            : take ? kc.withAlpha (hot ? 0.45f : 0.22f)
                                   : theme::line.withAlpha (hot ? 1.0f : 0.55f));
        g.drawRoundedRectangle (body.reduced (0.5f), 6.0f, 1.0f);

        auto in = body.toNearestInt().reduced (9, 3);
        auto meta = in.removeFromLeft (78);                  // the quiet column
        if (all)                                             // compact census rows
        {
            g.setColour (theme::textDim);
            g.setFont (theme::ui (10.0f));
            g.drawText (row.age.replace (" ago", ""), meta, juce::Justification::centredLeft);
            auto line = in;
            if (row.song.isNotEmpty())
            {
                const int w = juce::jmin (110, 24 + (int) theme::measure (theme::caps (8.5f), row.song));
                theme::chip (g, line.removeFromLeft (w).reduced (0, 3).toFloat(),
                             theme::accent, row.song, theme::caps (8.5f), 0.12f, 0.40f);
                line.removeFromLeft (6);
            }
            g.setColour (row.kind == 0 ? theme::text : theme::textDim);
            g.setFont (theme::ui (10.5f));
            g.drawText (row.subject, line, juce::Justification::centredLeft);
            return;
        }
        g.setColour (active ? theme::good : theme::textDim); // age over sha
        g.setFont (theme::ui (10.0f));
        g.drawText (row.age.replace (" ago", ""), meta.removeFromTop (in.getHeight() / 2),
                    juce::Justification::topLeft);
        g.setColour (theme::textMute);
        g.setFont (theme::mono (8.5f));
        g.drawText (row.sha, meta, juce::Justification::bottomLeft);

        auto top = in.removeFromTop (16);
        paintDiffBars (g, top.removeFromRight (176), row);
        g.setColour (row.kind == 0 ? theme::text : theme::textDim);
        g.setFont (theme::ui (11.0f));
        g.drawText (cleanSubject (row), top, juce::Justification::centredLeft);

        auto stripArea = in.reduced (0, 2);
        paintStrip (g, stripArea, row, active, hot);
    }

    void paintDiffBars (juce::Graphics& g, juce::Rectangle<int> r, const Row& row)
    {
        if (! row.stats || (row.added == 0 && row.removed == 0)) return;
        auto bars = r.toFloat();
        const float midY = bars.getCentreY();
        auto barW = [] (int n) { return juce::jmin (38.0f, std::sqrt ((float) n) * 1.5f + 2.0f); };
        float x = bars.getRight();
        if (row.removed > 0)                                 // red pulls left from the edge
        {
            const float w = barW (row.removed);
            g.setColour (theme::bad.withAlpha (0.80f));
            g.fillRoundedRectangle (x - w, midY + 1.0f, w, 3.0f, 1.5f);
            x -= w + 4.0f;
        }
        if (row.added > 0)
        {
            const float w = barW (row.added);
            g.setColour (theme::good.withAlpha (0.90f));
            g.fillRoundedRectangle (x - w, midY - 4.0f, w, 3.0f, 1.5f);
            x -= w + 4.0f;
        }
        g.setFont (theme::ui (9.5f));
        juce::String t;
        if (row.added > 0)   t << "+" << juce::String (row.added);
        if (row.removed > 0) t << (t.isEmpty() ? "-" : " -") << juce::String (row.removed);
        g.setColour (theme::textDim);
        g.drawText (t, juce::Rectangle<int> (r.getX(), r.getY(), (int) x - r.getX() - 2, r.getHeight()),
                    juce::Justification::centredRight);
    }

    // ------------------------------------------------------------- filmstrip
    void paintStrip (juce::Graphics& g, juce::Rectangle<int> r, const Row& row,
                     bool active, bool hot)
    {
        g.setColour (theme::inset);
        g.fillRoundedRectangle (r.toFloat(), 4.0f);
        if (! row.stats)                                     // still reading the tape: shimmer
        {
            const float w = 140.0f;
            const float x = std::fmod (phase * 5.0f, (float) r.getWidth() + w * 2.0f) - w;
            g.saveState();
            g.reduceClipRegion (r.reduced (1));
            juce::ColourGradient sweep (juce::Colours::transparentWhite,
                                        (float) r.getX() + x - w, (float) r.getCentreY(),
                                        juce::Colours::transparentWhite,
                                        (float) r.getX() + x + w, (float) r.getCentreY(), false);
            sweep.addColour (0.5, theme::accent.withAlpha (0.10f));
            g.setGradientFill (sweep);
            g.fillRect (r.reduced (1));
            g.restoreState();
            return;
        }
        if (row.strips.empty()) return;
        const auto inner = r.reduced (3, 2);
        if (inner.getWidth() < 24 || inner.getHeight() < 4) return;
        g.drawImage (stripImage (row, inner.getWidth(), inner.getHeight()),
                     inner.toFloat());

        if (active)                                          // the take that is SOUNDING
        {
            auto er = inner.toFloat().removeFromRight (26.0f).withSizeKeepingCentre (16.0f, 14.0f);
            g.setColour (theme::inset.withAlpha (0.70f));
            g.fillRoundedRectangle (er.expanded (4.0f), 4.0f);
            for (int i = 0; i < 3; ++i)
            {
                const float h = 3.5f + 5.0f * std::abs (std::sin (phase * 0.23f + (float) i * 1.15f));
                g.setColour (theme::good.withAlpha (0.90f));
                g.fillRoundedRectangle (er.getX() + (float) i * 6.0f, er.getBottom() - h, 3.6f, h, 1.2f);
            }
        }
        else if (hot)                                        // the material invitation: play
        {
            auto pr = inner.toFloat().removeFromRight (30.0f).withSizeKeepingCentre (18.0f, 18.0f);
            g.setColour (theme::inset.withAlpha (0.80f));
            g.fillEllipse (pr.expanded (2.0f));
            g.setColour (theme::good.withAlpha (0.95f));
            g.drawEllipse (pr, 1.1f);
            juce::Path tri;
            tri.addTriangle (pr.getX() + 6.5f, pr.getY() + 4.5f,
                             pr.getX() + 6.5f, pr.getBottom() - 4.5f,
                             pr.getRight() - 4.5f, pr.getCentreY());
            g.fillPath (tri);
        }
    }

    juce::Image stripImage (const Row& row, int w, int h)
    {
        const auto key = row.sha + row.path + juce::String (w) + "x" + juce::String (h);
        auto found = stripCache.find (key);
        if (found != stripCache.end()) return found->second;

        juce::Image img (juce::Image::ARGB, juce::jmax (8, w), juce::jmax (4, h), true);
        juce::Graphics g (img);
        const int nb = juce::jmax (1, (int) row.strips.size());
        const float bandH = (float) h / (float) nb;
        for (int bi = 0; bi < (int) row.strips.size(); ++bi)
        {
            const auto& s = row.strips[(size_t) bi];
            const float y0 = bandH * (float) bi;
            const auto base = laneColour (s.name);
            const float gap = bandH >= 3.0f ? 1.0f : 0.0f;   // lanes read as LANES
            g.setColour (base.withAlpha (0.05f));            // faint wash names the lane
            g.fillRect (0.0f, y0, (float) w, juce::jmax (1.0f, bandH - gap));
            const int gr = s.grid.size();                    // kept material: TRUE density
            for (int ri = 0; ri < gr; ++ri)
            {
                const auto& gs = s.grid[ri];
                const float rh = juce::jmax (1.0f, (bandH - gap - 0.4f) / (float) gr);
                const float ry = y0 + rh * (float) ri;
                const float cw = (float) w / (float) juce::jmax (1, gs.length());
                for (int ci = 0; ci < gs.length(); ++ci)
                {
                    const auto ch = gs[ci];
                    const int v = ch >= '0' && ch <= '9' ? ch - '0'
                                : ch >= 'a' && ch <= 'f' ? 10 + ch - 'a' : 0;
                    if (v <= 0) continue;
                    g.setColour (base.withAlpha (0.08f
                                    + 0.55f * std::pow ((float) v / 15.0f, 1.1f)));
                    g.fillRect (cw * (float) ci, ry, juce::jmax (1.0f, cw), rh);
                }
            }
            int lo = 127, hi = 0;                            // pitch range for diff dots
            for (auto* src : { &s.added, &s.removed })
                for (auto& p : *src) { lo = juce::jmin (lo, p.p); hi = juce::jmax (hi, p.p); }
            const float bscale = (float) w / juce::jmax (1.0f, row.beats);
            const float dotH = juce::jlimit (1.4f, 3.0f, bandH * 0.45f);
            auto plot = [&] (const std::vector<Pt>& pts, juce::Colour c, float alpha)
            {
                for (auto& p : pts)
                {
                    const float t = hi > lo ? (float) (p.p - lo) / (float) (hi - lo) : 0.5f;
                    const float py = y0 + 0.6f + (1.0f - t) * juce::jmax (0.0f, bandH - dotH - 1.2f);
                    g.setColour (c.withAlpha (alpha));
                    g.fillRect (p.b * bscale, py, juce::jmax (1.3f, p.l * bscale), dotH);
                }
            };
            plot (s.removed, theme::bad, 0.85f);             // what this take erased
            plot (s.added, theme::good, 0.95f);              // what it brought
            if (s.propChange)                                // knobs moved: amber tick
            {
                g.setColour (theme::warn.withAlpha (0.85f));
                g.fillRect (0.0f, y0 + 1.0f, 2.0f, juce::jmax (1.0f, bandH - 2.0f));
            }
        }
        stripCache[key] = std::move (img);
        return stripCache[key];
    }

    std::vector<Row> rows;
    std::vector<Item> items;
    std::map<juce::String, juce::Image> stripCache;
    juce::StringArray chips;
    juce::String song, censusLine, filter, activeSha;
    bool all = false;
    int contentH = 0, hoverItem = -1, hoverDot = -1;
    float scrollY = 0, phase = 0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (HistoryPanel)
};
