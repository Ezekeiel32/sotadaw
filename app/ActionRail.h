// ActionRail.h - THE ACTION RAILS (agent-first law, Chezy's UI CHAT SPEC 2026-07-07;
// WINGS ARE AIR, 2026-07-08): every move the agent makes streams IMMEDIATELY into
// agent mode as a live glass card speaking the DAW's own grammar - SOUND + FX on
// the LEFT wing, MASTER on the RIGHT. THE WING ITSELF IS INVISIBLE: no panel, no
// header, no grid, no placeholder - the whole page is the chat, and components
// MATERIALIZE on either side of the centred column only when the agent GENERATES
// them (receipts) or the user SELECTS something (track strip / master strip).
// Each card is born at the column's edge and drifts into place (fade + drift +
// settle on the host clock); an empty wing is pure page. Fed by the edit-receipt
// stream (ipc/receipts.jsonl - the same receipts the SCOPE LAW audits), enriched
// from the live proposal parse (cards show the STATE of what was touched, not
// prose), frozen by the take's verdict. Material is GhostGlass: frosted body, top
// sheen, breathing tinted edge - state as material, never banners. Rails RENDER
// only in agent mode (the sidebar keeps its own story); ingestion never stops, so
// flipping F4 reveals the session's whole action history.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "SongLoader.h"
#include "UiTheme.h"
#include "PluginFaces.h"   // the voice's FACE rides into the chat (one-resolver law)

//==============================================================================
// One agent action as a glass card: header (KIND + track | tool), a state body
// bound to the freshest song/proposal parse, the receipt's own words as a dim
// mono footer. Consecutive same-shaped actions collapse into one card ("xN").
class ActionCard : public juce::Component
{
public:
    enum class Kind { fx, sound, mix, sends, motion, master, buses, ears };

    ActionCard (Kind k, juce::String toolIn, juce::String trackIn, juce::String summaryIn)
        : kind (k), tool (std::move (toolIn)), track (std::move (trackIn)),
          summary (std::move (summaryIn))
    {
        setInterceptsMouseClicks (true, false);   // click = whole receipt to clipboard
        freshAt = juce::Time::getMillisecondCounter();
    }

    Kind cardKind() const           { return kind; }
    const juce::String& toolName() const  { return tool; }
    const juce::String& trackName() const { return track; }
    bool live() const               { return verdict < 0; }
    // a card deserves a PATCH CABLE while what it shows is IN the song: live
    // runs, accepted takes, standing/selection material. Rejected (2) and
    // dissolved (0) describe changes that are NOT in the song - no wire lies.
    bool wiredState() const         { return verdict != 0 && verdict != 2; }

    void bump (const juce::String& newSummary)   // same action again: collapse, re-flash
    {
        ++count;
        if (newSummary.isNotEmpty()) summary = newSummary;
        freshAt = juce::Time::getMillisecondCounter();
        repaint();
    }

    // ---- EARS payload (right rail, mastering evidence) ----
    void setEars (juce::String which, double peak, int clipped, double lufs)
    {
        earsWhich = std::move (which); earsPeak = peak; earsClipped = clipped; earsLufs = lufs;
        repaint();
    }

    // ---- state binding: copy WHAT WAS TOUCHED out of the freshest parse ----
    // (copies, never pointers - the flow's song moves on without us; stale-ptr law)
    void retarget (const sotadaw::Song& s)
    {
        if (! live()) return;
        const sotadaw::SongTrack* t = nullptr;
        for (auto& tr : s.tracks) if (tr.name == track) { t = &tr; break; }
        switch (kind)
        {
            case Kind::fx:     if (t != nullptr) chain = t->fx;      break;
            case Kind::sound:  if (t != nullptr) { srcKind = t->source.kind; srcId = t->source.id;
                                                   srcPreset = t->source.preset;
                                                   srcParams = t->source.params;
                                                   // PATTERN DNA: a knobless voice
                                                   // still shows WHAT IT PLAYS
                                                   dna.clear(); dnaSpan = 0;
                                                   const size_t nN = t->notes.size();
                                                   const size_t stride = juce::jmax ((size_t) 1, nN / 160);
                                                   for (size_t ni = 0; ni < nN; ni += stride)
                                                   {
                                                       const auto& n = t->notes[ni];
                                                       dna.push_back ({ (float) n.start,
                                                                        (float) n.pitch,
                                                                        (float) n.vel });
                                                       dnaSpan = juce::jmax (dnaSpan,
                                                                     (float) (n.start + n.len));
                                                   } } break;
            case Kind::mix:    if (t != nullptr) { gainDb = t->gainDb; pan = t->pan; hasMix = true; } break;
            case Kind::sends:  if (t != nullptr) sends = t->sends;   break;
            case Kind::motion: if (t != nullptr) autos = t->automation;
                               else              autos = s.automation;   // song-scope motion
                               break;
            case Kind::master: chain = s.master; gainDb = s.masterGainDb; hasMix = true; break;
            case Kind::buses:  buses = s.buses;  break;
            case Kind::ears:   break;
        }
        repaint();
    }

    void freeze (int v)   // 0 dissolved / 1 accepted / 2 rejected (MidiCard grammar)
    {
        if (! live()) return;
        verdict = v;
        repaint();
    }

    void standing()       // 3 = the session DOSSIER: steady material, not an action
    {
        verdict = 3;      // not live (never retargets/bumps), no verdict stamp
        repaint();
    }

    // SELECTION cards (Chezy's initial spec): the current pick's fx/sound — cleared
    // and rebuilt on every selection change, distinct from the agent's action cards
    void markSelection()       { selCard = true; standing(); }
    bool fromSelection() const { return selCard; }

    // master/buses are SONG-GLOBAL steady state, not a frozen moment — refresh them
    // from the live song even while standing (a master card born from an empty-master
    // proposal receipt must pick up the real chain when the dossier tops up)
    void refreshStanding (const sotadaw::Song& s)
    {
        const int keep = verdict;
        verdict = -1;                 // briefly live so retarget runs
        retarget (s);
        verdict = keep;
        repaint();
    }
    bool chainEmpty() const { return chain.empty(); }

    // MATERIALIZE (wings-are-air law): a new card is born at the chat column's
    // edge, translucent, a breath small - and drifts OUTWARD into its resting
    // place. AGE-EASED and applied only on LIVE surfaces: an unmapped snapshot
    // rig never ticks, so a stateful alpha-0 birth would freeze invisible there
    // (isShowing() guards the pose; rigs shoot the landed truth). fromDx = where
    // it starts relative to rest (left wing +, right wing -: toward the column).
    void beginEntrance (float fromDx)
    {
        entFromX = fromDx;
        enterAt = juce::Time::getMillisecondCounter();
        if (isShowing()) applyEntrance();     // live page: strike the birth pose NOW
    }
    bool entering() const
    { return juce::Time::getMillisecondCounter() - enterAt < 430; }

    void tick()
    {
        if (! isShowing()) return;
        if (entering()) applyEntrance();      // entrance runs for EVERY card kind
        if (! live()) return;
        // a card can stay verdict-less for a whole session (fx/master receipts wait
        // for the take's accept/reject) — an endless 30Hz breath repaint per card
        // quietly ate the message thread as the wings filled (LAG DOSSIER v2 #3).
        // The breath settles after 45s; the card keeps its live tint, statically.
        if (juce::Time::getMillisecondCounter() - freshAt > 45000) return;
        breath += 0.05f;
        if (breath > juce::MathConstants<float>::twoPi) breath -= juce::MathConstants<float>::twoPi;
        repaint();
    }

    void mouseUp (const juce::MouseEvent& e) override
    {
        if (e.mouseWasDraggedSinceMouseDown()) return;
        juce::SystemClipboard::copyTextToClipboard (tool + " " + track + ": " + summary);
        copiedAt = juce::Time::getMillisecondCounter();
        repaint();
    }

    //-------------------------------------------------------------- measure
    static const char* kindWord (Kind k)
    {
        switch (k)
        {
            case Kind::fx:     return "FX";
            case Kind::sound:  return "SOUND";
            case Kind::mix:    return "MIX";
            case Kind::sends:  return "SENDS";
            case Kind::motion: return "MOTION";
            case Kind::master: return "MASTER";
            case Kind::buses:  return "BUSES";
            case Kind::ears:   return "EARS";
        }
        return "";
    }

    // device flow for fx chains: how many rows of DEVICE TILES at this width?
    // (UI CHAT SPEC law: the chain renders as the DAW's own devices — knob
    // tiles — never text chips)
    int deviceRows (int w) const
    {
        if (kind != Kind::fx && kind != Kind::master) return 0;
        if (chain.empty()) return 1;
        const int perRow = juce::jmax (1, (w - 18) / (deviceW + 6));
        const int n = juce::jmin ((int) chain.size(), 6);
        return juce::jmin (2, (n + perRow - 1) / perRow);
    }

    int preferredHeight (int w) const
    {
        int body = 16;
        switch (kind)
        {
            case Kind::fx:     body = deviceRows (w) * (deviceH + 5);             break;
            case Kind::master: body = deviceRows (w) * (deviceH + 5) + 18;        break;
            case Kind::sound:  body = ! srcParams.empty() ? 52
                                    : ! dna.empty()       ? 46 : 32;               break;
            case Kind::mix:    body = 30;                                          break;
            case Kind::sends:  body = 16 * juce::jmin (3, juce::jmax (1, (int) sends.size())); break;
            case Kind::motion: body = 14 * juce::jmin (2, juce::jmax (1, (int) autos.size())) + 22; break;
            case Kind::buses:  body = 16 * juce::jmin (3, juce::jmax (1, (int) buses.size()));      break;
            case Kind::ears:   return 22 + 34 + 6;   // no footer: the numbers ARE the story
        }
        return 22 + body + 15 + 6;
    }

    //---------------------------------------------------------------- paint
    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        const float br = 0.5f + 0.5f * std::sin (breath);
        const auto tint = live()       ? theme::accentB
                        : verdict == 1 ? theme::good
                        : verdict == 2 ? theme::bad
                        : verdict == 3 ? theme::accent   // STANDING dossier: VISIBLE (was
                                       : theme::textMute; // dim grey -> device tiles vanished)

        // frosted glass body (GhostGlass numbers) + the take-side tint
        g.setColour (juce::Colours::white.withAlpha (live() ? 0.030f + 0.012f * br : 0.026f));
        g.fillRoundedRectangle (r, 8.0f);
        g.setColour (tint.withAlpha (live() ? 0.050f : 0.030f));
        g.fillRoundedRectangle (r, 8.0f);
        auto sheen = r.withHeight (juce::jmin (14.0f, r.getHeight() * 0.32f));
        g.setGradientFill ({ juce::Colours::white.withAlpha (0.06f), sheen.getTopLeft(),
                             juce::Colours::white.withAlpha (0.0f),  sheen.getBottomLeft(), false });
        g.fillRoundedRectangle (sheen, 8.0f);

        // birth flash: the card LANDS (fresh receipts glow for ~600ms)
        const auto age = juce::Time::getMillisecondCounter() - freshAt;
        if (age < 600)
        {
            g.setColour (tint.withAlpha (0.16f * (1.0f - (float) age / 600.0f)));
            g.fillRoundedRectangle (r, 8.0f);
        }

        // breathing edge while the agent is alive; verdict sets it still
        g.setColour (tint.withAlpha (live() ? 0.24f + 0.24f * br
                                            : verdict == 0 ? 0.14f : 0.40f));
        g.drawRoundedRectangle (r, 8.0f, live() ? 1.4f : 1.1f);

        // header: KIND + track | tool xN
        auto head = r.reduced (9.0f, 0.0f).withTrimmedTop (4.0f).withHeight (16.0f);
        g.setColour (tint.brighter (0.15f).withAlpha (0.95f));
        g.setFont (theme::caps (8.5f));
        const auto kw = juce::String (kindWord (kind));
        g.drawText (kw, head.toNearestInt(), juce::Justification::centredLeft);
        const float kwW = theme::measure (theme::caps (8.5f), kw) + 7.0f;
        g.setColour (theme::text.withAlpha (0.88f));
        g.setFont (theme::ui (10.5f, juce::Font::bold));
        g.drawText (kind == Kind::ears ? earsWhich : track,
                    head.withTrimmedLeft (kwW).toNearestInt(), juce::Justification::centredLeft);
        g.setColour (theme::textMute.withAlpha (0.85f));
        g.setFont (theme::mono (8.5f));
        g.drawText (count > 1 ? tool + " x" + juce::String (count) : tool,
                    head.toNearestInt(), juce::Justification::centredRight);

        // THE AGENT'S MARK while live / the verdict stamp once decided
        if (live())
        {
            auto sp = juce::Rectangle<float> (r.getRight() - 17.0f, r.getY() + 3.5f, 9.0f, 9.0f);
            if (getWidth() > 150 && tool.length() * 6 < getWidth() - 60)
                theme::spark (g, sp, tint.withAlpha (0.30f + 0.30f * br));
        }
        else if (verdict == 1 || verdict == 2)   // dossier cards (3) wear no stamp
        {
            const float cx = r.getRight() - 13.0f, cy = r.getY() + 8.5f;
            juce::Path p;
            if (verdict == 1) { p.startNewSubPath (cx - 3.4f, cy);        p.lineTo (cx - 0.8f, cy + 2.8f); p.lineTo (cx + 3.6f, cy - 2.6f); }
            else              { p.startNewSubPath (cx - 3.0f, cy - 3.0f); p.lineTo (cx + 3.0f, cy + 3.0f);
                                p.startNewSubPath (cx + 3.0f, cy - 3.0f); p.lineTo (cx - 3.0f, cy + 3.0f); }
            g.setColour (tint.withAlpha (0.9f));
            g.strokePath (p, { 1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        }

        auto body = r.reduced (9.0f, 0.0f).withTrimmedTop (22.0f);
        switch (kind)
        {
            case Kind::fx:
            case Kind::master: paintDevices (g, body, tint); break;
            case Kind::sound:  paintSound (g, body);         break;
            case Kind::mix:    paintMix   (g, body);         break;
            case Kind::sends:  paintSends (g, body);         break;
            case Kind::motion: paintMotion (g, body, tint);  break;
            case Kind::buses:  paintBuses (g, body, tint);   break;
            case Kind::ears:   paintEars  (g, body);         break;
        }

        if (kind != Kind::ears)   // the receipt's own words, one dim mono line
        {
            g.setColour (theme::textMute.withAlpha (0.62f));
            g.setFont (theme::mono (8.5f));
            g.drawText (summary, r.reduced (9.0f, 0.0f).withTrimmedTop (r.getHeight() - 19.0f)
                                  .withHeight (13.0f).toNearestInt(),
                        juce::Justification::centredLeft);
        }
        if (juce::Time::getMillisecondCounter() - copiedAt < 900)
        {
            g.setColour (theme::good.withAlpha (0.9f));
            g.setFont (theme::ui (8.5f, juce::Font::bold));
            g.drawText ("copied", r.reduced (9.0f, 2.0f).toNearestInt(), juce::Justification::bottomRight);
        }
    }

private:
    static juce::String chipLabel (const sotadaw::SongFx& f)
    {
        auto id = f.id.startsWith ("fx_") ? f.id.substring (3) : f.id;
        if (id.startsWith ("vst3:")) id = id.substring (5);
        if (f.bypass) id = "(" + id + ")";
        return f.params.empty() ? id : id + " ." + juce::String ((int) f.params.size());
    }
    juce::String gainLabel() const
    { return "gain " + juce::String (gainDb, 1) + "dB"; }

    // one param -> an honest 0..1 knob position (per-key musical ranges; unknown
    // keys take a symmetric squash so ANY value still points somewhere true)
    static float knobNorm (const juce::String& k, float v)
    {
        if (k == "mix" || k == "amount" || k == "width" || k == "depth" || k == "feedback")
            return juce::jlimit (0.0f, 1.0f, v);
        if (k == "ceiling")  return juce::jlimit (0.0f, 1.0f, (v + 3.0f) / 3.0f);
        if (k == "level" || k == "gain" || k == "makeup")
            return juce::jmap (juce::jlimit (-24.0f, 6.0f, v), -24.0f, 6.0f, 0.0f, 1.0f);
        if (k == "cutoff" || k == "freq")
            return juce::jlimit (0.0f, 1.0f,
                                 std::log (juce::jmax (20.0f, v) / 20.0f) / std::log (1000.0f));
        if (k == "knob" || k == "pan") return juce::jlimit (0.0f, 1.0f, v * 0.5f + 0.5f);
        if (k == "drive" || k == "res" || k == "size")
            return juce::jlimit (0.0f, 1.0f, v / 4.0f);
        if (k == "time") return juce::jlimit (0.0f, 1.0f, v / 1.5f);
        return juce::jlimit (0.0f, 1.0f, v / (std::abs (v) + 1.0f) * 0.5f + 0.5f);
    }

    // THE DAW'S OWN KNOB (Chezy: "make the wings consistent with the DAW UI"):
    // this is faces::FaceKnob's anatomy verbatim, chat-sized — inset capped well,
    // machined inner ring, a 270deg grey track arc (1.25pi..2.75pi) with a
    // cool->hot gradient value arc, and a glow tip. One knob language across the
    // whole app: the modal, the mixer and the wing all draw the same face.
    static void drawKnob (juce::Graphics& g, float cx, float cy, float rad,
                          float norm, juce::Colour tint, bool dim)
    {
        const float a0 = juce::MathConstants<float>::pi * 1.25f;
        const float a1 = juce::MathConstants<float>::pi * 2.75f;
        const float at = a0 + (a1 - a0) * juce::jlimit (0.0f, 1.0f, norm);
        const float aw = juce::jmax (2.0f, rad * 0.17f);
        // well + capped face (vertical sheen = machined, the FaceKnob look)
        g.setColour (theme::inset.withAlpha (dim ? 0.5f : 1.0f));
        g.fillEllipse (cx - rad - 2.5f, cy - rad - 2.5f, (rad + 2.5f) * 2.0f, (rad + 2.5f) * 2.0f);
        g.setGradientFill ({ theme::panelHi.brighter (0.12f), cx, cy - rad,
                             theme::panel.darker (0.25f), cx, cy + rad, false });
        g.fillEllipse (cx - rad, cy - rad, rad * 2.0f, rad * 2.0f);
        g.setColour (theme::inset.brighter (0.35f).withAlpha (dim ? 0.4f : 0.9f));
        g.drawEllipse (cx - rad * 0.5f, cy - rad * 0.5f, rad, rad, 1.0f);   // machined inner ring
        // track arc + value arc (the FaceKnob gradient: cool bottom -> hot top)
        juce::Path track, val;
        track.addCentredArc (cx, cy, rad, rad, 0.0f, a0, a1, true);
        g.setColour (theme::grid.withAlpha (dim ? 0.5f : 1.0f));
        g.strokePath (track, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        if (norm > 0.004f)
        {
            val.addCentredArc (cx, cy, rad, rad, 0.0f, a0, at, true);
            g.setGradientFill ({ tint.darker (0.25f), cx - rad, cy + rad,
                                 tint.brighter (0.25f), cx + rad, cy - rad, false });
            g.strokePath (val, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        }
        // pointer + glow tip
        const float px = cx + std::sin (at) * (rad - aw * 1.6f);
        const float py = cy - std::cos (at) * (rad - aw * 1.6f);
        if (rad > 8.0f)
        {
            g.setColour (theme::text.withAlpha (dim ? 0.5f : 0.85f));
            g.drawLine (cx + std::sin (at) * rad * 0.34f, cy - std::cos (at) * rad * 0.34f,
                        px, py, juce::jmax (1.4f, aw * 0.5f));
        }
        g.setColour (tint.withAlpha (dim ? 0.3f : 0.4f));
        g.fillEllipse (px - aw, py - aw, aw * 2.0f, aw * 2.0f);
        g.setColour (theme::text.withAlpha (dim ? 0.55f : 1.0f));
        g.fillEllipse (px - aw * 0.45f, py - aw * 0.45f, aw * 0.9f, aw * 0.9f);
    }

    // THE DEVICES (UI CHAT SPEC): the chain as the DAW's own knob tiles — the
    // same grammar a producer reads on a rack, chat-sized
    void paintDevices (juce::Graphics& g, juce::Rectangle<float> body, juce::Colour tint)
    {
        if (chain.empty() && kind == Kind::fx)
        {
            g.setColour (theme::textMute.withAlpha (0.5f));
            g.setFont (theme::mono (9.5f));
            g.drawText ("chain cleared", body.withHeight (18.0f).toNearestInt(),
                        juce::Justification::centredLeft);
            return;
        }
        const int perRow = juce::jmax (1, ((int) body.getWidth()) / (deviceW + 6));
        float x = body.getX(), y = body.getY() + 1.0f;
        int col = 0, row = 0, shown = 0;
        for (auto& f : chain)
        {
            if (col == perRow) { col = 0; ++row; x = body.getX(); y += (float) deviceH + 5.0f; }
            if (row >= 2) break;
            juce::Rectangle<float> d (x, y, (float) deviceW, (float) deviceH);
            const bool dim = f.bypass;
            // the tile: an inset device face with a lit nameplate
            g.setColour (juce::Colour (0xff05060a).withAlpha (dim ? 0.45f : 0.8f));
            g.fillRoundedRectangle (d, 5.0f);
            g.setColour (tint.withAlpha (dim ? 0.16f : 0.35f));
            g.drawRoundedRectangle (d.reduced (0.5f), 5.0f, 1.0f);
            auto id = f.id.startsWith ("fx_") ? f.id.substring (3)
                    : f.id.startsWith ("vst3:") ? f.id.substring (5)
                    : f.id.fromLastOccurrenceOf ("/", false, false);
            g.setColour ((dim ? theme::textMute : theme::text).withAlpha (0.92f));
            g.setFont (theme::caps (7.6f));
            g.drawText (id.toUpperCase().substring (0, 13),
                        d.withHeight (13.0f).reduced (5.0f, 1.0f).toNearestInt(),
                        juce::Justification::centredLeft);
            if (dim)
            {
                g.setColour (theme::textMute.withAlpha (0.8f));
                g.setFont (theme::caps (6.0f));
                g.drawText ("BYP", d.withHeight (11.0f).reduced (4.0f, 0.0f).toNearestInt(),
                            juce::Justification::centredRight);
            }
            // up to 3 knobs, priority params first — the device's own hands
            static const char* prio[] = { "ceiling", "cutoff", "mix", "level", "amount",
                                          "drive", "knob", "gain", "res", "time", "size",
                                          "freq", "width", "depth", "feedback" };
            std::vector<std::pair<juce::String, float>> ks;
            for (auto* k : prio)
            {
                auto it = f.params.find (k);
                if (it != f.params.end()) ks.push_back ({ it->first, it->second });
                if (ks.size() == 3) break;
            }
            for (auto& pr : f.params)
            {
                if (ks.size() >= 3) break;
                bool have = false;
                for (auto& e : ks) if (e.first == pr.first) { have = true; break; }
                if (! have) ks.push_back ({ pr.first, pr.second });
            }
            const int nk = (int) ks.size();
            const float kr = 9.5f;                         // bigger tile -> bigger knobs
            for (int i = 0; i < nk; ++i)
            {
                const float kx = d.getX() + d.getWidth() * ((float) i + 0.5f) / (float) juce::jmax (1, nk);
                const float ky = d.getY() + 24.0f;
                drawKnob (g, kx, ky, kr, knobNorm (ks[(size_t) i].first, ks[(size_t) i].second),
                          tint, dim);
                g.setColour (theme::textMute.withAlpha (dim ? 0.4f : 0.8f));
                g.setFont (theme::mono (6.4f));
                g.drawText (ks[(size_t) i].first.substring (0, 8),
                            (int) (kx - 20.0f), (int) (ky + kr + 2.0f), 40, 9,
                            juce::Justification::centred);
            }
            if (nk == 0)
            {
                g.setColour (theme::textMute.withAlpha (dim ? 0.35f : 0.6f));
                g.setFont (theme::mono (7.0f));
                g.drawText ("default", d.withTrimmedTop (14.0f).toNearestInt(),
                            juce::Justification::centred);
            }
            x += (float) deviceW + 6.0f; ++col; ++shown;
        }
        if (shown < (int) chain.size())
        {
            g.setColour (theme::textDim);
            g.setFont (theme::mono (8.5f));
            g.drawText ("+" + juce::String ((int) chain.size() - shown),
                        (int) x + 2, (int) y + deviceH / 2 - 6, 26, 12,
                        juce::Justification::centredLeft);
        }
        if (kind == Kind::master)   // masterGainDb: the one post-chain fader (keep 0 law)
        {
            const float fy = body.getY() + (float) (deviceRows ((int) body.getWidth() + 18) * (deviceH + 5)) + 4.0f;
            auto slot = juce::Rectangle<float> (body.getX(), fy + 4.0f, body.getWidth() - 64.0f, 5.0f);
            const bool hot = std::abs (gainDb) > 0.01;
            g.setColour (theme::inset);
            g.fillRoundedRectangle (slot, 2.5f);
            const float fx = juce::jmap (juce::jlimit (-24.0f, 6.0f, (float) gainDb),
                                         -24.0f, 6.0f, slot.getX() + 3.0f, slot.getRight() - 3.0f);
            g.setColour ((hot ? theme::warn : tint).withAlpha (0.95f));
            g.fillRoundedRectangle (fx - 2.6f, slot.getY() - 3.0f, 5.2f, 11.0f, 2.0f);
            g.setColour (hot ? theme::warn : theme::textDim);
            g.setFont (theme::mono (8.0f));
            g.drawText (gainLabel(), (int) slot.getRight() + 6, (int) fy, 60, 13,
                        juce::Justification::centredLeft);
        }
    }

    void paintSound (juce::Graphics& g, juce::Rectangle<float> body)
    {
        // the voice's FACE (PluginFaces skin) at chat scale — the same identity a
        // producer sees on the modal, never bare text (UI CHAT SPEC law)
        auto face = body.withHeight (juce::jmax (26.0f, body.getHeight() - 3.0f));
        {
            juce::Graphics::ScopedSaveState ss (g);
            juce::Path clip;
            clip.addRoundedRectangle (face.getX(), face.getY(), face.getWidth(),
                                      face.getHeight(), 5.0f);
            g.reduceClipRegion (clip);
            const auto skin = faces::skinFor (srcId.isNotEmpty() ? srcId : summary);
            faces::paintBackdrop (g, face, skin, 0);
            g.setGradientFill ({ skin.hot.withAlpha (0.16f), face.getTopLeft(),
                                 skin.cool.withAlpha (0.05f), face.getBottomRight(), false });
            g.fillRect (face);
            g.setColour (skin.hot.withAlpha (0.248f));
            g.drawRoundedRectangle (face.reduced (0.5f), 5.0f, 1.0f);
            g.setColour (theme::text.withAlpha (0.94f));
            g.setFont (theme::ui (10.5f, juce::Font::bold));
            g.drawText (srcId.isNotEmpty() ? srcId : summary,
                        face.reduced (8.0f, 0.0f).toNearestInt(),
                        juce::Justification::centredLeft);
            g.setColour (skin.hot.brighter (0.2f).withAlpha (0.9f));
            g.setFont (theme::caps (6.5f));
            g.drawText (skin.family.toUpperCase(),
                        face.reduced (8.0f, 3.0f).toNearestInt(),
                        juce::Justification::topRight);
            if (srcPreset.isNotEmpty())
            {
                g.setColour (theme::textDim.withAlpha (0.9f));
                g.setFont (theme::mono (7.5f));
                g.drawText (srcPreset.fromLastOccurrenceOf ("/", false, false),
                            face.reduced (8.0f, 2.0f).toNearestInt(),
                            juce::Justification::bottomLeft);
            }
            // THE PATTERN DNA (Chezy's bare-drum-card gap): a knobless voice shows
            // WHAT IT PLAYS — its notes as a constellation (beat x pitch, vel = light)
            if (srcParams.empty() && ! dna.empty() && face.getHeight() > 36.0f)
            {
                auto band = face.reduced (8.0f, 4.0f).withTrimmedTop (14.0f);
                float pLo = 127.0f, pHi = 0.0f;
                for (auto& d : dna) { pLo = juce::jmin (pLo, d.p); pHi = juce::jmax (pHi, d.p); }
                const float span = juce::jmax (1.0f, dnaSpan);
                const float pr   = juce::jmax (1.0f, pHi - pLo);
                g.setColour (skin.hot.withAlpha (0.10f));          // the beat grid, faint
                for (float bb = 0.0f; bb <= span; bb += 4.0f)
                    g.drawVerticalLine ((int) (band.getX() + band.getWidth() * (bb / span)),
                                        band.getY(), band.getBottom());
                for (auto& d : dna)
                {
                    const float dx = band.getX() + band.getWidth() * (d.s / span);
                    const float dy = band.getBottom() - band.getHeight() * ((d.p - pLo) / pr);
                    g.setColour (skin.hot.withAlpha (0.30f + 0.55f * juce::jlimit (0.0f, 1.0f, d.v)));
                    g.fillEllipse (dx - 1.1f, dy - 1.1f, 2.2f, 2.2f);
                }
            }
            // THE SYNTH FACE (the ULTRATHINK "GRITTY BASS SYNTH" component): a voice
            // that carries knobs shows them — hero params first — the same FaceKnob
            // language as the fx rack + the plugin modal, not a bare name
            if (! srcParams.empty() && face.getHeight() > 40.0f)
            {
                static const char* prio[] = { "cutoff", "filter", "reso", "res", "env",
                                              "osc", "amp gain", "gain", "drive", "detune",
                                              "mix", "attack", "release", "pan" };
                std::vector<std::pair<juce::String, float>> ks;
                for (auto* k : prio)
                {
                    for (auto& pr : srcParams)
                        if (pr.first.toLowerCase().contains (k)
                            && std::none_of (ks.begin(), ks.end(),
                                             [&] (auto& e) { return e.first == pr.first; }))
                        { ks.push_back (pr); break; }
                    if (ks.size() == 4) break;
                }
                for (auto& pr : srcParams) { if (ks.size() >= 4) break;
                    if (std::none_of (ks.begin(), ks.end(), [&] (auto& e) { return e.first == pr.first; }))
                        ks.push_back (pr); }
                const auto tint = live() ? theme::accentB : theme::accent;
                auto row = face.withTrimmedTop (14.0f).reduced (8.0f, 3.0f);
                const int nk = (int) ks.size();
                for (int i = 0; i < nk; ++i)
                {
                    const float kx = row.getX() + row.getWidth() * ((float) i + 0.5f) / (float) nk;
                    const float ky = row.getCentreY() + 2.0f;
                    drawKnob (g, kx, ky, 9.0f, knobNorm (ks[(size_t) i].first, ks[(size_t) i].second),
                              tint, ! live() && verdict != 3);
                    g.setColour (theme::textMute.withAlpha (0.8f));
                    g.setFont (theme::mono (6.0f));
                    auto lbl = ks[(size_t) i].first.fromLastOccurrenceOf (" ", false, false);
                    g.drawText (lbl.substring (0, 8), (int) (kx - 22.0f), (int) (ky + 10.0f), 44, 8,
                                juce::Justification::centred);
                }
            }
        }
    }

    void paintMix (juce::Graphics& g, juce::Rectangle<float> body)
    {
        if (! hasMix) return;
        // the DAW's own hands (UI CHAT SPEC): a real fader + a real pan pot
        const auto tint = live() ? theme::accentB : theme::textMute;
        auto slot = juce::Rectangle<float> (body.getX() + 2.0f, body.getY() + 10.0f,
                                            body.getWidth() - 106.0f, 5.0f);
        g.setColour (theme::inset);
        g.fillRoundedRectangle (slot, 2.5f);
        for (float m = 0.0f; m <= 1.001f; m += 0.2f)       // dB ticks on the rail
        {
            g.setColour (juce::Colours::white.withAlpha (0.10f));
            g.fillRect (slot.getX() + slot.getWidth() * m, slot.getY() - 2.0f, 1.0f, 2.0f);
        }
        const float fx = juce::jmap (juce::jlimit (-24.0f, 6.0f, (float) gainDb),
                                     -24.0f, 6.0f, slot.getX() + 3.0f, slot.getRight() - 3.0f);
        g.setColour (tint.withAlpha (0.35f));               // cap glow
        g.fillRoundedRectangle (fx - 4.5f, slot.getY() - 5.5f, 9.0f, 16.0f, 3.0f);
        g.setColour (tint.brighter (0.2f));
        g.fillRoundedRectangle (fx - 3.0f, slot.getY() - 4.0f, 6.0f, 13.0f, 2.2f);
        g.setColour (theme::text.withAlpha (0.9f));
        g.setFont (theme::mono (8.5f));
        g.drawText (juce::String (gainDb, 1) + "dB",
                    (int) slot.getRight() + 6, (int) body.getY() + 3, 44, 14,
                    juce::Justification::centredLeft);
        drawKnob (g, body.getRight() - 26.0f, body.getY() + 12.0f, 8.0f,
                  (float) pan * 0.5f + 0.5f, tint, false);
        const auto panS = std::abs (pan) < 0.005 ? juce::String ("C")
                         : (pan < 0 ? "L" : "R") + juce::String ((int) std::round (std::abs (pan) * 50));
        g.setColour (theme::textMute.withAlpha (0.8f));
        g.setFont (theme::mono (6.2f));
        g.drawText ("pan " + panS, (int) body.getRight() - 46, (int) body.getY() + 22, 42, 9,
                    juce::Justification::centred);
    }

    void paintSends (juce::Graphics& g, juce::Rectangle<float> body)
    {
        if (sends.empty())
        {
            g.setColour (theme::textMute.withAlpha (0.5f));
            g.setFont (theme::mono (9.5f));
            g.drawText ("sends cleared", body.withHeight (15.0f).toNearestInt(),
                        juce::Justification::centredLeft);
            return;
        }
        // THE SEND ROUTING (not text): a labelled bar per aux send — the level fills
        // toward the bus name, the same send-strip language as the mixer's returns
        const auto tint = live() ? theme::accentB : theme::accent;
        float y = body.getY();
        for (size_t i = 0; i < sends.size() && i < 3; ++i)
        {
            auto& sd = sends[i];
            auto row = juce::Rectangle<float> (body.getX(), y, body.getWidth(), 14.0f);
            g.setColour (theme::inset.withAlpha (0.7f));
            g.fillRoundedRectangle (row, 3.0f);
            const float frac = juce::jmap (juce::jlimit (-30.0f, 6.0f, (float) sd.gainDb),
                                           -30.0f, 6.0f, 0.06f, 1.0f);
            g.setColour (tint.withAlpha (0.32f));
            g.fillRoundedRectangle (row.withWidth (row.getWidth() * frac), 3.0f);
            g.setColour (tint.withAlpha (0.85f));                    // the routing arrow
            g.fillEllipse (row.getX() + 4.0f, row.getCentreY() - 2.0f, 4.0f, 4.0f);
            g.setColour (theme::text.withAlpha (0.92f));
            g.setFont (theme::caps (7.5f));
            g.drawText ("-> " + sd.bus.toUpperCase(), row.withTrimmedLeft (12.0f).toNearestInt(),
                        juce::Justification::centredLeft);
            g.setColour (theme::textDim);
            g.setFont (theme::mono (7.5f));
            g.drawText (juce::String (sd.gainDb, 0) + " dB",
                        row.withTrimmedRight (5.0f).toNearestInt(), juce::Justification::centredRight);
            y += 16.0f;
        }
    }

    void paintMotion (juce::Graphics& g, juce::Rectangle<float> body, juce::Colour tint)
    {
        float y = body.getY();
        const int nShow = juce::jmin (2, (int) autos.size());
        g.setFont (theme::mono (8.5f));
        for (int i = 0; i < nShow; ++i)
        {
            auto& a = autos[autos.size() - (size_t) nShow + (size_t) i];   // newest last
            g.setColour (theme::text.withAlpha (0.8f));
            g.drawText (a.target + "  (" + juce::String ((int) a.points.size()) + " pts)",
                        (int) body.getX(), (int) y, (int) body.getWidth(), 13,
                        juce::Justification::centredLeft);
            y += 14.0f;
        }
        if (autos.empty())
        {
            g.setColour (theme::textMute.withAlpha (0.5f));
            g.drawText ("motion cleared", (int) body.getX(), (int) y, (int) body.getWidth(), 13,
                        juce::Justification::centredLeft);
            return;
        }
        // THE JOURNEY, DRAWN: the newest lane's curve as a strip (automation-motion law)
        auto& a = autos.back();
        if (a.points.size() < 2) return;
        auto strip = juce::Rectangle<float> (body.getX(), y + 2.0f, body.getWidth(), 16.0f);
        double b0 = a.points.front().beat, b1 = a.points.back().beat;
        double v0 = 1e18, v1 = -1e18;
        for (auto& p : a.points) { v0 = juce::jmin (v0, p.v); v1 = juce::jmax (v1, p.v); }
        if (b1 <= b0) b1 = b0 + 1.0;
        if (v1 <= v0) v1 = v0 + 1.0;
        juce::Path path;
        for (size_t i = 0; i < a.points.size(); ++i)
        {
            const float px = strip.getX() + (float) ((a.points[i].beat - b0) / (b1 - b0)) * strip.getWidth();
            const float py = strip.getBottom() - (float) ((a.points[i].v - v0) / (v1 - v0)) * strip.getHeight();
            if (i == 0) path.startNewSubPath (px, py); else path.lineTo (px, py);
            g.setColour (tint.withAlpha (0.85f));
            g.fillEllipse (px - 1.6f, py - 1.6f, 3.2f, 3.2f);
        }
        g.setColour (tint.withAlpha (0.65f));
        g.strokePath (path, { 1.3f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
    }

    void paintBuses (juce::Graphics& g, juce::Rectangle<float> body, juce::Colour tint)
    {
        if (buses.empty())
        {
            g.setColour (theme::textMute.withAlpha (0.5f));
            g.setFont (theme::mono (9.5f));
            g.drawText ("no buses", body.withHeight (15.0f).toNearestInt(), juce::Justification::centredLeft);
            return;
        }
        float y = body.getY();
        for (size_t i = 0; i < buses.size() && i < 3; ++i)
        {
            auto& b = buses[i];
            g.setColour (tint.brighter (0.1f).withAlpha (0.9f));
            g.setFont (theme::caps (8.0f));
            g.drawText (b.id.toUpperCase(), (int) body.getX(), (int) y, 52, 14, juce::Justification::centredLeft);
            juce::String fxs;
            for (auto& f : b.fx) fxs << (fxs.isEmpty() ? "" : " > ") << chipLabel (f);
            g.setColour (theme::text.withAlpha (0.78f));
            g.setFont (theme::mono (8.5f));
            g.drawText (fxs, (int) body.getX() + 54, (int) y, (int) body.getWidth() - 54, 14,
                        juce::Justification::centredLeft);
            y += 16.0f;
        }
    }

    void paintEars (juce::Graphics& g, juce::Rectangle<float> body)
    {
        const bool clean = earsClipped == 0;
        const char* names[] = { "peak dBFS", "clipped", "LUFS" };
        const juce::String vals[] = { juce::String (earsPeak, 1), juce::String (earsClipped),
                                      juce::String (earsLufs, 1) };
        const float cell = body.getWidth() / 3.0f;
        for (int i = 0; i < 3; ++i)
        {
            auto c = juce::Rectangle<float> (body.getX() + cell * (float) i, body.getY(), cell - 6.0f, 32.0f);
            g.setColour (theme::textMute);
            g.setFont (theme::ui (8.0f));
            g.drawText (names[i], c.toNearestInt(), juce::Justification::topLeft);
            g.setColour (i == 1 ? (clean ? theme::good : theme::bad) : theme::text);
            g.setFont (theme::mono (12.5f, juce::Font::bold));
            g.drawText (vals[i], c.withTrimmedTop (11.0f).toNearestInt(), juce::Justification::topLeft);
        }
    }

    // the entrance itself: age-eased alpha + a drift-and-settle transform. Bounds
    // stay the LAYOUT truth (the rail owns them); only the transform travels, so
    // a reflow mid-entrance never fights the animation. Idempotent at rest: the
    // last call past 430ms restores identity + full alpha (a minimised window
    // resuming mid-entrance heals on its first tick).
    void applyEntrance()
    {
        const float t = juce::jlimit (0.0f, 1.0f,
            (float) (juce::Time::getMillisecondCounter() - enterAt) / 420.0f);
        const float e = t * t * (3.0f - 2.0f * t);   // smoothstep
        setAlpha (e);
        if (t >= 1.0f) { setTransform ({}); repaint(); return; }
        const auto b = getBounds().toFloat();
        const float s = 0.955f + 0.045f * e;
        setTransform (juce::AffineTransform::scale (s, s, b.getCentreX(), b.getCentreY())
                        .translated (entFromX * (1.0f - e), 14.0f * (1.0f - e)));
        repaint();
    }

    static constexpr int deviceW = 104, deviceH = 54;  // one fx = one knob tile (wider: Chezy)
    Kind kind;
    bool selCard = false;
    juce::String tool, track, summary;
    int count = 1;
    int verdict = -1;                       // -1 live / 0 dissolved / 1 accepted / 2 rejected
    float breath = 0.0f;
    juce::uint32 enterAt = 0;               // MATERIALIZE birth tick (age-eased pose)
    float entFromX = 0.0f;
    juce::uint32 freshAt = 0, copiedAt = 0;

    // state copies (never pointers)
    std::vector<sotadaw::SongFx> chain;
    std::vector<sotadaw::SongBus> buses;
    std::vector<sotadaw::SongSend> sends;
    std::vector<sotadaw::SongAuto> autos;
    juce::String srcKind, srcId, srcPreset;
    std::map<juce::String, float> srcParams;   // the voice's set knobs (vst3/tweaked)
    struct DnaDot { float s = 0, p = 0, v = 0; };   // start / pitch / velocity
    std::vector<DnaDot> dna;                   // the track's PATTERN, on the face
    float dnaSpan = 0;                         // beats the dots cover
    double gainDb = 0, pan = 0;
    bool hasMix = false;
    juce::String earsWhich;
    double earsPeak = 0, earsLufs = 0;
    int earsClipped = 0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ActionCard)
};

//==============================================================================
// A wing of the agent console - AIR, not a panel (Chezy 2026-07-08): the rail
// draws NOTHING of its own. It is an invisible strip beside the centred chat
// where cards MATERIALIZE as the agent generates or the user selects; the stack
// floats up from the composer's eye-line (bottom-anchored), newest at the
// bottom, pinned like the chat (scroll law: never yank a reader).
class ActionRail : public juce::Component
{
public:
    enum class Side { left, right };

    explicit ActionRail (Side s) : side (s)
    {
        addAndMakeVisible (vp);
        vp.setViewedComponent (&content, false);
        vp.setScrollBarsShown (true, false);
        vp.setScrollBarThickness (4);        // a hairline; only overflow reveals it
    }

    ActionCard* addAction (ActionCard::Kind k, const juce::String& tool,
                           const juce::String& track, const juce::String& summary,
                           const sotadaw::Song& state)
    {
        // collapse law: the same tool hammering the same aspect grows ONE card
        if (! cards.isEmpty())
        {
            auto* last = cards.getLast();
            if (last->live() && last->cardKind() == k
                && last->toolName() == tool && last->trackName() == track)
            {
                last->bump (summary);
                last->retarget (state);
                layout();
                return last;
            }
        }
        auto* c = cards.add (new ActionCard (k, tool, track, summary));
        content.addAndMakeVisible (c);
        c->retarget (state);
        if (cards.size() > 48) { content.removeChildComponent (cards.getFirst()); cards.remove (0); }
        layout();
        // born at the column's edge, drifting outward into place (after layout:
        // the entrance transform pivots on the card's REST bounds)
        c->beginEntrance (side == Side::left ? 46.0f : -46.0f);
        return c;
    }

    void addEars (const juce::String& which, double peak, int clipped, double lufs)
    {
        auto* c = addAction (ActionCard::Kind::ears, "analyze", which, {}, sotadaw::Song());
        c->setEars (which, peak, clipped, lufs);
    }

    // THE WINGS ARE CONTEXTUAL (Chezy's initial spec, corrected 2026-07-07): they
    // show ONLY what the user SELECTS + what the agent GENERATES, never a full
    // dossier. LEFT: the selected track(s)' fx rack (or synth/voice face if bare);
    // RIGHT: the master desk + buses only when the master lane is the selection.
    // Agent-action cards (receipts) are untouched — selection cards are a separate,
    // rebuilt-on-change set.
    void setSelection (const sotadaw::Song& s, const std::set<int>& sel)
    {
        for (int i = cards.size(); --i >= 0;)          // drop the prior selection set
            if (cards[i]->fromSelection())
            {
                content.removeChildComponent (cards[i]);
                cards.remove (i);
            }
        if (side == Side::left)
        {
            for (int ti : sel)
            {
                if (ti < 0 || ti >= (int) s.tracks.size()) continue;
                auto& t = s.tracks[(size_t) ti];
                auto* c = addAction (t.fx.empty() ? ActionCard::Kind::sound
                                                  : ActionCard::Kind::fx,
                                     "selected", t.name,
                                     t.fx.empty() ? "selected voice" : "selected rack", s);
                c->markSelection();
            }
        }
        layout();
    }

    // the master lane was selected -> the RIGHT wing shows the master desk + buses
    void showMaster (const sotadaw::Song& s, bool on)
    {
        for (int i = cards.size(); --i >= 0;)
            if (cards[i]->fromSelection())
            { content.removeChildComponent (cards[i]); cards.remove (i); }
        if (on && side == Side::right)
        {
            auto* m = addAction (ActionCard::Kind::master, "selected", "master",
                                 "selected chain", s);
            m->markSelection();
            if (! s.buses.empty())
            {
                auto* b = addAction (ActionCard::Kind::buses, "selected", "buses", "returns", s);
                b->markSelection();
            }
        }
        layout();
    }

    void retargetAll (const sotadaw::Song& state)
    {
        bool any = false;
        for (auto* c : cards)
            if (c->live()) { c->retarget (state); any = true; }
        if (any) layout();   // chains grow chips: heights move
    }

    void freezeAll (int verdict)
    {
        for (auto* c : cards) c->freeze (verdict);
    }

    void tick()
    {
        if (! isShowing()) return;
        for (auto* c : cards) c->tick();
    }

    int cardCount() const { return cards.size(); }
    int liveCount() const
    {
        int n = 0;
        for (auto* c : cards) n += c->live() ? 1 : 0;
        return n;
    }

    // THE PATCHBAY TAPS (fable-uxwave 2026-07-11): the loom asks each wing which
    // cards are plug-worthy right now - the newest live/selection cards actually
    // on screen (viewport-clipped cards keep their cables coiled). Read-only; the
    // console converts card pointers to overlay space and hangs the wires.
    struct RailJack
    {
        juce::Component* card;
        juce::String track;
        ActionCard::Kind kind;
        bool live, selection;
    };
    std::vector<RailJack> railJacks (int maxN) const
    {
        std::vector<RailJack> out;
        const auto vis = vp.getViewArea().reduced (0, 4);
        for (int i = cards.size(); --i >= 0 && (int) out.size() < maxN;)
        {
            auto* c = cards[i];
            if (! c->wiredState()) continue;   // accepted MOTION/FX receipts stay wired
            // a wire exists only while its JACK CORNER is truly on screen — an
            // intersects() test let half-scrolled cards leave their plug floating
            // at the clip edge, and fully-scrolled cards plugged into the ROOM
            // (Chezy's "bass wire not connected" / "wire in the middle", 2026-07-11)
            const auto bb = c->getBounds();
            const juce::Point<int> jack (side == Side::left ? bb.getX() + 4
                                                            : bb.getRight() - 4,
                                         bb.getBottom() - 12);
            if (! vis.contains (jack)) continue;
            out.push_back ({ c, c->trackName(), c->cardKind(), c->live(),
                             c->fromSelection() });
        }
        return out;
    }

    void resized() override
    {
        vp.setBounds (getLocalBounds());     // AIR: no header band, the whole wing is sky
        layout();
    }

    // NO paint(): the wing is invisible - the page shows through until a card lands.

private:
    void layout()
    {
        const int w = juce::jmax (60, vp.getWidth() - 8);
        const int wasBottom = vp.getViewPositionY() + vp.getHeight();
        const bool follow = content.getHeight() <= vp.getHeight()
                            || wasBottom >= content.getHeight() - 80;
        int total = 0;                       // the stack floats up from the composer
        for (auto* c : cards) total += c->preferredHeight (w) + 10;
        int y = juce::jmax (4, vp.getHeight() - 4 - total);
        for (auto* c : cards)
        {
            const int hh = c->preferredHeight (w);
            c->setBounds (0, y, w, hh);
            y += hh + 10;
        }
        content.setSize (w + 8, juce::jmax (y, vp.getHeight()));
        if (follow)
            vp.setViewPosition (0, juce::jmax (0, content.getHeight() - vp.getHeight()));
    }

    Side side;
    juce::Component content;
    juce::Viewport vp;
    juce::OwnedArray<ActionCard> cards;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ActionRail)
};
