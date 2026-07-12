// ChatPanel.h - the agent conversation surface. Extracted from ui_main.cpp so
// the uismoke rig can PAINT it: the chat is styled by eyes, not by faith.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

//==============================================================================
// Agent chat — Cursor/Claude-Code language: user cards right, agent cards left,
// tool calls as pills, status as thin centered lines. Replaces the raw text log.
class ChatPanel : public juce::Component, private juce::Timer
{
public:
    // action = THE ACTION STREAM: one structured agent tool-call, streamed the
    // instant its tool_use block lands — a DAW component (family glyph + summary
    // + target track), never prose. meta = [family, tool, track, colourHex].
    enum class Kind { user, agent, tool, action, status, error, proposal, analysis, perception, report, live, variants };
    struct Msg { Kind kind; juce::String text; juce::StringArray meta; float h = 20.0f;
                 bool expanded = false; bool wasStream = false; bool wasThink = false;
                 std::vector<float> peaks;
                 // THE CHAT IS A DAW: a live component rides the transcript (Kind::live).
                 // The panel owns its lifetime + flow position; the host keeps the raw
                 // pointer to retarget/freeze it and hears onLiveGone when pruned.
                 std::unique_ptr<juce::Component> live; int liveH = 0; };
    std::function<void()> onAudition, onAccept, onReject;   // proposal-card buttons
    std::function<void()> onPlayTake;                       // #17: EARS card ▶ = hear what it measured
    std::function<void (const juce::String&)> onSuggest;    // empty-state starter chips -> prompt box
    // #21c BLIND ROUND: variants card. meta stride 4 = [label, wav, lufs, peak]
    // per take; text empty while open, the picked LABEL once decided (card dims,
    // pick chips retire). Play passes the wav path, pick passes the label.
    std::function<void (const juce::String&)> onPlayVariant, onPickVariant;

    ChatPanel()
    {
        addAndMakeVisible (vp);
        vp.setViewedComponent (&content, false);
        vp.setScrollBarsShown (true, false);
        content.owner = this;
        // CC3-5 scroll law: the jump pill appears when the user has scrolled up and
        // new messages land below — never yank, always offer the way back.
        addChildComponent (jumpBtn);
        // pin transitions are USER-driven ONLY: geometry churn (the F4 morph
        // re-wraps text and re-measures totals) must never strand the pill
        vp.onUserScroll = [this]
        {
            const bool pin = content.getHeight() - (vp.getViewPositionY() + vp.getHeight()) <= 100;
            if (pin == pinnedToBottom) return;
            pinnedToBottom = pin;
            jumpBtn.setVisible (! pin);
        };
        jumpBtn.onClick = [this] { pinnedToBottom = true; jumpBtn.setVisible (false);
                                   vp.autoMove = true;
                                   vp.setViewPosition (0, juce::jmax (0, content.getHeight() - vp.getHeight()));
                                   vp.autoMove = false; };
        startTimerHz (24);             // animates the composing dots + underline shimmer while busy
    }

    void add (Kind k, juce::String text, juce::StringArray meta = {})
    {
        // strings arrive from many sources (agent JSON, C literals) — normalise the
        // usual UTF-8 punctuation so a stray codepage can never mojibake the chat
        text = text.replace (juce::String::fromUTF8 ("\xe2\x80\xa6"), "...")
                   .replace (juce::String::fromUTF8 ("\xe2\x80\x94"), " - ")
                   .replace (juce::String::fromUTF8 ("\xe2\x80\x93"), "-");
        text = text.trim();   // ** and ` now RENDER (appendInline) - the old strip hid them
        if (text.isEmpty() && k != Kind::variants) return;   // #21c: an OPEN round card's
                                                             // text is empty BY DESIGN
                                                             // (it becomes the picked label)
        // TOKEN STREAM fold (pass 5, hardened 2026-07-11): the block-complete
        // reply REPLACES its own live-typing card - the final lands where it
        // typed, never a twin. The card is rarely msgs.back() by then (cost
        // lines and action pills land between the last delta and the final),
        // so scan a short tail window - Chezy's doubled-final screenshot.
        if (k == Kind::agent)
        {
            const int window = juce::jmin (8, (int) msgs.size());
            for (int back = 0; back < window; ++back)
            {
                auto& m = msgs[msgs.size() - 1 - (size_t) back];
                if (m.kind != Kind::agent || ! m.wasStream) continue;
                if (! (m.text == text || text.startsWith (m.text)
                       || m.text.startsWith (text)))
                    continue;
                const float old = m.h;
                if (text.length() >= m.text.length()) m.text = text;
                m.wasStream = false;
                m.wasThink  = false;
                streamOpen = false;
                measure (m, juce::jmax (60, vp.getWidth() - 12));
                totalH += m.h - old;
                pruneThinkTail();
                syncContent();
                return;
            }
            pruneThinkTail();   // reply landed fresh: reasoning breadcrumbs retire
        }
        if (k != Kind::status) streamOpen = false;   // real content ends the typing run
        // consecutive tool pills of the same name collapse into "xN"
        if (k == Kind::tool && ! msgs.empty() && msgs.back().kind == Kind::tool)
        {
            auto& last = msgs.back();
            const auto base = last.text.upToFirstOccurrenceOf ("  x", false, false);
            if (base == text)
            {
                const int n = last.text.contains ("  x") ? last.text.fromFirstOccurrenceOf ("  x", false, false).getIntValue() : 1;
                last.text = base + "  x" + juce::String (n + 1);
                content.repaint();
                return;
            }
        }
        // identical consecutive ACTIONS collapse too (a get_song storm is one card)
        if (k == Kind::action && ! msgs.empty() && msgs.back().kind == Kind::action
            && msgs.back().meta == meta
            && msgs.back().text.upToFirstOccurrenceOf ("  x", false, false) == text)
        {
            auto& last = msgs.back();
            const int n = last.text.contains ("  x")
                            ? last.text.fromFirstOccurrenceOf ("  x", false, false).getIntValue() : 1;
            last.text = text + "  x" + juce::String (n + 1);
            content.repaint();
            return;
        }
        // HEARTBEAT LADDER KILL (Chezy: "not a fat status log"): consecutive
        // compose/stream heartbeats collapse into ONE updating line — the 8-rung
        // "...composing (N min in), still streaming..." ladder becomes a single
        // quiet pulse, exactly the iteration-3 clean feel.
        auto isBeat = [] (const juce::String& t)
        { return t.containsIgnoreCase ("still streaming") || t.containsIgnoreCase ("composing")
              || t.containsIgnoreCase ("working"); };
        if (k == Kind::status && ! msgs.empty() && msgs.back().kind == Kind::status
            && isBeat (text) && isBeat (msgs.back().text))
        {
            msgs.back().text = text;
            content.repaint();
            return;
        }
        msgs.push_back ({ k, text, meta });
        if (msgs.size() > 400) { prune(); return; }
        // incremental: measure ONLY the new message (audio-friendly — no O(n) relayout per event)
        measure (msgs.back(), juce::jmax (60, vp.getWidth() - 12));
        totalH += msgs.back().h;
        syncContent();
    }
    void clear()
    {
        for (auto& m : msgs)
            if (m.live != nullptr && onLiveGone) onLiveGone (m.live.get());
        msgs.clear();
        streamOpen = false;
        relayout();
    }

    // TOKEN STREAM (pass 5): the agent's reply TYPES into ONE growing card.
    // Each call carries the full accumulated text (idempotent replace); the
    // matching block-complete add() folds into it above. A tool pill or any
    // other real content between deltas closes the run - the next delta opens
    // a fresh card (text blocks interleaved with tools read like the truth).
    void streamText (juce::String text, bool thinking = false)
    {
        text = text.replace (juce::String::fromUTF8 ("\xe2\x80\xa6"), "...")
                   .replace (juce::String::fromUTF8 ("\xe2\x80\x94"), " - ")
                   .replace (juce::String::fromUTF8 ("\xe2\x80\x93"), "-")
                   .trim();
        if (text.isEmpty()) return;
        if (streamOpen && ! msgs.empty() && msgs.back().kind == Kind::agent
            && msgs.back().wasStream)
        {
            auto& last = msgs.back();
            if (last.text == text) return;
            const float old = last.h;
            last.text = text;
            last.wasThink = thinking;      // prose takes the card over from the mind
            measure (last, juce::jmax (60, vp.getWidth() - 12));
            totalH += last.h - old;
            syncContent();
            return;
        }
        // a thinking pulse between tool pills REOPENS its card instead of
        // littering one per turn (fable redacts thinking - the pulse is a
        // climbing counter, one card per run is the whole story)
        if (thinking)
            for (int back = 0; back < juce::jmin (6, (int) msgs.size()); ++back)
            {
                auto& m = msgs[msgs.size() - 1 - (size_t) back];
                if (! m.wasThink) continue;
                const float old = m.h;
                m.text = text;
                measure (m, juce::jmax (60, vp.getWidth() - 12));
                totalH += m.h - old;
                syncContent();
                return;
            }
        Msg m { Kind::agent, text, {} };
        m.wasStream = true;
        m.wasThink = thinking;
        msgs.push_back (std::move (m));
        streamOpen = true;
        if (msgs.size() > 400) { prune(); return; }
        measure (msgs.back(), juce::jmax (60, vp.getWidth() - 12));
        totalH += msgs.back().h;
        syncContent();
    }

    int countKind (Kind k) const   // rig evidence: the transcript's census by kind
    {
        int n = 0;
        for (auto& m : msgs)
            if (m.kind == k) ++n;
        return n;
    }

    // LIVE CARDS (THE CHAT IS A DAW): mount a real component into the message flow.
    // It scrolls with the transcript, paints itself, takes its own mouse — the same
    // class that owns the stage, chat-sized. Returns the raw pointer for host wiring.
    std::function<void (juce::Component*)> onLiveGone;   // fired when pruning drops one
    juce::Component* addLive (std::unique_ptr<juce::Component> c, int contentH)
    {
        if (c == nullptr) return nullptr;
        Msg m { Kind::live, {}, {} };
        m.live = std::move (c);
        m.liveH = juce::jmax (40, contentH);
        auto* raw = m.live.get();
        content.addAndMakeVisible (raw);
        msgs.push_back (std::move (m));
        if (msgs.size() > 400) { prune(); return raw; }
        measure (msgs.back(), juce::jmax (60, vp.getWidth() - 12));
        totalH += msgs.back().h;
        syncContent();
        return raw;
    }
    void setLiveHeight (juce::Component* c, int contentH)   // responsive: cards re-fit the column
    {
        for (auto& m : msgs)
            if (m.live.get() == c)
            {
                if (m.liveH == juce::jmax (40, contentH)) return;
                const float old = m.h;
                m.liveH = juce::jmax (40, contentH);
                measure (m, juce::jmax (60, vp.getWidth() - 12));
                totalH += m.h - old;
                syncContent();
                return;
            }
    }

    // CHAT P2 (f124): the rendered take's WAVEFORM rides the proposal card —
    // the ears' evidence inline, not just buttons. Attaches to the newest
    // message of that kind; heights re-measure. #17: the EARS card wears the
    // same strip — it SHOWS the wav its ▶ pill plays.
    void setPeaksOn (Kind k, const std::vector<float>& p)
    {
        for (auto it = msgs.rbegin(); it != msgs.rend(); ++it)
            if (it->kind == k)
            {
                const float old = it->h;
                it->peaks = p;
                measure (*it, juce::jmax (60, vp.getWidth() - 12));
                totalH += it->h - old;
                syncContent();
                return;
            }
    }
    void setProposalPeaks (const std::vector<float>& p) { setPeaksOn (Kind::proposal, p); }

    // #21c: the blind verdict landed — the newest round card shows its pick and
    // retires its chips (the wavs are gone server-side; a dead ▶ would lie)
    void markVariantsPicked (const juce::String& label)
    {
        for (auto it = msgs.rbegin(); it != msgs.rend(); ++it)
            if (it->kind == Kind::variants) { it->text = label; break; }
        content.repaint();
    }

    // #21c camera hooks (SOTADAW_SNAP_BLIND): machine truth about the newest
    // round card + a click through the REAL hit-scan (hits fill during paint —
    // census after a shoot, never before)
    juce::String blindCensus() const
    {
        for (auto it = msgs.rbegin(); it != msgs.rend(); ++it)
            if (it->kind == Kind::variants)
            {
                int play = 0, pick = 0;
                for (auto& h : content.hits)
                {
                    if (h.action >= 20 && h.action < 28) ++play;
                    if (h.action >= 40 && h.action < 48) ++pick;
                }
                juce::StringArray labs;
                for (int i = 0; i + 3 < it->meta.size(); i += 4) labs.add (it->meta[i]);
                return "n=" + juce::String (it->meta.size() / 4)
                     + " labels=" + labs.joinIntoString (",")
                     + " picked=" + (it->text.isEmpty() ? "-" : it->text)
                     + " hitsPlay=" + juce::String (play)
                     + " hitsPick=" + juce::String (pick);
            }
        return "n=0";
    }
    bool clickAction (int action)
    {
        for (auto& h : content.hits)
            if (h.action == action)
            {
                const auto now = juce::Time::getCurrentTime();
                const juce::MouseEvent ev (juce::Desktop::getInstance().getMainMouseSource(),
                                           h.r.getCentre(), {}, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
                                           &content, &content, now, h.r.getCentre(), now, 1, false);
                content.mouseUp (ev);
                return true;
            }
        return false;
    }

    void toggleExpand (int idx)         // fold/unfold a long reply (also the smoke rig's probe)
    {
        if (idx < 0 || idx >= (int) msgs.size()) return;
        auto& m = msgs[(size_t) idx];
        m.expanded = ! m.expanded;
        const float old = m.h;
        measure (m, juce::jmax (60, vp.getWidth() - 12));
        totalH += m.h - old;
        syncContent();
    }

    juce::String headerInfo;            // right side of the panel header ("139 skills - KG online")
    bool agentBusy = false;             // pulses the status dot
    bool agentDead = false;             // sidecar gone: red dot + auto-restart note
    // THE PAGE IS THE CHAT (Chezy 2026-07-08): in agent mode the panel sheds its
    // body - no fill, no border, no header strip. The transcript floats straight
    // on the console; liveness becomes a floating glass pill (state as material).
    bool frameless = false;
    bool pinnedForRig() const { return pinnedToBottom; }
    bool pillOnForRig() const { return jumpBtn.isVisible(); }
    void userScrollForRig (int y) { vp.setViewPosition (0, y); }   // autoMove OFF = a user act

    void resized() override
    {
        vp.autoMove = true;
        vp.setBounds (getLocalBounds().withTrimmedTop (frameless ? 4 : 32));
        jumpBtn.setBounds (getWidth() - 106, getHeight() - 32, 92, 22);   // off the reading line
        relayout();
        vp.autoMove = false;
    }
    void paint (juce::Graphics& g) override
    {
        if (frameless) return;          // the page carries the chrome now
        auto r = getLocalBounds().toFloat();
        g.setColour (theme::panel);
        g.fillRoundedRectangle (r, 12.0f);
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawRoundedRectangle (r.reduced (0.5f), 12.0f, 1.0f);
        // header: agent identity strip
        auto h = getLocalBounds().removeFromTop (32).toFloat();
        g.setColour (theme::panelHi.withAlpha (0.6f));
        g.fillRoundedRectangle (h.reduced (1.0f, 1.0f).withTrimmedBottom (-6.0f).withHeight (31.0f), 11.0f);
        g.setGradientFill (theme::brand ({ h.getX() + 1.0f, h.getBottom() - 2.0f,
                                            h.getWidth() - 2.0f, 2.0f }, 0.5f));
        g.fillRect (h.getX() + 1.0f, h.getBottom() - 1.5f, h.getWidth() - 2.0f, 1.5f);
        theme::spark (g, { h.getX() + 12.0f, h.getCentreY() - 6.0f, 12.0f, 12.0f }, theme::agent);
        g.setColour (theme::text);
        g.setFont (theme::ui (12.0f, juce::Font::bold));
        g.drawText ("PRODUCER AGENT", (int) h.getX() + 32, (int) h.getY(), 130, (int) h.getHeight(),
                    juce::Justification::centredLeft);
        g.setColour (agentDead ? theme::bad : agentBusy ? theme::warn : theme::good);
        g.fillEllipse (h.getX() + 165.0f, h.getCentreY() - 3.0f, 6.0f, 6.0f);
        if (agentDead)
        {
            g.setColour (theme::bad.withAlpha (0.9f));
            g.setFont (theme::ui (10.0f, juce::Font::bold));
            g.drawText ("OFFLINE - restarting", (int) h.getX() + 176, (int) h.getY(), 120,
                        (int) h.getHeight(), juce::Justification::centredLeft);
        }
        if (agentBusy && ! agentDead)
        {
            // the underline comes alive: a comet of light sweeps the brand strip
            const float sweep = (float) (juce::Time::getMillisecondCounter() % 1400) / 1400.0f;
            const float sx = h.getX() + sweep * (h.getWidth() + 90.0f) - 20.0f;
            const float tail = juce::jmin (70.0f, sx - h.getX() - 1.0f);
            if (tail > 2.0f)
            {
                g.setGradientFill ({ juce::Colours::transparentWhite, sx - tail, 0.0f,
                                     juce::Colours::white.withAlpha (0.55f), sx, 0.0f, false });
                g.fillRect (sx - tail, h.getBottom() - 1.5f,
                            juce::jmin (tail, h.getRight() - 1.0f - (sx - tail)), 1.5f);
            }
            // the living indicator: "composing" + walking dots, right-aligned
            g.setColour (theme::warn.withAlpha (0.92f));
            g.setFont (theme::ui (10.0f, juce::Font::bold));
            g.drawText ("composing", h.toNearestInt().reduced (12, 0).removeFromRight (92).removeFromLeft (60),
                        juce::Justification::centredLeft);
            const int ph = (int) (juce::Time::getMillisecondCounter() / 250) % 3;
            for (int i = 0; i < 3; ++i)
            {
                g.setColour (theme::warn.withAlpha (i == ph ? 0.95f : 0.30f));
                g.fillEllipse (h.getRight() - 38.0f + 9.0f * (float) i, h.getCentreY() - 1.5f, 4.0f, 4.0f);
            }
        }
        else
        {
            g.setColour (theme::textMute);
            g.setFont (theme::ui (10.0f));
            g.drawText (headerInfo, h.toNearestInt().reduced (12, 0), juce::Justification::centredRight);
        }
    }

    void paintOverChildren (juce::Graphics& g) override
    {
        if (! frameless) return;
        // scrolled history dissolves at the page's top edge - depth, never a clip
        if (vp.getViewPositionY() > 4)
        {
            auto top = getLocalBounds().toFloat().withHeight (26.0f);
            g.setGradientFill ({ juce::Colour (0xff0a0b12).withAlpha (0.85f), top.getTopLeft(),
                                 juce::Colour (0xff0a0b12).withAlpha (0.0f),  top.getBottomLeft(), false });
            g.fillRect (top);
        }
        if (! agentBusy && ! agentDead) return;
        // THE LIVENESS PILL: a floating glass chip, top-centre of the column -
        // the frameless page's only status material (never a banner strip)
        const auto tint = agentDead ? theme::bad : theme::warn;
        const juce::String word = agentDead ? "OFFLINE - restarting" : "composing";
        const float tw = theme::measure (theme::ui (10.0f, juce::Font::bold), word);
        const float pw = tw + (agentDead ? 34.0f : 60.0f);
        juce::Rectangle<float> pill ((float) getWidth() * 0.5f - pw * 0.5f, 6.0f, pw, 22.0f);
        g.setColour (juce::Colour (0xff0c0e15).withAlpha (0.82f));
        g.fillRoundedRectangle (pill, 11.0f);
        g.setColour (juce::Colours::white.withAlpha (0.035f));
        g.fillRoundedRectangle (pill, 11.0f);
        g.setColour (tint.withAlpha (0.45f));
        g.drawRoundedRectangle (pill.reduced (0.5f), 11.0f, 1.0f);
        theme::spark (g, { pill.getX() + 8.0f, pill.getCentreY() - 5.0f, 10.0f, 10.0f },
                      theme::agent.withAlpha (0.9f));
        g.setColour (tint.withAlpha (0.95f));
        g.setFont (theme::ui (10.0f, juce::Font::bold));
        g.drawText (word, pill.withTrimmedLeft (23.0f).toNearestInt(),
                    juce::Justification::centredLeft);
        if (! agentDead)
        {
            const int ph = (int) (juce::Time::getMillisecondCounter() / 250) % 3;
            for (int i = 0; i < 3; ++i)
            {
                g.setColour (theme::warn.withAlpha (i == ph ? 0.95f : 0.30f));
                g.fillEllipse (pill.getRight() - 32.0f + 8.0f * (float) i,
                               pill.getCentreY() - 2.0f, 4.0f, 4.0f);
            }
        }
    }

private:
    void pruneThinkTail()   // thinking cards are scaffolding: they leave when the reply lands
    {
        bool removed = false;
        for (int i = (int) msgs.size(); --i >= 0 && i >= (int) msgs.size() - 12;)
            if (msgs[(size_t) i].wasThink)
            {
                totalH -= msgs[(size_t) i].h;
                msgs.erase (msgs.begin() + i);
                removed = true;
            }
        if (removed) syncContent();
    }

    void prune()   // the oldest 100 leave; live cards announce their death first
    {
        for (auto it = msgs.begin(); it != msgs.begin() + 100; ++it)
            if (it->live != nullptr && onLiveGone) onLiveGone (it->live.get());
        msgs.erase (msgs.begin(), msgs.begin() + 100);
        relayout();
    }

    void timerCallback() override
    {
        // busy animates (shimmer + dots) at full rate; dead is a STATIC banner — a
        // 2 Hz touch is enough to catch the host flipping the flag without a repaint
        if (agentBusy || (agentDead && ++deadTick % 12 == 0)) repaint (0, 0, getWidth(), 32);
        if (content.flashIdx != -1 && juce::Time::getMillisecondCounter() - content.flashAt <= 1300)
            content.repaint();
        else if (content.flashIdx != -1)
        {
            content.flashIdx = -1;
            content.repaint();
        }
    }

    struct Content : public juce::Component
    {
        ChatPanel* owner = nullptr;
        float topOffset = 0.0f;         // bottom-anchor: few messages sit by the composer, not in a void
        struct Hit { juce::Rectangle<float> r; int action; };
        std::vector<Hit> hits;
        int flashIdx = -1;              // click-to-copy feedback
        juce::uint32 flashAt = 0;
        int hoverAction = -1;           // buttons/chips light under the mouse

        void mouseMove (const juce::MouseEvent& e) override
        {
            int h = -1;
            for (auto& hh : hits)
                if ((hh.action < 100 || hh.action >= 500) && hh.r.contains (e.position)) { h = hh.action; break; }
            if (h != hoverAction) { hoverAction = h; repaint(); }
        }
        void mouseExit (const juce::MouseEvent&) override
        {
            if (hoverAction != -1) { hoverAction = -1; repaint(); }
        }

        void mouseUp (const juce::MouseEvent& e) override
        {
            if (e.mods.isPopupMenu())   // right-click: the whole conversation as text
            {
                juce::String all;
                for (auto& m : owner->msgs)
                {
                    if (m.kind == Kind::live) continue;   // components aren't text
                    all << (m.kind == Kind::user ? "you: " : m.kind == Kind::tool ? "  tool: "
                            : m.kind == Kind::action ? "  act: "
                            : m.kind == Kind::error ? "ERROR: " : m.kind == Kind::proposal ? "PROPOSAL: " : "agent: ")
                        << m.text << "\n";
                }
                juce::SystemClipboard::copyTextToClipboard (all);
                flashIdx = -2; flashAt = juce::Time::getMillisecondCounter();
                repaint();
                return;
            }
            for (auto& h : hits)
                if (h.r.contains (e.getPosition().toFloat()))
                {
                    if (h.action == 0 && owner->onAudition) owner->onAudition();
                    if (h.action == 1 && owner->onAccept)   owner->onAccept();
                    if (h.action == 2 && owner->onReject)   owner->onReject();
                    if (h.action == 3 && owner->onPlayTake) owner->onPlayTake();   // #17 ▶
                    if (h.action >= 20 && h.action < 48)   // #21c blind round: ▶ take / PICK
                        for (auto it = owner->msgs.rbegin(); it != owner->msgs.rend(); ++it)
                            if (it->kind == Kind::variants)
                            {
                                if (it->text.isEmpty())    // an open round only
                                {
                                    const bool pick = h.action >= 40;
                                    const int s = (h.action - (pick ? 40 : 20)) * 4;
                                    if (s + 3 < it->meta.size())
                                    {
                                        if (pick && owner->onPickVariant)        owner->onPickVariant (it->meta[s]);
                                        if (! pick && owner->onPlayVariant)      owner->onPlayVariant (it->meta[s + 1]);
                                    }
                                }
                                break;
                            }
                    static const char* starters[] = { "make the drop hit harder and darker",
                                                      "hum a topline over the lead",
                                                      "tighten the mix - kick and bass are fighting",
                                                      "double the hook an octave up, quieter" };
                    if (h.action >= 10 && h.action < 14 && owner->onSuggest)
                        owner->onSuggest (starters[h.action - 10]);
                    if (h.action >= 500)   // fold/unfold a long reply
                    {
                        owner->toggleExpand (h.action - 500);
                        return;
                    }
                    if (h.action >= 100)   // click a message = COPY it (chat text isn't web text)
                    {
                        juce::SystemClipboard::copyTextToClipboard (owner->msgs[(size_t) (h.action - 100)].text);
                        flashIdx = h.action - 100;
                        flashAt = juce::Time::getMillisecondCounter();
                        repaint();
                    }
                    return;
                }
        }

        void drawCopied (juce::Graphics& g, juce::Rectangle<float> card, int idx)
        {
            if (idx != flashIdx || juce::Time::getMillisecondCounter() - flashAt > 1100) return;
            auto chip = juce::Rectangle<float> (card.getRight() - 58.0f, card.getY() - 8.0f, 54.0f, 16.0f);
            g.setColour (theme::good.withAlpha (0.92f));
            g.fillRoundedRectangle (chip, 8.0f);
            g.setColour (theme::inset);
            g.setFont (theme::ui (9.5f, juce::Font::bold));
            g.drawText ("copied", chip.toNearestInt(), juce::Justification::centred);
        }

        void paint (juce::Graphics& g) override
        {
            hits.clear();
            if (flashIdx == -2 && juce::Time::getMillisecondCounter() - flashAt <= 1100)
            {
                // ride the VISIBLE top (content y=2 scrolls offscreen on long threads)
                // and wear pill material — never naked text over a live row
                const auto tf = theme::ui (10.5f, juce::Font::bold);
                const float tw2 = theme::measure (tf, "conversation copied") + 26.0f;
                juce::Rectangle<float> pill ((float) getWidth() * 0.5f - tw2 * 0.5f,
                                             (float) owner->vp.getViewPositionY() + 4.0f,
                                             tw2, 18.0f);
                g.setColour (theme::inset.withAlpha (0.94f));
                g.fillRoundedRectangle (pill, 9.0f);
                g.setColour (theme::good.withAlpha (0.55f));
                g.drawRoundedRectangle (pill.reduced (0.5f), 9.0f, 1.0f);
                g.setColour (theme::good.withAlpha (0.95f));
                g.setFont (tf);
                g.drawText ("conversation copied", pill.toNearestInt(), juce::Justification::centred);
            }
            const int w = getWidth();
            // THE COACH IS AN EMPTY-STATE, NOT A SPACE-FILLER (Chezy live 2026-07-10:
            // the hero + starter chips painted into the void ABOVE a bottom-anchored
            // live conversation — chips landed on real rows and their hit-rects stayed
            // CLICKABLE over messages). State gates the coach: it exists only while
            // the transcript is empty; geometry only sizes it.
            if (owner->msgs.empty() && topOffset > 90.0f)
            {
                const float cx = (float) w * 0.5f, cy = topOffset * 0.5f;
                g.setColour (theme::agent.withAlpha (0.05f));                  // aura rings
                g.fillEllipse (cx - 44.0f, cy - 57.0f, 88.0f, 88.0f);
                g.setColour (theme::agent.withAlpha (0.09f));
                g.fillEllipse (cx - 28.0f, cy - 41.0f, 56.0f, 56.0f);
                theme::spark (g, { cx - 15.0f, cy - 28.0f, 30.0f, 30.0f }, theme::agent.withAlpha (0.55f));
                g.setColour (theme::text.withAlpha (0.75f));
                g.setFont (theme::ui (12.5f, juce::Font::bold));
                g.drawText ("tell the producer what to change", 0, (int) cy + 14, w, 16, juce::Justification::centred);
                g.setColour (theme::textMute.withAlpha (0.7f));
                g.setFont (theme::ui (10.0f));
                g.drawText ("drag a track, groove, or preset here to give it context", 0, (int) cy + 32, w, 14,
                            juce::Justification::centred);
                if (topOffset > 320.0f)   // chips only when ALL FOUR fit: their bottom
                {                         // (topOffset/2 + 180) must clear the viewport
                                          // (~topOffset + 20 when empty) -> t >= 320
                    static const char* starters[] = { "make the drop hit harder and darker",
                                                      "hum a topline over the lead",
                                                      "tighten the mix - kick and bass are fighting",
                                                      "double the hook an octave up, quieter" };
                    float sy = cy + 60.0f;
                    g.setFont (theme::ui (11.0f));
                    for (int i = 0; i < 4; ++i)
                    {
                        const bool hov = hoverAction == 10 + i;
                        const auto tw = theme::measure (theme::ui (11.0f), starters[i]) + 30.0f;
                        juce::Rectangle<float> chip ((float) w * 0.5f - tw * 0.5f, sy, tw, 24.0f);
                        if (hov)
                        {
                            g.setGradientFill (theme::brand (chip, 0.18f));
                            g.fillRoundedRectangle (chip, 12.0f);
                        }
                        else
                        {
                            g.setColour (theme::accent.withAlpha (0.07f));
                            g.fillRoundedRectangle (chip, 12.0f);
                        }
                        g.setColour (theme::accent.withAlpha (hov ? 0.65f : 0.35f));
                        g.drawRoundedRectangle (chip.reduced (0.5f), 12.0f, 1.0f);
                        g.setColour (hov ? theme::text : theme::textDim);
                        g.drawText (starters[i], chip.toNearestInt(), juce::Justification::centred);
                        hits.push_back ({ chip, 10 + i });
                        sy += 32.0f;
                    }
                }
            }
            float y = 8.0f + topOffset;
            for (auto& m : owner->msgs)
            {
                const float cardW = w - 20.0f;
                if (m.kind == Kind::live)
                {
                    // the card paints itself (a child in the flow); the panel gives it
                    // elevation + the agent's gutter mark so the thread reads as one hand
                    juce::Rectangle<float> card (24.0f, y + 4.0f, (float) w - 34.0f, m.h - 12.0f);
                    g.setColour (juce::Colours::black.withAlpha (0.20f));
                    g.fillRoundedRectangle (card.translated (0.0f, 2.5f).expanded (1.5f), 11.0f);
                    g.setColour (theme::agent.withAlpha (0.16f));
                    g.fillEllipse (4.0f, y + 5.0f, 16.0f, 16.0f);
                    theme::spark (g, { 8.0f, y + 9.0f, 8.0f, 8.0f }, theme::agent);
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::proposal)
                {
                    juce::AttributedString as;
                    as.append (m.text, theme::ui (12.0f), theme::text);
                    juce::TextLayout tl;
                    tl.createLayout (as, cardW - 28.0f);
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 10.0f);
                    theme::card (g, card, theme::panelHi, 9.0f);
                    g.setColour (theme::good.withAlpha (0.55f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.2f);
                    // header band
                    auto band = card.withHeight (24.0f);
                    g.setGradientFill ({ theme::good.withAlpha (0.22f), band.getTopLeft(),
                                         theme::good.withAlpha (0.02f), band.getTopRight(), false });
                    juce::Path bp; bp.addRoundedRectangle (band.getX(), band.getY(), band.getWidth(), band.getHeight(),
                                                           9.0f, 9.0f, true, true, false, false);
                    g.fillPath (bp);
                    g.setColour (theme::good);
                    g.fillEllipse (band.getX() + 10.0f, band.getCentreY() - 3.0f, 6.0f, 6.0f);
                    g.setFont (theme::ui (10.0f, juce::Font::bold));
                    g.drawText ("PROPOSAL", band.reduced (24, 0).toNearestInt(), juce::Justification::centredLeft);
                    g.setColour (theme::textMute);
                    g.setFont (theme::ui (9.5f));
                    g.drawText ("ghost notes on the canvas - audition, then decide",
                                band.reduced (24, 0).toNearestInt(), juce::Justification::centredRight);
                    float textTop = 22.0f;
                    if (! m.meta.isEmpty())   // MAKE proposals show their SHAPE: the section map
                    {
                        auto strip = card.withTrimmedTop (28.0f).withHeight (16.0f).reduced (12.0f, 0.0f);
                        const float segW = strip.getWidth() / (float) m.meta.size();
                        for (int i = 0; i < m.meta.size(); ++i)
                        {
                            juce::Rectangle<float> seg (strip.getX() + segW * (float) i, strip.getY(),
                                                        segW - 2.0f, strip.getHeight());
                            const auto c = theme::trackColour (i);
                            g.setColour (c.withAlpha (0.20f));
                            g.fillRoundedRectangle (seg, 4.0f);
                            g.setColour (c.withAlpha (0.85f));
                            g.fillRect (seg.getX() + 1.0f, seg.getBottom() - 2.0f, seg.getWidth() - 2.0f, 2.0f);
                            if (segW > 34.0f)
                            {
                                g.setColour (theme::text.withAlpha (0.85f));
                                g.setFont (theme::ui (8.5f, juce::Font::bold));
                                g.drawText (m.meta[i].toUpperCase().substring (0, 9), seg.toNearestInt(),
                                            juce::Justification::centred);
                            }
                        }
                        textTop = 48.0f;
                    }
                    if (! m.peaks.empty())
                    {
                        auto wr = card.withTrimmedTop (textTop + 2.0f).withHeight (24.0f).reduced (12.0f, 0.0f);
                        const float mid = wr.getCentreY();
                        const float cw = wr.getWidth() / (float) m.peaks.size();
                        for (size_t pi = 0; pi < m.peaks.size(); ++pi)
                        {
                            const float a = juce::jlimit (0.04f, 1.0f, m.peaks[pi]);
                            const float hh = a * 11.0f;
                            g.setColour (theme::accent.withAlpha (0.28f + 0.6f * a));
                            g.fillRect (wr.getX() + cw * (float) pi, mid - hh, juce::jmax (1.0f, cw - 1.0f), hh * 2.0f);
                        }
                        textTop += 30.0f;
                    }
                    tl.draw (g, card.reduced (14.0f, 8.0f).withTrimmedTop (textTop).withTrimmedBottom (38.0f));
                    // action row: Audition (outline) / Accept (filled) / Reject (outline)
                    auto btnRow = card.removeFromBottom (40.0f).reduced (10.0f, 6.0f);
                    const char* labels[] = { "Audition", "Accept", "Reject" };
                    const juce::Colour cols[] = { theme::accent, theme::good, theme::bad };
                    for (int b = 0; b < 3; ++b)
                    {
                        auto chip = btnRow.removeFromLeft (btnRow.getWidth() / (float) (3 - b)).reduced (3.0f, 0.0f);
                        const bool hov = hoverAction == b;
                        if (b == 1)
                        {
                            g.setColour (cols[b].withAlpha (hov ? 0.30f : 0.18f));
                            g.fillRoundedRectangle (chip.expanded (1.5f), 8.0f);
                            g.setColour (hov ? cols[b].brighter (0.12f) : cols[b]);
                            g.fillRoundedRectangle (chip, 7.0f);
                            g.setColour (juce::Colours::white.withAlpha (0.22f));
                            g.drawHorizontalLine ((int) chip.getY() + 1, chip.getX() + 5.0f, chip.getRight() - 5.0f);
                            g.setColour (theme::inset);
                        }
                        else
                        {
                            g.setColour (cols[b].withAlpha (hov ? 0.22f : 0.13f));
                            g.fillRoundedRectangle (chip, 7.0f);
                            g.setColour (cols[b].withAlpha (hov ? 1.0f : 0.8f));
                            g.drawRoundedRectangle (chip.reduced (0.5f), 7.0f, 1.2f);
                            g.setColour (theme::text);
                        }
                        g.setFont (theme::ui (12.0f, juce::Font::bold));
                        g.drawText (labels[b], chip, juce::Justification::centred);
                        hits.push_back ({ chip, b });
                    }
                    hits.push_back ({ card, 100 + (int) (&m - &owner->msgs[0]) });
                    drawCopied (g, card, (int) (&m - &owner->msgs[0]));
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::analysis)
                {
                    // EARS CARD (CC3-3): the numbers as meters, not prose. meta = which|peak|clipped|lufs
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 8.0f);
                    theme::card (g, card, theme::panelHi, 9.0f);
                    const bool clean = m.meta.size() > 2 && m.meta[2].getIntValue() == 0;
                    const auto edge = clean ? theme::good : theme::bad;
                    g.setColour (edge.withAlpha (0.45f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (edge);
                    g.setFont (theme::ui (9.5f, juce::Font::bold));
                    g.drawText ("EARS  " + (m.meta.isEmpty() ? juce::String() : m.meta[0].toUpperCase()),
                                card.reduced (12.0f, 6.0f).toNearestInt(), juce::Justification::topLeft);
                    const char* names[] = { "peak dBFS", "clipped", "LUFS" };
                    auto row = card.withTrimmedTop (22.0f).reduced (12.0f, 4.0f);
                    const float cell = row.getWidth() / 3.0f;
                    for (int i = 0; i < 3 && i + 1 < m.meta.size(); ++i)
                    {
                        auto c = juce::Rectangle<float> (row.getX() + cell * (float) i, row.getY(), cell - 8.0f, row.getHeight());
                        g.setColour (theme::textMute);
                        g.setFont (theme::ui (8.5f));
                        g.drawText (names[i], c.toNearestInt(), juce::Justification::topLeft);
                        g.setColour (i == 1 ? (clean ? theme::good : theme::bad) : theme::text);
                        g.setFont (theme::mono (13.0f, juce::Font::bold));
                        g.drawText (m.meta[i + 1], c.withTrimmedTop (11.0f).toNearestInt(), juce::Justification::topLeft);
                        if (i == 2)   // LUFS position bar, -24..0
                        {
                            const float v = juce::jlimit (-24.0f, 0.0f, m.meta[3].getFloatValue());
                            auto bar = c.withTrimmedTop (30.0f).withHeight (4.0f);
                            g.setColour (theme::inset);
                            g.fillRoundedRectangle (bar, 2.0f);
                            g.setColour (theme::accent);
                            g.fillRoundedRectangle (bar.withWidth (bar.getWidth() * (v + 24.0f) / 24.0f), 2.0f);
                        }
                    }
                    // #17 THE TRANSCRIPT PLAYS: the EARS card plays the render
                    // it measured — a ▶ pill top-right, riding the preview rail
                    if (owner->onPlayTake)
                    {
                        auto pb = juce::Rectangle<float> (card.getRight() - 32.0f,
                                                          card.getY() + 5.0f, 24.0f, 16.0f);
                        g.setColour (edge.withAlpha (0.22f));
                        g.fillRoundedRectangle (pb, 8.0f);
                        g.setColour (edge);
                        juce::Path tri;
                        tri.addTriangle (pb.getX() + 8.0f, pb.getY() + 3.5f,
                                         pb.getX() + 8.0f, pb.getBottom() - 3.5f,
                                         pb.getRight() - 7.0f, pb.getCentreY());
                        g.fillPath (tri);
                        hits.push_back ({ pb, 3 });
                    }
                    hits.push_back ({ card, 100 + (int) (&m - &owner->msgs[0]) });
                    drawCopied (g, card, (int) (&m - &owner->msgs[0]));
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::variants)
                {
                    // #21c BLIND ROUND CARD: N anonymous takes, each playable,
                    // one PICK crowns. meta stride 4 = [label, wav, lufs, peak];
                    // text = the picked label once decided (chips retire, card dims
                    // — the loser wavs are GONE server-side, a live ▶ would lie).
                    const int n = m.meta.size() / 4;
                    const bool picked = m.text.isNotEmpty();
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 8.0f);
                    theme::card (g, card, theme::panelHi, 9.0f);
                    const auto edge = picked ? theme::textMute : theme::accent;
                    g.setColour (edge.withAlpha (0.45f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (edge);
                    g.setFont (theme::ui (9.5f, juce::Font::bold));
                    g.drawText (picked ? "BLIND ROUND - PICKED " + m.text
                                       : "BLIND ROUND - listen, then PICK",
                                card.reduced (12.0f, 6.0f).toNearestInt(),
                                juce::Justification::topLeft);
                    for (int i = 0; i < n; ++i)
                    {
                        auto r = juce::Rectangle<float> (card.getX() + 10.0f,
                                                         card.getY() + 24.0f + 26.0f * (float) i,
                                                         card.getWidth() - 20.0f, 24.0f);
                        const bool winner = picked && m.meta[i * 4] == m.text;
                        const float dim = (picked && ! winner) ? 0.3f : 1.0f;
                        if (! picked)                       // ▶ pill (open rounds only)
                        {
                            auto pb = r.removeFromLeft (30.0f).reduced (2.0f, 4.0f);
                            g.setColour (theme::accent.withAlpha (hoverAction == 20 + i ? 0.4f : 0.18f));
                            g.fillRoundedRectangle (pb, 8.0f);
                            g.setColour (theme::accent);
                            juce::Path tri;
                            tri.addTriangle (pb.getCentreX() - 3.0f, pb.getCentreY() - 4.0f,
                                             pb.getCentreX() - 3.0f, pb.getCentreY() + 4.0f,
                                             pb.getCentreX() + 5.0f, pb.getCentreY());
                            g.fillPath (tri);
                            hits.push_back ({ pb, 20 + i });
                        }
                        else r.removeFromLeft (30.0f);
                        g.setColour ((winner ? theme::accent : theme::text).withAlpha (dim));
                        g.setFont (theme::mono (15.0f, juce::Font::bold));
                        g.drawText (m.meta[i * 4], r.removeFromLeft (26.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                        g.setColour (theme::textMute.withAlpha (dim));
                        g.setFont (theme::mono (10.5f));
                        g.drawText (m.meta[i * 4 + 2] + " LUFS   " + m.meta[i * 4 + 3] + " dBFS",
                                    r.withTrimmedRight (54.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                        if (! picked)                       // PICK chip
                        {
                            auto pk = r.removeFromRight (50.0f).reduced (2.0f, 3.0f);
                            g.setColour (theme::good.withAlpha (hoverAction == 40 + i ? 0.5f : 0.2f));
                            g.fillRoundedRectangle (pk, 9.0f);
                            g.setColour (theme::good);
                            g.setFont (theme::ui (10.0f, juce::Font::bold));
                            g.drawText ("PICK", pk.toNearestInt(), juce::Justification::centred);
                            hits.push_back ({ pk, 40 + i });
                        }
                        else if (winner)
                        {
                            g.setColour (theme::good);
                            g.setFont (theme::ui (10.0f, juce::Font::bold));
                            g.drawText ("-> proposal", r.removeFromRight (74.0f).toNearestInt(),
                                        juce::Justification::centredRight);
                        }
                    }
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::perception)
                {
                    // THE SOUND TENSOR CARD (CC3-4): the chat SHOWS what the agent hears.
                    // Mono rows, heat-tinted low->high (warm sub, cool air) — an image made of type.
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 8.0f);
                    theme::card (g, card, theme::inset, 9.0f);
                    g.setColour (theme::agent.withAlpha (0.5f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (theme::agent);
                    g.setFont (theme::ui (10.5f, juce::Font::bold));
                    g.drawText ("THE AGENT HEARS", card.reduced (12.0f, 6.0f).toNearestInt(),
                                juce::Justification::topLeft);
                    auto lines = juce::StringArray::fromLines (m.text);
                    // BIGGER + ADAPTIVE: the tensor fills the card width (see tensorRowH)
                    const float rowH = tensorRowH (cardW, m.text);
                    float ly = card.getY() + 24.0f;
                    g.setFont (theme::mono (rowH - 2.5f));
                    for (int i = 0; i < lines.size(); ++i)
                    {
                        const float t = lines.size() > 2 ? (float) (i - 1) / (float) juce::jmax (1, lines.size() - 2) : 0.0f;
                        const auto rowCol = i == 0 ? theme::textMute
                                            : juce::Colour::fromHSV (0.58f - 0.55f * (1.0f - t), 0.55f, 0.95f, 0.9f);
                        g.setColour (rowCol);
                        g.drawText (lines[i], (int) card.getX() + 13, (int) ly,
                                    (int) card.getWidth() - 26, (int) rowH,
                                    juce::Justification::centredLeft);
                        ly += rowH;
                    }
                    hits.push_back ({ card, 100 + (int) (&m - &owner->msgs[0]) });
                    drawCopied (g, card, (int) (&m - &owner->msgs[0]));
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::report)
                {
                    // REPORT CARD (CC4-I4): doctor/energy/verb outputs as a mono card —
                    // they were squashing into one clipped status line (pure console-feel).
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 8.0f);
                    theme::card (g, card, theme::inset, 9.0f);
                    g.setColour (theme::accentB.withAlpha (0.4f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    auto lines = juce::StringArray::fromLines (m.text);
                    juce::String head = lines.isEmpty() ? juce::String ("REPORT") : lines[0];
                    if (head.startsWith ("[") && head.contains ("]"))
                        head = head.substring (1).upToFirstOccurrenceOf ("]", false, false).toUpperCase();
                    g.setColour (theme::accentB);
                    g.setFont (theme::ui (9.5f, juce::Font::bold));
                    g.drawText (head, card.reduced (12.0f, 5.0f).toNearestInt(), juce::Justification::topLeft);
                    float ly = card.getY() + 20.0f;
                    g.setFont (theme::mono (10.0f));
                    for (int i = 0; i < lines.size(); ++i)
                    {
                        auto row = i == 0 ? lines[0].fromFirstOccurrenceOf ("] ", false, false) : lines[i];
                        g.setColour (row.contains ("PASS") || row.contains ("CLEAN") ? theme::good.withAlpha (0.9f)
                                     : row.contains ("FAIL") || row.contains ("[X1]") ? theme::warn
                                     : theme::textDim);
                        g.drawText (row, (int) card.getX() + 12, (int) ly, (int) card.getWidth() - 24, 13,
                                    juce::Justification::centredLeft);
                        ly += 13.0f;
                    }
                    hits.push_back ({ card, 100 + (int) (&m - &owner->msgs[0]) });
                    drawCopied (g, card, (int) (&m - &owner->msgs[0]));
                    y += m.h;
                    continue;
                }
                if (m.kind == Kind::status)
                {
                    // NO MORE LADDER (Chezy live): status is a quiet centered dim
                    // line — no full-width divider rungs. Runs of status now recede
                    // into a soft grey column; the rich cards own the eye. A divider
                    // returns ONLY when a status sits ALONE between two cards (a real
                    // scene break), never inside a run.
                    const int idx = (int) (&m - &owner->msgs[0]);
                    const bool prevStatus = idx > 0 && owner->msgs[(size_t) idx - 1].kind == Kind::status;
                    const bool nextStatus = idx + 1 < (int) owner->msgs.size()
                                          && owner->msgs[(size_t) idx + 1].kind == Kind::status;
                    if (! prevStatus && ! nextStatus)          // isolated: a scene break
                    {
                        const float tw = theme::measure (theme::ui (9.5f), m.text);
                        const float cy = y + m.h * 0.5f;
                        g.setColour (theme::line.withAlpha (0.6f));
                        g.drawHorizontalLine ((int) cy, 20.0f, juce::jmax (20.0f, (w - tw) * 0.5f - 10.0f));
                        g.drawHorizontalLine ((int) cy, juce::jmin ((float) w - 20.0f, (w + tw) * 0.5f + 10.0f), (float) w - 20.0f);
                    }
                    const bool acc = m.text.startsWith ("you ACCEPTED");
                    const bool rej = m.text.startsWith ("you REJECTED");
                    if (acc || rej)
                    {   // a VERDICT is project memory — it wears a chip + glyph, not grey dust
                        const auto vc = acc ? theme::good : theme::bad;
                        const auto f2 = theme::ui (9.0f, juce::Font::bold);
                        const float tw2 = theme::measure (f2, m.text) + 30.0f;
                        juce::Rectangle<float> chip ((w - tw2) * 0.5f, y + 1.0f, tw2, m.h - 3.0f);
                        g.setColour (vc.withAlpha (0.10f));
                        g.fillRoundedRectangle (chip, 7.0f);
                        g.setColour (vc.withAlpha (0.45f));
                        g.drawRoundedRectangle (chip.reduced (0.5f), 7.0f, 1.0f);
                        const float gx = chip.getX() + 8.0f, gy = chip.getCentreY();
                        g.setColour (vc);
                        if (acc)
                        {
                            juce::Path ck;
                            ck.startNewSubPath (gx, gy + 0.5f);
                            ck.lineTo (gx + 2.2f, gy + 2.8f);
                            ck.lineTo (gx + 6.4f, gy - 2.6f);
                            g.strokePath (ck, { 1.6f, juce::PathStrokeType::curved,
                                                juce::PathStrokeType::rounded });
                        }
                        else
                        {
                            g.drawLine (gx, gy - 2.8f, gx + 5.6f, gy + 2.8f, 1.5f);
                            g.drawLine (gx, gy + 2.8f, gx + 5.6f, gy - 2.8f, 1.5f);
                        }
                        g.setColour (theme::textDim.brighter (0.1f));
                        g.setFont (f2);
                        g.drawText (m.text, chip.withTrimmedLeft (18.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                    }
                    else
                    {
                        g.setColour (theme::textMute.withAlpha (prevStatus || nextStatus ? 0.6f : 0.9f));
                        g.setFont (theme::ui (9.5f));
                        g.drawText (m.text, 10, (int) y, (int) cardW, (int) m.h, juce::Justification::centred);
                    }
                }
                else if (m.kind == Kind::tool)
                {
                    const float pw = juce::jmin (cardW - 18.0f, 48.0f + theme::measure (theme::mono (10.5f), m.text));
                    juce::Rectangle<float> pill (24.0f, y + 1.0f, pw, m.h - 7.0f);
                    g.setColour (theme::agent.withAlpha (0.35f));      // thread spine: tool runs hang off the agent
                    g.drawVerticalLine (16, y - 2.0f, y + m.h);
                    g.setColour (theme::inset);
                    g.fillRoundedRectangle (pill, 9.0f);
                    g.setColour (theme::agent.withAlpha (0.35f));
                    g.drawRoundedRectangle (pill.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (theme::agent);
                    g.fillEllipse (pill.getX() + 9.0f, pill.getCentreY() - 2.5f, 5.0f, 5.0f);
                    g.setColour (theme::textDim);
                    g.setFont (theme::mono (10.5f));
                    g.drawText (m.text, pill.withTrimmedLeft (21.0f).withTrimmedRight (10.0f).toNearestInt(),
                                juce::Justification::centredLeft);
                }
                else if (m.kind == Kind::action)
                {
                    // THE ACTION STREAM: one agent tool call as a DAW component —
                    // family glyph tile + TOOL caps + summary + target-track tick.
                    const auto family = m.meta.size() > 0 ? m.meta[0] : juce::String();
                    const auto tool   = m.meta.size() > 1 ? m.meta[1] : juce::String ("tool");
                    const auto track  = m.meta.size() > 2 ? m.meta[2] : juce::String();
                    const auto colHex = m.meta.size() > 3 ? m.meta[3] : juce::String();
                    const auto fc     = familyColour (family);
                    g.setColour (theme::agent.withAlpha (0.35f));      // the same thread spine
                    g.drawVerticalLine (16, y - 2.0f, y + m.h);
                    const float toolW = theme::measure (theme::caps (8.5f), tool.toUpperCase());
                    const float sumW  = m.text.isNotEmpty() ? 8.0f + theme::measure (theme::ui (10.5f), m.text) : 0.0f;
                    const float trkW  = track.isNotEmpty()
                                          ? 16.0f + theme::measure (theme::caps (7.5f), track.toUpperCase()) : 0.0f;
                    const float pw = juce::jmin (cardW - 18.0f, 34.0f + toolW + sumW + trkW + 14.0f);
                    juce::Rectangle<float> card (24.0f, y + 1.0f, pw, m.h - 8.0f);
                    g.setColour (theme::inset);
                    g.fillRoundedRectangle (card, 6.0f);
                    g.setColour (fc.withAlpha (0.10f));
                    g.fillRoundedRectangle (card, 6.0f);
                    g.setColour (fc.withAlpha (0.38f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 6.0f, 1.0f);
                    auto tile = juce::Rectangle<float> (card.getX() + 4.0f, card.getCentreY() - 7.0f, 14.0f, 14.0f);
                    g.setColour (fc.withAlpha (0.16f));                // the family tile
                    g.fillRoundedRectangle (tile, 4.0f);
                    familyGlyph (g, tile.reduced (2.5f), family, fc);
                    auto tr2 = card.withTrimmedLeft (24.0f).withTrimmedRight (6.0f);
                    g.setColour (fc.withMultipliedBrightness (1.15f));
                    g.setFont (theme::caps (8.5f));
                    g.drawText (tool.toUpperCase(), tr2.removeFromLeft (toolW + 2.0f).toNearestInt(),
                                juce::Justification::centredLeft);
                    if (track.isNotEmpty())                            // the target wears its channel colour
                    {
                        auto tc = tr2.removeFromRight (trkW);
                        const auto hex = colHex.removeCharacters ("#");
                        const auto col = juce::Colour::fromString (
                            hex.length() == 6 ? "ff" + hex : hex.isEmpty() ? "ff5d6478" : hex);
                        g.setColour (col.withAlpha (0.9f));
                        g.fillEllipse (tc.getX() + 2.0f, tc.getCentreY() - 2.5f, 5.0f, 5.0f);
                        g.setColour (theme::textDim);
                        g.setFont (theme::caps (7.5f));
                        g.drawText (track.toUpperCase(), tc.withTrimmedLeft (10.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                    }
                    if (m.text.isNotEmpty())
                    {
                        g.setColour (theme::text.withAlpha (0.8f));
                        g.setFont (theme::ui (10.5f));
                        g.drawText (m.text, tr2.reduced (5.0f, 0.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                    }
                }
                else
                {
                    const bool user = m.kind == Kind::user;
                    const bool err = m.kind == Kind::error;
                    const int idx = (int) (&m - &owner->msgs[0]);
                    juce::AttributedString as;
                    buildBody (as, m.text, err ? theme::warn.brighter (0.1f) : theme::text);
                    juce::TextLayout tl;
                    tl.createLayout (as, cardW * 0.87f - 26.0f);
                    const bool collapsible = tl.getHeight() > collapseTextH + 40.0f;
                    const bool clipped = collapsible && ! m.expanded;
                    const float shownH = clipped ? collapseTextH : tl.getHeight();
                    const float ch = shownH + 16.0f + (collapsible ? 18.0f : 0.0f);
                    const float bw = juce::jmin (cardW * 0.87f, tl.getWidth() + 28.0f);
                    juce::Rectangle<float> card (user ? w - 10.0f - bw : 24.0f, y, bw, ch);
                    if (user)
                    {
                        g.setColour (juce::Colours::black.withAlpha (0.25f));   // seat: the bubble sits proud
                        g.fillRoundedRectangle (card.translated (0.0f, 1.5f), 10.0f);
                        g.setGradientFill ({ theme::accent.withAlpha (0.30f), card.getTopLeft(),
                                             theme::accent.withAlpha (0.16f), card.getBottomLeft(), false });
                        g.fillRoundedRectangle (card, 10.0f);
                        g.setColour (juce::Colours::white.withAlpha (0.10f));   // glass top-light
                        g.drawHorizontalLine ((int) card.getY() + 1, card.getX() + 8.0f, card.getRight() - 8.0f);
                        g.setColour (theme::accent.withAlpha (0.45f));
                        g.drawRoundedRectangle (card.reduced (0.5f), 10.0f, 1.0f);
                    }
                    else if (err)
                    {
                        theme::card (g, card, theme::bad.withAlpha (0.13f), 10.0f, 0.0f);
                        g.setColour (theme::bad.withAlpha (0.85f));
                        g.fillRoundedRectangle (card.getX(), card.getY() + 3.0f, 3.0f, card.getHeight() - 6.0f, 1.5f);
                    }
                    else if (m.text.trimStart().startsWith ("PLAN:"))
                    {
                        // #16 THE PLAN CARD: the run's contract, streamed BEFORE
                        // tools fire (the PLAN-FIRST prompt law) — branded so the
                        // user sees the agent commit to a shape before it works
                        theme::card (g, card, theme::agent.withAlpha (0.10f), 10.0f);
                        g.setColour (theme::agent.withAlpha (0.9f));
                        g.fillRoundedRectangle (card.getX(), card.getY() + 3.0f, 3.0f,
                                                card.getHeight() - 6.0f, 1.5f);
                        g.setColour (theme::agent);
                        g.setFont (theme::caps (8.0f));
                        g.drawText ("THE PLAN", (int) card.getX() + 13, (int) y + 1, 120, 10,
                                    juce::Justification::centredLeft);
                        theme::spark (g, { 8.0f, y + 5.0f, 8.0f, 8.0f }, theme::agent);
                    }
                    else
                    {
                        theme::card (g, card, theme::panelHi, 10.0f);
                        // agent badge: violet spark in the gutter
                        g.setColour (theme::agent.withAlpha (0.16f));
                        g.fillEllipse (4.0f, y + 1.0f, 16.0f, 16.0f);
                        theme::spark (g, { 8.0f, y + 5.0f, 8.0f, 8.0f }, theme::agent);
                    }
                    auto textArea = card.reduced (13.0f, 8.0f).withHeight (shownH);
                    {
                        juce::Graphics::ScopedSaveState ss (g);
                        g.reduceClipRegion (textArea.getSmallestIntegerContainer());
                        tl.draw (g, textArea.withHeight (tl.getHeight()));
                    }
                    if (clipped)   // fade the cut so it reads as "more below", never a chop
                    {
                        const auto bgCol = user ? theme::panel.overlaidWith (theme::accent.withAlpha (0.20f))
                                          : err ? theme::panel.overlaidWith (theme::bad.withAlpha (0.13f))
                                                : theme::panelHi;
                        g.setGradientFill ({ bgCol.withAlpha (0.0f), 0.0f, textArea.getBottom() - 34.0f,
                                             bgCol, 0.0f, textArea.getBottom(), false });
                        g.fillRect (textArea.expanded (8.0f, 0.0f).withTop (textArea.getBottom() - 34.0f));
                    }
                    if (collapsible)   // the reveal chip: fold and unfold the essay
                    {
                        const juce::String lbl = clipped
                            ? "show all " + juce::String (tl.getNumLines()) + " lines" : "collapse";
                        const auto f = theme::ui (9.5f, juce::Font::bold);
                        const float cwid = theme::measure (f, lbl) + 32.0f;
                        juce::Rectangle<float> chip (card.getCentreX() - cwid * 0.5f,
                                                     card.getBottom() - 21.0f, cwid, 16.0f);
                        const bool hov = hoverAction == 500 + idx;
                        g.setColour (theme::accent.withAlpha (hov ? 0.26f : 0.11f));
                        g.fillRoundedRectangle (chip, 8.0f);
                        g.setColour (theme::accent.withAlpha (hov ? 0.85f : 0.40f));
                        g.drawRoundedRectangle (chip.reduced (0.5f), 8.0f, 1.0f);
                        g.setColour (hov ? theme::text : theme::textDim);
                        g.setFont (f);
                        g.drawText (lbl, chip.withTrimmedLeft (14.0f).toNearestInt(),
                                    juce::Justification::centred);
                        juce::Path cv;   // fold chevron
                        const float cxp = chip.getX() + 10.0f, cyp = chip.getCentreY();
                        if (clipped) { cv.startNewSubPath (cxp - 3.0f, cyp - 1.5f); cv.lineTo (cxp, cyp + 2.0f); cv.lineTo (cxp + 3.0f, cyp - 1.5f); }
                        else         { cv.startNewSubPath (cxp - 3.0f, cyp + 1.5f); cv.lineTo (cxp, cyp - 2.0f); cv.lineTo (cxp + 3.0f, cyp + 1.5f); }
                        g.setColour (theme::accent.withAlpha (hov ? 1.0f : 0.7f));
                        g.strokePath (cv, { 1.4f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
                        hits.push_back ({ chip, 500 + idx });
                    }
                    hits.push_back ({ card, 100 + idx });
                    drawCopied (g, card, idx);
                }
                y += m.h;
            }
        }
    };

    // The agent writes essays — headings, bullets and table rows get typographic
    // treatment so a long reply reads as a document, not a wall. Shared by
    // measure() and paint() so heights always match the pixels.
    // INLINE MARKDOWN (CC4-I4 firing 104): agents SPEAK markdown — raw asterisks and
    // backticks in the bubbles were the single loudest 'Windows 98' tell. Parses
    // **bold** and `code` (code = mono, brand-tinted) inside any line.
    static void appendInline (juce::AttributedString& as, const juce::String& ln,
                              const juce::Font& f, juce::Colour base, const juce::String& nl)
    {
        int i = 0;
        const auto flush = [&] (const juce::String& seg, bool bold, bool code)
        {
            if (seg.isEmpty()) return;
            if (code)      as.append (seg, theme::mono (f.getHeight() - 2.0f, juce::Font::bold),
                                       theme::accentB);
            else if (bold) as.append (seg, theme::ui (f.getHeight(), juce::Font::bold),   // theme bold face
                                       base.brighter (0.22f));                            // (f.boldened() no-ops
            else           as.append (seg, f, base);                                      //  without a bold variant)
        };
        juce::String plain;
        while (i < ln.length())
        {
            if (ln[i] == '`')
            {
                const int close = ln.indexOfChar (i + 1, '`');
                if (close > i)
                {
                    flush (plain, false, false); plain.clear();
                    flush (ln.substring (i + 1, close), false, true);
                    i = close + 1; continue;
                }
            }
            if (i + 1 < ln.length() && ln[i] == '*' && ln[i + 1] == '*')
            {
                const int close = ln.indexOf (i + 2, "**");
                if (close > i)
                {
                    flush (plain, false, false); plain.clear();
                    flush (ln.substring (i + 2, close), true, false);
                    i = close + 2; continue;
                }
            }
            plain += ln[i++];
        }
        flush (plain + nl, false, false);
    }

    static void buildBody (juce::AttributedString& as, const juce::String& text, juce::Colour base)
    {
        auto lines = juce::StringArray::fromLines (text);
        for (int i = 0; i < lines.size(); ++i)
        {
            const auto& ln = lines[i];
            const juce::String nl = i == lines.size() - 1 ? "" : "\n";
            const int pipes = ln.length() - ln.removeCharacters ("|").length();
            const auto body = ln.trimStart();
            const bool numbered = body.length() > 2 && juce::CharacterFunctions::isDigit (body[0])
                                  && (body[1] == '.' || (juce::CharacterFunctions::isDigit (body[1]) && body[2] == '.'));
            if (ln.startsWith ("# ") || ln.startsWith ("## ") || ln.startsWith ("### "))
                appendInline (as, ln.fromFirstOccurrenceOf (" ", false, false).trim(),
                              theme::ui (12.5f, juce::Font::bold), base.brighter (0.18f), nl);
            else if (body.startsWith ("- ") || body.startsWith ("* "))
                appendInline (as, juce::String::fromUTF8 ("\xe2\x80\xa2 ") + body.substring (2),
                              theme::ui (12.0f), base.withMultipliedAlpha (0.92f), nl);
            else if (numbered)
            {
                as.append (body.upToFirstOccurrenceOf (".", true, false) + " ",
                           theme::ui (12.0f, juce::Font::bold), theme::accent.withAlpha (0.9f));
                appendInline (as, body.fromFirstOccurrenceOf (".", false, false).trimStart(),
                              theme::ui (12.0f), base, nl);
            }
            else if (pipes >= 2)                          // table row: mono, dimmer, denser
                as.append (ln + nl, theme::mono (9.5f), base.withMultipliedAlpha (0.78f));
            else
                appendInline (as, ln, theme::ui (12.5f), base, nl);
        }
    }

    // ---- THE ACTION STREAM's family language (colour + drawn glyph, no fonts) ----
    static juce::Colour familyColour (const juce::String& f)
    {
        if (f == "fx" || f == "sound" || f == "dj" || f == "jam") return theme::accentB;
        if (f == "master")                                        return theme::good;
        if (f == "render")                                        return theme::warn;
        if (f == "ears")                                          return theme::meterHi;
        if (f == "read")                                          return theme::textMute;
        return theme::accent;                     // notes / track / song / vocal / tool
    }
    static void familyGlyph (juce::Graphics& g, juce::Rectangle<float> r,
                             const juce::String& f, juce::Colour c)
    {
        g.setColour (c.withAlpha (0.95f));
        const float x = r.getX(), y = r.getY(), w = r.getWidth(), h = r.getHeight();
        if (f == "fx")                            // a device knob, pointer at 1 o'clock
        {
            g.drawEllipse (r.reduced (1.0f), 1.2f);
            g.drawLine (r.getCentreX(), r.getCentreY(),
                        r.getCentreX() + w * 0.26f, y + h * 0.2f, 1.3f);
        }
        else if (f == "master")                   // the wall: staggered bricks
        {
            g.fillRoundedRectangle (x, y + h * 0.15f, w * 0.55f, h * 0.28f, 1.0f);
            g.fillRoundedRectangle (x + w * 0.62f, y + h * 0.15f, w * 0.38f, h * 0.28f, 1.0f);
            g.fillRoundedRectangle (x, y + h * 0.55f, w * 0.38f, h * 0.28f, 1.0f);
            g.fillRoundedRectangle (x + w * 0.45f, y + h * 0.55f, w * 0.55f, h * 0.28f, 1.0f);
        }
        else if (f == "notes")                    // two clip blocks on a lane
        {
            g.fillRoundedRectangle (x, y + h * 0.16f, w * 0.62f, h * 0.30f, 1.5f);
            g.fillRoundedRectangle (x + w * 0.30f, y + h * 0.56f, w * 0.62f, h * 0.30f, 1.5f);
        }
        else if (f == "track")                    // a channel fader
        {
            g.drawLine (r.getCentreX(), y, r.getCentreX(), r.getBottom(), 1.2f);
            g.fillRoundedRectangle (x + w * 0.18f, y + h * 0.38f, w * 0.64f, h * 0.26f, 1.5f);
        }
        else if (f == "song")                     // the arrangement: section bars
        {
            g.fillRect (x, y + h * 0.12f, w * 0.9f, h * 0.18f);
            g.fillRect (x, y + h * 0.42f, w * 0.6f, h * 0.18f);
            g.fillRect (x, y + h * 0.72f, w * 0.75f, h * 0.18f);
        }
        else if (f == "render")                   // bounce: arrow into the floor
        {
            g.drawLine (r.getCentreX(), y, r.getCentreX(), y + h * 0.58f, 1.3f);
            juce::Path p2;
            p2.addTriangle (r.getCentreX() - w * 0.22f, y + h * 0.45f,
                            r.getCentreX() + w * 0.22f, y + h * 0.45f,
                            r.getCentreX(), y + h * 0.72f);
            g.fillPath (p2);
            g.fillRect (x, r.getBottom() - h * 0.16f, w, h * 0.13f);
        }
        else if (f == "ears")                     // the analyzer: three live bands
        {
            g.fillRoundedRectangle (x + w * 0.06f, y + h * 0.45f, w * 0.2f, h * 0.55f, 1.0f);
            g.fillRoundedRectangle (x + w * 0.40f, y + h * 0.10f, w * 0.2f, h * 0.90f, 1.0f);
            g.fillRoundedRectangle (x + w * 0.74f, y + h * 0.30f, w * 0.2f, h * 0.70f, 1.0f);
        }
        else if (f == "sound")                    // a cycle of the voice itself
        {
            juce::Path p2;
            p2.startNewSubPath (x, r.getCentreY());
            p2.quadraticTo (x + w * 0.25f, y - h * 0.1f, r.getCentreX(), r.getCentreY());
            p2.quadraticTo (x + w * 0.75f, r.getBottom() + h * 0.1f, r.getRight(), r.getCentreY());
            g.strokePath (p2, juce::PathStrokeType (1.3f));
        }
        else if (f == "vocal")                    // the mic
        {
            g.fillRoundedRectangle (x + w * 0.32f, y, w * 0.36f, h * 0.52f, w * 0.18f);
            g.drawLine (r.getCentreX(), y + h * 0.62f, r.getCentreX(), r.getBottom(), 1.2f);
            g.drawLine (x + w * 0.22f, r.getBottom(), x + w * 0.78f, r.getBottom(), 1.2f);
        }
        else if (f == "dj")                       // two decks, kissing
        {
            g.drawEllipse (x, y + h * 0.2f, w * 0.55f, h * 0.55f, 1.2f);
            g.drawEllipse (x + w * 0.45f, y + h * 0.25f, w * 0.55f, h * 0.55f, 1.2f);
        }
        else
            theme::spark (g, r.reduced (1.0f), c); // jam / read / tool: the agent's mark
    }

    static constexpr float collapseTextH = 208.0f;        // long replies fold at ~14 lines

    // THE SOUND TENSOR is a fixed-width ASCII grid — make it BIGGER + ADAPTIVE
    // (Chezy: agent-first mode) by sizing the mono row to FILL the card width, so
    // a wide agent-mode column gets a big legible spectrogram, a narrow sidebar
    // stays compact. Pure fn of (cardW, text) — measure() and paint() agree.
    static float tensorRowH (float cardW, const juce::String& text)
    {
        int cols = 48;
        for (auto& ln : juce::StringArray::fromLines (text))
            cols = juce::jmax (cols, ln.length());
        const float fontH = juce::jlimit (8.5f, 15.0f,
                                          (cardW - 28.0f) / (0.60f * (float) juce::jmax (1, cols)));
        return fontH + 2.5f;
    }

    void measure (Msg& m, int w)
    {
        if (m.kind == Kind::live)        m.h = (float) m.liveH + 16.0f;
        else if (m.kind == Kind::status)      m.h = 15.0f;   // tight: runs recede
        else if (m.kind == Kind::analysis) m.h = 66.0f;
        else if (m.kind == Kind::variants) m.h = 38.0f + 26.0f * (float) (m.meta.size() / 4);
        else if (m.kind == Kind::report)
            m.h = 32.0f + 13.0f * (float) juce::StringArray::fromLines (m.text).size();
        else if (m.kind == Kind::perception)
            m.h = 34.0f + tensorRowH ((float) w - 20.0f, m.text)
                        * (float) juce::StringArray::fromLines (m.text).size();
        else if (m.kind == Kind::tool)   m.h = 25.0f;
        else if (m.kind == Kind::action) m.h = 28.0f;
        else if (m.kind == Kind::proposal)
        {
            const float wave = m.peaks.empty() ? 0.0f : 30.0f;
            juce::AttributedString as;
            as.append (m.text, theme::ui (12.0f), theme::text);
            juce::TextLayout tl;
            tl.createLayout (as, (w - 20.0f) - 28.0f);
            m.h = tl.getHeight() + 24.0f + 40.0f + 16.0f + 10.0f + (m.meta.isEmpty() ? 0.0f : 22.0f) + wave;
        }
        else
        {
            juce::AttributedString as;
            buildBody (as, m.text, theme::text);
            juce::TextLayout tl;
            tl.createLayout (as, (w - 20.0f) * 0.87f - 26.0f);
            const bool collapsible = tl.getHeight() > collapseTextH + 40.0f;
            const float shown = (collapsible && ! m.expanded) ? collapseTextH : tl.getHeight();
            m.h = shown + 16.0f + 8.0f + (collapsible ? 18.0f : 0.0f);
        }
    }

    void relayout()
    {
        const int w = juce::jmax (60, vp.getWidth() - 12);
        totalH = 6.0f;
        for (auto& m : msgs) { measure (m, w); totalH += m.h; }
        syncContent();
    }

    void syncContent()   // bottom-anchor when short, scroll when long — THE SCROLL LAW
    {                    // (CC3-5): follow only if the user was near the bottom; never yank.
        const int w = juce::jmax (60, vp.getWidth() - 12);
        const int vh = juce::jmax (0, vp.getMaximumVisibleHeight());
        vp.autoMove = true;                // every move below is OURS, not a user scroll
        content.topOffset = juce::jmax (0.0f, (float) vh - ((float) totalH + 14.0f));
        content.setSize (w, juce::jmax ((int) totalH + 14, vh));
        layoutLive();                      // live cards ride the same flow as paint
        content.repaint();
        if (pinnedToBottom)
            vp.setViewPosition (0, juce::jmax (0, content.getHeight() - vp.getHeight()));
        vp.autoMove = false;
        jumpBtn.setVisible (! pinnedToBottom);
    }

    void layoutLive()   // mirror of paint()'s y-walk: cards are CHILDREN, bounds must agree
    {
        float y = 8.0f + content.topOffset;
        const int w = content.getWidth();
        for (auto& m : msgs)
        {
            if (m.live != nullptr)
                m.live->setBounds (24, (int) y + 4, juce::jmax (40, w - 34), juce::jmax (32, (int) m.h - 12));
            y += m.h;
        }
    }

    float totalH = 6.0f;
    int deadTick = 0;
    bool pinnedToBottom = true;
    bool streamOpen = false;    // TOKEN STREAM: the tail msg is a growing agent card
    struct JumpPill : juce::Button
    {
        JumpPill() : juce::Button ("latest") {}
        void paintButton (juce::Graphics& g, bool over, bool) override
        {   // frosted material, never an accent slab over the reading line
            auto r = getLocalBounds().toFloat().reduced (0.5f);
            g.setColour (theme::panel.withAlpha (over ? 0.94f : 0.80f));
            g.fillRoundedRectangle (r, 11.0f);
            g.setColour (theme::accent.withAlpha (over ? 0.85f : 0.50f));
            g.drawRoundedRectangle (r, 11.0f, 1.0f);
            g.setColour (theme::text.withAlpha (0.92f));
            g.setFont (theme::caps (8.5f));
            g.drawText (juce::String::fromUTF8 ("\xe2\x86\x93") + "  LATEST", r,
                        juce::Justification::centred);
        }
    };
    JumpPill jumpBtn;
    std::vector<Msg> msgs;
    struct PinViewport : juce::Viewport
    {
        std::function<void()> onUserScroll;
        bool autoMove = false;             // set around every programmatic move
        void visibleAreaChanged (const juce::Rectangle<int>&) override
        { if (! autoMove && onUserScroll != nullptr) onUserScroll(); }
    };
    PinViewport vp;
    Content content;
    friend struct Content;
};
