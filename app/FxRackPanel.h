// FxRackPanel.h — THE DEVICE RACK: one strip's fx chain as touchable hardware.
// A bottom drawer (Live's device view crossed with FL's mixer inserts) targeting any
// track, any bus, or THE MASTER. Each module: per-param mini knobs that edit the LIVE
// engine parameter AND persist to song.json in the same gesture, a power dot = live
// bypass A/B (persists as fx "bypass": true), ✕ removes, ◀▶ reorders, + adds faust fx /
// eq / comp / vst3 inserts. Ctrl+click a module = the agent's context points at THIS fx.
// The MASTER target grows THE VERDICT: a master_report scorecard (KG MixTarget lane)
// with a CHECK button and one-click "ask the agent to fix what failed".
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include "SongLoader.h"
#include "UiTheme.h"

class FxRackPanel : public juce::Component, private juce::Timer
{
public:
    enum class Kind { track, bus, master };

    sotadaw::Song* song = nullptr;
    std::function<void()> onStructure;                     // chain shape changed -> snapshot+save+rebuild
    std::function<void()> onParamEdited;                   // knob turned (live-applied) -> scheduleSave
    std::function<te::Plugin* (int)> resolvePlugin;        // fx index of current target -> live plugin
    std::function<void (int)> onOpenFace;                  // open the module's full face
    std::function<void()> onCloseRack;
    std::function<void()> onRunCheck;                      // master: run tools/master_report.py async
    std::function<void()> onRunAuto;                       // master: run tools/auto_master.py async
    std::function<void (const juce::String&)> onAskAgent;  // failing verdict -> composed prompt
    std::function<void()> onPointedChange;                 // pointed module = agent context changed
    std::function<juce::StringArray()> listFaustFx;        // fx_* dsp names for the add menu
    std::function<juce::StringArray()> listVstFx;          // scanned vst3 effect names

    FxRackPanel()
    {
        viewport.setViewedComponent (&strip, false);
        viewport.setScrollBarsShown (false, true, false, true);
        viewport.setScrollBarThickness (8);
        addAndMakeVisible (viewport);
        startTimerHz (8);                                  // knobs follow agent/automation edits
    }

    // ---------------------------------------------------------------- target
    Kind kind = Kind::track;
    int targetIndex = 0;                                   // track or bus index
    int lastTrackIndex = 0;                                // the track chip remembers its home

    void setTarget (Kind k, int index)
    {
        kind = k;
        targetIndex = juce::jmax (0, index);
        if (k == Kind::track) lastTrackIndex = targetIndex;
        if (pointedFx >= 0) { pointedFx = -1; if (onPointedChange) onPointedChange(); }
        refreshTarget();
    }

    std::vector<sotadaw::SongFx>* chain() const
    {
        if (song == nullptr) return nullptr;
        if (kind == Kind::master) return &song->master;
        if (kind == Kind::bus)
            return targetIndex < (int) song->buses.size() ? &song->buses[(size_t) targetIndex].fx : nullptr;
        return targetIndex < (int) song->tracks.size() ? &song->tracks[(size_t) targetIndex].fx : nullptr;
    }

    juce::String targetName() const
    {
        if (song == nullptr) return {};
        if (kind == Kind::master) return "MASTER";
        if (kind == Kind::bus)
            return targetIndex < (int) song->buses.size() ? "bus:" + song->buses[(size_t) targetIndex].id
                                                          : juce::String ("bus:?");
        return targetIndex < (int) song->tracks.size() ? song->tracks[(size_t) targetIndex].name
                                                       : juce::String ("?");
    }

    juce::Colour targetColour() const
    {
        if (kind == Kind::master) return theme::accent.interpolatedWith (theme::text, 0.55f);
        if (kind == Kind::bus)    return theme::accentB;
        return theme::trackColour (targetIndex);
    }

    // rebuild modules from the song chain + live engine (call after ANY engine rebuild:
    // old AutomatableParameter pointers die with the edit)
    void refreshTarget()
    {
        modules.clear();
        auto* ch = chain();
        if (ch != nullptr)
            for (int i = 0; i < (int) ch->size(); ++i)
            {
                auto* m = modules.add (new Module (*this, i));
                strip.addAndMakeVisible (m);
            }
        if (pointedFx >= (int) modules.size()) { pointedFx = -1; if (onPointedChange) onPointedChange(); }
        resized();
        repaint();
    }

    // ---------------------------------------------------------------- verdict state
    juce::var report;                                      // last master_report JSON (void = none yet)
    bool checking = false;
    bool mastering = false;                                // auto-master convergence in flight
    void setReport (const juce::var& r)  { report = r; checking = false; repaint(); }
    void setChecking (bool on)           { checking = on; repaint(); }
    void setMastering (bool on)          { mastering = on; repaint(); }

    // ---------------------------------------------------------------- pointed fx = agent context
    int pointedFx = -1;
    juce::String pointedSelectionJson() const
    {
        if (pointedFx < 0 || song == nullptr) return {};
        const auto scope = kind == Kind::master ? "master" : kind == Kind::bus ? "bus" : "track";
        const auto owner = kind == Kind::master ? juce::String ("master")
                         : kind == Kind::bus ? (targetIndex < (int) song->buses.size()
                                                    ? song->buses[(size_t) targetIndex].id : juce::String())
                         : (targetIndex < (int) song->tracks.size()
                                ? song->tracks[(size_t) targetIndex].name : juce::String());
        return "{\"type\": \"fx\", \"scope\": \"" + juce::String (scope) + "\", \"owner\": "
               + juce::JSON::toString (juce::var (owner))
               + ", \"index\": " + juce::String (pointedFx) + "}";
    }
    juce::String pointedLabel() const
    {
        auto* ch = chain();
        if (ch == nullptr || pointedFx < 0 || pointedFx >= (int) ch->size()) return {};
        auto& f = (*ch)[(size_t) pointedFx];
        return (f.id.isNotEmpty() ? f.id : f.type) + " @ " + targetName();
    }

    // ---------------------------------------------------------------- geometry
    static constexpr int headerH = 26, cardW = 268;

    void resized() override
    {
        auto r = getLocalBounds().withTrimmedTop (headerH).reduced (8, 4);
        if (kind == Kind::master)
            r.removeFromRight (cardW + 6);                 // the verdict card
        viewport.setBounds (r);
        int x = 2;
        const int mh = juce::jmax (60, r.getHeight() - 10);
        for (auto* m : modules)
        {
            m->setBounds (x, 2, m->preferredWidth(), mh);
            x += m->preferredWidth() + 8;
        }
        strip.setSize (juce::jmax (x + 2, r.getWidth()), juce::jmax (1, r.getHeight() - 8));
    }

    // ---------------------------------------------------------------- painting
    void paint (juce::Graphics& g) override
    {
        auto full = getLocalBounds();
        theme::backdrop (g, full);
        const auto col = targetColour();
        g.setGradientFill ({ col.withAlpha (0.10f), full.toFloat().getTopLeft(),
                             col.withAlpha (0.0f), { full.toFloat().getX() + 420.0f, (float) full.getY() }, false });
        g.fillRect (full.withHeight (headerH));
        g.setColour (theme::line);
        g.drawHorizontalLine (headerH - 1, 0.0f, (float) getWidth());

        hits.clear();
        auto h = full.withHeight (headerH).reduced (10, 3);
        g.setColour (col.withAlpha (0.95f));
        g.fillRoundedRectangle (2.0f, 4.0f, 3.5f, (float) headerH - 8.0f, 1.75f);
        g.setColour (theme::textMute);
        g.setFont (theme::caps (9.0f));
        g.drawText ("RACK", h.removeFromLeft (38), juce::Justification::centredLeft);

        auto chipf = theme::ui (10.0f, juce::Font::bold);
        auto addChip = [&] (const juce::String& label, juce::Colour c, bool on,
                            const juce::String& act, int arg)
        {
            const float w = theme::measure (chipf, label) + 20.0f;
            if (h.getWidth() < (int) w + 4) return;
            auto r = h.removeFromLeft ((int) w).toFloat().reduced (0.0f, 1.0f);
            const bool hov = r.contains (lastMouse);       // the hand is answered
            theme::chip (g, r, c, label, chipf,
                         on ? 0.30f : hov ? 0.19f : 0.10f,
                         on ? 0.95f : hov ? 0.70f : 0.4f, on);
            hits.push_back ({ r, act, arg });
            h.removeFromLeft (5);
        };

        // targets: the home track | every bus | MASTER
        if (song != nullptr)
        {
            const int ti = kind == Kind::track ? targetIndex : lastTrackIndex;
            if (ti < (int) song->tracks.size())
                addChip (song->tracks[(size_t) ti].name, theme::trackColour (ti),
                         kind == Kind::track, "track", ti);
            for (int b = 0; b < (int) song->buses.size(); ++b)
                addChip ("bus:" + song->buses[(size_t) b].id, theme::accentB,
                         kind == Kind::bus && targetIndex == b, "bus", b);
            addChip ("MASTER", theme::accent.interpolatedWith (theme::text, 0.55f),
                     kind == Kind::master, "master", 0);
        }
        h.removeFromLeft (8);
        addChip ("+ FX", theme::good, false, "add", 0);

        // right side: close, then (master) check state
        {
            auto rr = full.withHeight (headerH).reduced (8, 3);
            auto xr = rr.removeFromRight (20).toFloat().reduced (1.0f);
            g.setColour (theme::textDim);
            const auto c = xr.reduced (5.0f);
            g.drawLine (c.getX(), c.getY(), c.getRight(), c.getBottom(), 1.4f);
            g.drawLine (c.getX(), c.getBottom(), c.getRight(), c.getY(), 1.4f);
            hits.push_back ({ xr, "close", 0 });
        }

        if (chain() != nullptr && chain()->empty())
        {
            g.setColour (theme::textDim);
            g.setFont (theme::ui (11.0f));
            g.drawText ("empty chain - hit + FX (order = signal flow)",
                        viewport.getBounds(), juce::Justification::centred);
        }
        if (kind == Kind::master)
            paintVerdict (g, { getWidth() - cardW - 8, headerH + 4, cardW, getHeight() - headerH - 10 });
    }

    void paintVerdict (juce::Graphics& g, juce::Rectangle<int> r)
    {
        theme::card (g, r.toFloat(), theme::panel, 9.0f);
        auto a = r.reduced (10, 7);
        auto top = a.removeFromTop (16);
        g.setColour (theme::textMute);
        g.setFont (theme::caps (8.5f));
        g.drawText ("MASTER CHECK", top, juce::Justification::centredLeft);

        const auto chipf = theme::ui (9.5f, juce::Font::bold);
        {   // CHECK judges; AUTO converges (the two verbs of the card)
            const auto label = checking ? juce::String ("CHECKING") : juce::String ("CHECK");
            const float w = theme::measure (chipf, label) + 22.0f;
            auto cr = top.removeFromRight ((int) w).toFloat().expanded (0.0f, 2.0f);
            theme::chip (g, cr, checking ? theme::warn : theme::accent, label, chipf,
                         checking ? 0.30f : 0.16f, 0.8f, checking);
            if (! checking && ! mastering) hits.push_back ({ cr, "check", 0 });
            top.removeFromRight (5);
            const auto alab = mastering ? juce::String ("MASTERING") : juce::String ("AUTO");
            const float aw = theme::measure (chipf, alab) + 22.0f;
            auto ar = top.removeFromRight ((int) aw).toFloat().expanded (0.0f, 2.0f);
            theme::chip (g, ar, mastering ? theme::warn : theme::accentB, alab, chipf,
                         mastering ? 0.30f : 0.16f, 0.85f, mastering);
            if (! mastering && ! checking) hits.push_back ({ ar, "auto", 0 });
        }
        a.removeFromTop (3);

        if (! report.isObject())
        {
            g.setColour (theme::textDim);
            g.setFont (theme::ui (10.5f));
            g.drawText (mastering ? "auto-master: converging (renders + measures)..."
                        : checking ? "rendering + measuring..."
                        : "CHECK judges vs the genre target;",
                        a.removeFromTop (16), juce::Justification::centredLeft);
            if (! checking && ! mastering)
                g.drawText ("AUTO converges the chain until it passes",
                            a.removeFromTop (14), juce::Justification::centredLeft);
            return;
        }

        const bool pass = (bool) report.getProperty ("pass", false);
        const double score = (double) report.getProperty ("score", 0.0);
        {   // verdict row: PASS/FIX pill + score + target lane
            auto row = a.removeFromTop (20);
            auto pr = row.removeFromLeft (52).toFloat().reduced (0.0f, 1.0f);
            theme::chip (g, pr, pass ? theme::good : theme::warn, pass ? "PASS" : "FIX",
                         theme::ui (10.5f, juce::Font::bold), 0.3f, 0.95f, true);
            g.setColour (theme::text);
            g.setFont (theme::mono (10.5f, juce::Font::bold));
            g.drawText (juce::String (score * 100.0, 0) + "%", row.removeFromLeft (44),
                        juce::Justification::centredLeft);
            g.setColour (theme::textDim);
            g.setFont (theme::mono (8.5f));
            g.drawText (report.getProperty ("target", "").toString(), row,
                        juce::Justification::centredRight);
        }
        a.removeFromTop (3);

        auto* checks = report.getProperty ("checks", juce::var()).getArray();
        juce::String firstHint;
        if (checks != nullptr)
        {
            const auto fixFirst = report.getProperty ("fix_first", "").toString();
            for (auto& c : *checks)
            {
                if (a.getHeight() < 26) break;
                auto row = a.removeFromTop (13);
                const bool ok = (bool) c.getProperty ("ok", false);
                const auto nm = c.getProperty ("name", "?").toString();
                g.setColour (ok ? theme::good : theme::bad);
                g.fillEllipse ((float) row.getX() + 1.0f, (float) row.getCentreY() - 2.5f, 5.0f, 5.0f);
                g.setColour (nm == fixFirst && ! ok ? theme::text : ok ? theme::textDim : theme::warn);
                g.setFont (theme::ui (9.5f, nm == fixFirst && ! ok ? juce::Font::bold : juce::Font::plain));
                g.drawText (nm, row.withTrimmedLeft (10).withWidth (92), juce::Justification::centredLeft);
                g.setColour (ok ? theme::textMute : theme::text);
                g.setFont (theme::mono (8.5f));
                auto gotv = c.getProperty ("got", juce::var());
                const auto got = gotv.isDouble() ? juce::String ((double) gotv, 2)
                               : gotv.isObject() || gotv.isArray() ? juce::String ("(bands)")
                               : gotv.toString();
                g.drawText (got + "  " + c.getProperty ("want", "").toString().substring (0, 14),
                            row.withTrimmedLeft (104), juce::Justification::centredLeft);
                if (! ok && firstHint.isEmpty())
                    firstHint = c.getProperty ("hint", "").toString();
            }
        }
        if (! pass && a.getHeight() >= 22)
        {   // one action: hand the failing verdict to the agent
            auto br = a.removeFromBottom (20).toFloat().reduced (0.0f, 1.0f);
            theme::chip (g, br, theme::agent, "ASK AGENT TO FIX", chipf, 0.18f, 0.85f, true);
            hits.push_back ({ br, "fix", 0 });
        }
        if (firstHint.isNotEmpty() && a.getHeight() > 20)
        {
            g.setColour (theme::textDim);
            g.setFont (theme::ui (8.5f));
            g.drawFittedText (firstHint, a.reduced (1, 2), juce::Justification::topLeft, 3, 1.0f);
        }
    }

    void mouseMove (const juce::MouseEvent& e) override
    {
        lastMouse = e.position;
        repaint (0, 0, getWidth(), headerH);               // chips answer the hand
    }
    void mouseExit (const juce::MouseEvent&) override
    {
        lastMouse = { -1.0f, -1.0f };
        repaint (0, 0, getWidth(), headerH);
    }

    // ---- module header drag = carry the module to a new slot (arrows stay) ----
    int dragFrom = -1, dragInsert = -1;
    void updateDragInsert (int stripX)
    {
        int ins = 0;
        for (auto* m : modules)
            if (stripX > m->getBounds().getCentreX()) ++ins;
        if (ins != dragInsert) { dragInsert = ins; repaint(); }
    }
    void finishDrag()
    {
        const int from = dragFrom, to = dragInsert;
        dragFrom = dragInsert = -1;
        repaint();
        if (from < 0 || to < 0 || to == from || to == from + 1) return;
        moveFxTo (from, to > from ? to - 1 : to);
    }
    void moveFxTo (int from, int dest)                     // deferred (same law as moveFx)
    {
        juce::MessageManager::callAsync ([sp = juce::Component::SafePointer<FxRackPanel> (this), from, dest]
        {
            auto* self = sp.getComponent();
            if (self == nullptr) return;
            auto* ch = self->chain();
            if (ch == nullptr || from < 0 || dest < 0
                || from >= (int) ch->size() || dest >= (int) ch->size()) return;
            auto fx = std::move ((*ch)[(size_t) from]);
            ch->erase (ch->begin() + from);
            ch->insert (ch->begin() + dest, std::move (fx));
            if (self->pointedFx == from) self->pointedFx = dest;
            if (self->onStructure) self->onStructure();
            self->refreshTarget();
        });
    }
    void paintOverChildren (juce::Graphics& g) override
    {
        if (dragFrom < 0 || dragInsert < 0 || modules.isEmpty()) return;
        const int nMod = modules.size();
        const auto stripRect = dragInsert <= 0
            ? modules[0]->getBounds().withWidth (3).translated (-4, 0)
            : modules[juce::jmin (dragInsert, nMod) - 1]->getBounds()
                  .withX (modules[juce::jmin (dragInsert, nMod) - 1]->getRight() + 2).withWidth (3);
        const auto seam = getLocalArea (&strip, stripRect).toFloat();
        if (seam.getRight() < 0 || seam.getX() > (float) getWidth()) return;
        theme::glowRing (g, seam, theme::accent, 2.0f);
        g.setGradientFill (theme::brand (seam, 0.95f));
        g.fillRoundedRectangle (seam, 1.5f);
    }

    void mouseDown (const juce::MouseEvent& e) override
    {
        for (auto& hz : hits)
            if (hz.r.contains (e.position))
            {
                if (hz.act == "close")       { if (onCloseRack) onCloseRack(); }
                else if (hz.act == "track")  setTarget (Kind::track, hz.arg);
                else if (hz.act == "bus")    setTarget (Kind::bus, hz.arg);
                else if (hz.act == "master") setTarget (Kind::master, 0);
                else if (hz.act == "add")    showAddMenu();
                else if (hz.act == "check")  { if (onRunCheck) onRunCheck(); }
                else if (hz.act == "auto")   { if (onRunAuto) onRunAuto(); }
                else if (hz.act == "fix")    askAgent();
                return;
            }
    }

    // ---------------------------------------------------------------- chain edits
    void addFx (const sotadaw::SongFx& fx)
    {
        if (auto* ch = chain())
        {
            ch->push_back (fx);
            if (onStructure) onStructure();
            refreshTarget();
        }
    }
    // remove/move are triggered from a Module's OWN mouseDown, and rebuilding the
    // module list would delete that component mid-event — defer to the next tick.
    void removeFx (int i)
    {
        juce::MessageManager::callAsync ([sp = juce::Component::SafePointer<FxRackPanel> (this), i]
        {
            auto* self = sp.getComponent();
            if (self == nullptr) return;
            if (auto* ch = self->chain(); ch != nullptr && i >= 0 && i < (int) ch->size())
            {
                ch->erase (ch->begin() + i);
                if (self->pointedFx == i)
                { self->pointedFx = -1; if (self->onPointedChange) self->onPointedChange(); }
                if (self->onStructure) self->onStructure();
                self->refreshTarget();
            }
        });
    }
    void moveFx (int i, int dir)
    {
        juce::MessageManager::callAsync ([sp = juce::Component::SafePointer<FxRackPanel> (this), i, dir]
        {
            auto* self = sp.getComponent();
            if (self == nullptr) return;
            auto* ch = self->chain();
            const int j = i + dir;
            if (ch == nullptr || i < 0 || j < 0 || i >= (int) ch->size() || j >= (int) ch->size()) return;
            std::swap ((*ch)[(size_t) i], (*ch)[(size_t) j]);
            if (self->pointedFx == i) self->pointedFx = j;
            else if (self->pointedFx == j) self->pointedFx = i;
            if (self->onStructure) self->onStructure();
            self->refreshTarget();
        });
    }
    void toggleBypass (int i)
    {
        auto* ch = chain();
        if (ch == nullptr || i < 0 || i >= (int) ch->size()) return;
        auto& f = (*ch)[(size_t) i];
        f.bypass = ! f.bypass;
        if (auto* p = resolvePlugin ? resolvePlugin (i) : nullptr)
            p->setEnabled (! f.bypass);                    // LIVE A/B — no rebuild
        if (onParamEdited) onParamEdited();
        repaint();
        for (auto* m : modules) m->repaint();
    }
    void togglePoint (int i)
    {
        pointedFx = pointedFx == i ? -1 : i;
        if (onPointedChange) onPointedChange();
        for (auto* m : modules) m->repaint();
    }

    void showAddMenu()
    {
        juce::PopupMenu m;
        m.addSectionHeader ("FAUST FX");
        if (listFaustFx)
            for (auto& id : listFaustFx())
                m.addItem (id, [this, id] { addFx ({ id, "faustfx", {}, false, {} }); });
        m.addSectionHeader ("BUILT-IN");
        m.addItem ("eq (4-band)", [this] { addFx ({ "eq", "eq", {}, false, {} }); });
        m.addItem ("comp",        [this] { addFx ({ "comp", "comp", {}, false, {} }); });
        if (listVstFx)
        {
            auto vsts = listVstFx();
            if (! vsts.isEmpty())
            {
                m.addSectionHeader ("VST3 INSERTS");
                for (auto& v : vsts)
                    m.addItem (v, [this, v] { addFx ({ "vst3:" + v, "faustfx", {}, false, {} }); });
            }
        }
        m.showMenuAsync ({});
    }

    void askAgent()
    {
        if (! report.isObject() || onAskAgent == nullptr) return;
        juce::StringArray fails;
        if (auto* checks = report.getProperty ("checks", juce::var()).getArray())
            for (auto& c : *checks)
                if (! (bool) c.getProperty ("ok", false))
                {
                    auto gotv = c.getProperty ("got", juce::var());
                    fails.add (c.getProperty ("name", "?").toString() + " (got "
                               + (gotv.isDouble() ? juce::String ((double) gotv, 2) : gotv.toString())
                               + ", want " + c.getProperty ("want", "").toString() + ")");
                }
        onAskAgent ("MASTER CHECK failed on " + fails.joinIntoString (", ")
                    + ". Fix at the source per the mastering-verdict and mix-headroom skills, then "
                    "run master_report after each change until pass is true. Genre lane: "
                    + report.getProperty ("target", "generic").toString() + ".");
    }

private:
    void timerCallback() override
    {
        if (! isVisible()) return;
        for (auto* m : modules) m->syncKnobs();
        if (checking || mastering) repaint (getWidth() - cardW - 8, 0, cardW + 8, headerH + 6);
    }

    // ------------------------------------------------------------ the mini knob
    // Edits the LIVE engine parameter and persists into the song's fx params in the
    // same gesture (the rack's contract; faces are live-only).
    class RackKnob : public juce::Slider
    {
    public:
        RackKnob (te::AutomatableParameter* p, juce::Colour accent,
                  std::function<void (float)> persist)
            : param (p), col (accent), persistFn (std::move (persist))
        {
            setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
            setTextBoxStyle (juce::Slider::NoTextBox, true, 0, 0);
            setRotaryParameters (juce::MathConstants<float>::pi * 1.25f,
                                 juce::MathConstants<float>::pi * 2.75f, true);
            const auto lo = param->valueRange.start, hi = param->valueRange.end;
            setRange (lo, hi, 0.0);
            setValue (param->getCurrentValue(), juce::dontSendNotification);
            setDoubleClickReturnValue (true, param->getCurrentValue());
            setName (param->getParameterName());
            onValueChange = [this]
            {
                param->setParameter ((float) getValue(), juce::sendNotification);
                if (persistFn) persistFn ((float) getValue());
            };
        }
        void syncFromParam()
        {
            if (! isMouseButtonDown())
                setValue (param->getCurrentValue(), juce::dontSendNotification);
        }
        void paint (juce::Graphics& g) override
        {
            auto r = getLocalBounds().toFloat();
            auto well = r.withHeight (r.getWidth()).reduced (7.0f);
            const float cx = well.getCentreX(), cy = well.getCentreY(), rad = well.getWidth() * 0.5f;
            const float a0 = juce::MathConstants<float>::pi * 1.25f,
                        a1 = juce::MathConstants<float>::pi * 2.75f;
            const float t = (float) valueToProportionOfLength (getValue());
            const float at = a0 + (a1 - a0) * t;
            const float aw = juce::jmax (2.6f, rad * 0.13f);
            g.setColour (theme::inset);
            g.fillEllipse (well.expanded (2.0f));
            g.setGradientFill ({ theme::panelHi.brighter (0.10f), cx, well.getY(),
                                 theme::panel.darker (0.22f), cx, well.getBottom(), false });
            g.fillEllipse (well.reduced (aw + 2.0f));
            juce::Path track, val;
            track.addCentredArc (cx, cy, rad, rad, 0.0f, a0, a1, true);
            g.setColour (theme::grid);
            g.strokePath (track, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
            if (t > 0.004f)
            {
                val.addCentredArc (cx, cy, rad, rad, 0.0f, a0, at, true);
                g.setColour (col.withAlpha (persistFn ? 0.95f : 0.55f));   // dimmer arc = live-only
                g.strokePath (val, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
            }
            const float px = cx + std::sin (at) * (rad - aw * 1.6f),
                        py = cy - std::cos (at) * (rad - aw * 1.6f);
            g.setColour (theme::text);
            g.fillEllipse (px - 1.6f, py - 1.6f, 3.2f, 3.2f);
            g.setColour (theme::textDim);
            g.setFont (theme::ui (8.0f, juce::Font::bold));
            g.drawText (getName().substring (0, 9),
                        r.withTrimmedTop (r.getWidth() - 3.0f).withHeight (10.0f).toNearestInt(),
                        juce::Justification::centred);
            g.setColour (col.brighter (0.2f));
            g.setFont (theme::mono (8.0f));
            g.drawText (juce::String (getValue(), std::abs (getMaximum() - getMinimum()) > 20.0 ? 0 : 2),
                        r.withTrimmedTop (r.getWidth() + 6.5f).withHeight (9.0f).toNearestInt(),
                        juce::Justification::centred);
        }
    private:
        te::AutomatableParameter* param;
        juce::Colour col;
        std::function<void (float)> persistFn;
    };

    // ------------------------------------------------------------ one module card
    class Module : public juce::Component
    {
    public:
        Module (FxRackPanel& ownerIn, int indexIn) : owner (ownerIn), index (indexIn)
        {
            auto* ch = owner.chain();
            if (ch == nullptr || index >= (int) ch->size()) return;
            auto& f = (*ch)[(size_t) index];
            isVst = f.id.startsWith ("vst3:");
            title = isVst ? f.id.substring (5) : (f.id.isNotEmpty() ? f.id : f.type);
            if (title.startsWith ("fx_")) title = title.substring (3);
            auto* plug = owner.resolvePlugin ? owner.resolvePlugin (index) : nullptr;
            if (plug != nullptr && ! isVst)                // vst3: face-only (natural-units law)
                for (auto p : plug->getAutomatableParameters())
                {
                    if (p == nullptr || knobs.size() >= 8) continue;
                    const auto key = songKeyFor (f, p->paramID);
                    if (f.type != "faustfx" && key.isEmpty()) continue;   // unmapped built-in extras
                    auto persist = key.isEmpty() ? std::function<void (float)>()
                                 : std::function<void (float)> ([this, key] (float v)
                                   {
                                       if (auto* c2 = owner.chain(); c2 != nullptr && index < (int) c2->size())
                                       {
                                           (*c2)[(size_t) index].params[key] = v;
                                           if (owner.onParamEdited) owner.onParamEdited();
                                       }
                                   });
                    auto* k = knobs.add (new RackKnob (p, owner.targetColour(), std::move (persist)));
                    addAndMakeVisible (k);
                }
        }

        int preferredWidth() const
        {
            if (knobs.isEmpty()) return 132;
            return juce::jmax (110, juce::jmin (4, knobs.size()) * 48 + 14);
        }

        void resized() override
        {
            auto r = getLocalBounds().reduced (7, 0).withTrimmedTop (19);
            const int rows = knobs.size() > 4 ? 2 : 1;
            const int kh = juce::jmin (62, r.getHeight() / rows);
            const int perRow = rows == 1 ? knobs.size() : (knobs.size() + 1) / 2;
            for (int i = 0; i < knobs.size(); ++i)
            {
                const int row = i / juce::jmax (1, perRow), colI = i % juce::jmax (1, perRow);
                knobs[i]->setBounds (r.getX() + colI * 48, r.getY() + row * kh, 44, kh);
            }
        }

        void syncKnobs() { for (auto* k : knobs) k->syncFromParam(); }

        void paint (juce::Graphics& g) override
        {
            auto* ch = owner.chain();
            if (ch == nullptr || index >= (int) ch->size()) return;
            auto& f = (*ch)[(size_t) index];
            const auto col = owner.targetColour();
            auto r = getLocalBounds().toFloat().reduced (1.0f);
            const auto base = f.bypass ? theme::panel.darker (0.12f) : theme::panelHi;
            theme::card (g, r, isMouseOver (true) && ! f.bypass ? base.brighter (0.05f) : base,
                         8.0f, f.bypass ? 0.4f : 1.0f);
            if (owner.dragFrom == index)                   // carried: the module lifts
            {
                g.setColour (owner.targetColour().withAlpha (0.14f));
                g.fillRoundedRectangle (r, 8.0f);
            }
            if (owner.pointedFx == index)                  // the agent is pointed HERE
            {
                g.setColour (theme::agent.withAlpha (0.9f));
                g.drawRoundedRectangle (r.reduced (0.6f), 8.0f, 1.5f);
            }
            auto head = getLocalBounds().reduced (7, 3).withHeight (14);
            // power dot: lit = active, hollow = bypassed
            powerRect = head.removeFromLeft (12).toFloat();
            g.setColour (f.bypass ? theme::textMute : theme::good);
            if (f.bypass) g.drawEllipse (powerRect.withSizeKeepingCentre (7.0f, 7.0f), 1.4f);
            else          g.fillEllipse (powerRect.withSizeKeepingCentre (7.0f, 7.0f));
            // ✕ remove, ▶ ◀ reorder (right-aligned)
            closeRect = head.removeFromRight (13).toFloat();
            g.setColour (theme::textDim);
            {
                const auto c = closeRect.reduced (3.0f);
                g.drawLine (c.getX(), c.getY(), c.getRight(), c.getBottom(), 1.3f);
                g.drawLine (c.getX(), c.getBottom(), c.getRight(), c.getY(), 1.3f);
            }
            rightRect = head.removeFromRight (12).toFloat();
            leftRect  = head.removeFromRight (12).toFloat();
            g.setFont (theme::ui (9.0f, juce::Font::bold));
            const bool canL = index > 0, canR = index + 1 < (int) ch->size();
            g.setColour (theme::textDim.withAlpha (canL ? 0.9f : 0.3f));
            g.drawText (juce::String::fromUTF8 ("\xe2\x97\x80"), leftRect.toNearestInt(), juce::Justification::centred);
            g.setColour (theme::textDim.withAlpha (canR ? 0.9f : 0.3f));
            g.drawText (juce::String::fromUTF8 ("\xe2\x96\xb6"), rightRect.toNearestInt(), juce::Justification::centred);
            // title (double-click = face)
            g.setColour (f.bypass ? theme::textDim : col.brighter (0.25f));
            g.setFont (theme::ui (10.0f, juce::Font::bold));
            titleRect = head.toFloat();
            g.drawText (title, head, juce::Justification::centredLeft);
            if (isVst || knobs.isEmpty())
            {
                g.setColour (theme::textDim);
                g.setFont (theme::ui (9.0f));
                g.drawFittedText (isVst ? "vst3 insert - double-click for its own editor"
                                        + juce::String (f.preset.isNotEmpty() ? "\npreset: "
                                            + juce::File (f.preset).getFileName() : juce::String())
                                        : "no live params (rebuild pending?)",
                                  getLocalBounds().reduced (9, 4).withTrimmedTop (18),
                                  juce::Justification::topLeft, 3);
            }
            if (f.bypass)
            {
                g.setColour (theme::textMute);
                g.setFont (theme::caps (8.0f));
                g.drawText ("BYPASSED", getLocalBounds().removeFromBottom (11),
                            juce::Justification::centred);
            }
        }

        void mouseDown (const juce::MouseEvent& e) override
        {
            if (powerRect.contains (e.position))      { owner.toggleBypass (index); return; }
            if (closeRect.contains (e.position))      { owner.removeFx (index); return; }
            if (leftRect.contains (e.position))       { owner.moveFx (index, -1); return; }
            if (rightRect.contains (e.position))      { owner.moveFx (index, +1); return; }
            if (e.mods.isCtrlDown() || e.mods.isCommandDown())
            { owner.togglePoint (index); return; }    // point the agent at THIS fx
            if (titleRect.contains (e.position))      // grab the header = carry the module
            {
                carrying = true;
                owner.dragFrom = index;
                owner.updateDragInsert (getX() + e.getPosition().x);
            }
        }
        void mouseDrag (const juce::MouseEvent& e) override
        {
            if (carrying)
                owner.updateDragInsert (e.getEventRelativeTo (&owner.strip).getPosition().x);
        }
        void mouseUp (const juce::MouseEvent&) override
        {
            if (carrying) { carrying = false; owner.finishDrag(); }
        }
        void mouseMove (const juce::MouseEvent& e) override
        {
            setMouseCursor (titleRect.contains (e.position)
                              ? juce::MouseCursor::DraggingHandCursor
                              : juce::MouseCursor::NormalCursor);
        }
        void mouseEnter (const juce::MouseEvent&) override { repaint(); }
        void mouseExit (const juce::MouseEvent&) override  { repaint(); }
        void mouseDoubleClick (const juce::MouseEvent&) override
        {
            if (owner.onOpenFace) owner.onOpenFace (index);
        }
        bool carrying = false;

    private:
        // engine param id -> song.json params key (the persistence contract):
        // faust zones ARE their ids; built-ins map to the friendly keys makeFaustFx reads.
        static juce::String songKeyFor (const sotadaw::SongFx& f, const juce::String& paramID)
        {
            if (f.type == "eq")
            {
                static const std::map<juce::String, juce::String> m {
                    { "Low-pass freq", "loFreq" },   { "Low-pass gain", "loGain" },
                    { "Mid freq 1", "midFreq" },     { "Mid gain 1", "midGain" },  { "Mid Q 1", "midQ" },
                    { "Mid freq 2", "midFreq2" },    { "Mid gain 2", "midGain2" }, { "Mid Q 2", "midQ2" },
                    { "High-pass freq", "hiFreq" },  { "High-pass gain", "hiGain" } };
                auto it = m.find (paramID);
                return it != m.end() ? it->second : juce::String();
            }
            if (f.type == "comp")
            {
                if (paramID == "output gain") return "outputDb";
                if (paramID == "threshold" || paramID == "ratio"
                    || paramID == "attack" || paramID == "release") return paramID;
                return {};
            }
            return paramID;                            // faust: zone name == param id == song key
        }

        FxRackPanel& owner;
        int index = 0;
        bool isVst = false;
        juce::String title;
        juce::OwnedArray<RackKnob> knobs;
        juce::Rectangle<float> powerRect, closeRect, leftRect, rightRect, titleRect;
    };

    struct Hit { juce::Rectangle<float> r; juce::String act; int arg; };
    std::vector<Hit> hits;
    juce::Point<float> lastMouse { -1.0f, -1.0f };   // header chips answer the hand
    juce::Viewport viewport;
    juce::Component strip;
    juce::OwnedArray<Module> modules;
};
