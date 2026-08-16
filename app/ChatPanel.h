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
    enum class Kind { user, agent, tool, action, status, error, proposal, analysis, perception, report, live, variants, divider };
    // THE SELECTION ENGINE (Chezy 2026-07-16: "I need to select every single bit
    // of text just like in every other app"): every textual message carries its
    // own display layout — wrapped lines of styled segments with REAL glyph
    // geometry — so the mouse can address characters, not cards. measure() builds
    // it; paint() draws FROM it (one source of truth: highlight and glyphs can
    // never disagree); the click-to-copy era is over.
    struct Seg { juce::String t; juce::Font f; juce::Colour c; float x = 0, w = 0; };
    struct DispLine { float y = 0, h = 14.0f; int src = 0; std::vector<Seg> segs; };
    struct Msg { Kind kind; juce::String text; juce::StringArray meta; float h = 20.0f;
                 bool expanded = false; bool wasStream = false; bool wasThink = false;
                 // P65 RUN FOLDS: runId stamped lazily (user asks open runs); folded
                 // members paint nothing; a Kind::divider row summarizes the run.
                 int runId = 0; bool folded = false; juce::int64 at = 0;
                 std::vector<float> peaks;
                 // the display layout (selection truth): lines + the flat text they show
                 std::vector<DispLine> lay; juce::String dispText;
                 float layW = 0.0f, layH = 0.0f;          // natural width / total text height
                 float txX = 0.0f, txY = 0.0f, yTop = 0.0f;   // text origin + card top (set by paint)
                 // THE CHAT IS A DAW: a live component rides the transcript (Kind::live).
                 // The panel owns its lifetime + flow position; the host keeps the raw
                 // pointer to retarget/freeze it and hears onLiveGone when pruned.
                 std::unique_ptr<juce::Component> live; int liveH = 0; };
    std::function<void()> onAudition, onAccept, onReject;   // proposal-card buttons
    std::function<void()> onPlayTake;                       // #17: EARS card ▶ = hear what it measured
    std::function<void()> onRetry;                          // P64: error card ↻ — host resends or explains
    std::function<void (const juce::String&)> onSuggest;    // empty-state starter chips -> prompt box
    std::function<void (int)> onDoor;   // THE DOORS (rebrand 31 §1a): 0=bring a song, 1=MAKE, 2=finish
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

    // THE FINAL IS NOT A TWIN (2026-08-02 "responses ARE STILL DOUBLED"):
    // the run-end "agent done: <text>" used to land as a second full card
    // beside the streamed one whenever the sidecar's dedup missed (long
    // replies, caps, whitespace). The sidecar is fixed at the source; this
    // is the UI belt - cap-blind prefix law, mirror of tools/chat_truth.py.
    void addFinal (const juce::String& body)
    {
        const auto norm = [] (juce::String s)
        { return s.replace ("\n", " ").replace ("  ", " ").trim(); };
        const auto f = norm (body);
        for (int back = 0; back < juce::jmin (8, (int) msgs.size()); ++back)
        {
            auto& m = msgs[msgs.size() - 1 - (size_t) back];
            if (m.kind == Kind::user) break;
            if (m.kind != Kind::agent || m.wasThink) continue;
            const auto c = norm (m.text);
            if (f.isNotEmpty() && c.isNotEmpty())
            {
                const auto& shorter = f.length() <= c.length() ? f : c;
                const auto& longer  = f.length() <= c.length() ? c : f;
                const bool same = f == c
                    || (shorter.length() >= 600
                        && longer.startsWith (shorter.substring (0, 600)))
                    || (shorter.length() >= 80 && longer.startsWith (shorter));
                if (same) { add (Kind::status, "producer done."); return; }
            }
            break;   // only the nearest settled reply guards
        }
        add (Kind::agent, body);
    }

    void add (Kind k, juce::String text, juce::StringArray meta = {})
    {
        if (agentBusy) lastEventMs = juce::Time::getMillisecondCounter();   // P63: any event calms "quiet"
        addInner (k, std::move (text), std::move (meta));
        if (! msgs.empty() && msgs.back().at == 0)
            msgs.back().at = juce::Time::currentTimeMillis();
        if (k == Kind::user)
        {   // P65: a fresh ask ages the transcript — old runs fold behind dividers
            refreshRunFolds();
            relayout();
        }
    }
    // P65 SESSION DIVIDERS: a RUN = one user ask and everything until the next.
    // The last 3 runs stay open; older ones fold into one honest line each
    // ("18:42 \"make the drop harder\" - 12 actions"). Click = expand in place;
    // an expanded divider PINS its run open (the next sweep respects the hand).
    // Runs carrying LIVE cards never fold (their components are real - memory
    // honesty by avoidance). Ids are stamped lazily from the transcript itself,
    // so every add path (replay included) stays covered with zero push-site law.
    int foldKeepRuns = 3;
    void refreshRunFolds()
    {
        int run = 0;
        for (auto& m : msgs)
        {
            if (m.kind == Kind::user) ++run;
            if (m.kind != Kind::divider) m.runId = run;
        }
        if (run <= foldKeepRuns) return;
        bool changed = false;
        for (int id = 1; id <= run - foldKeepRuns; ++id)
        {
            bool hasLive = false, hasDivider = false, anyOpen = false, pinned = false;
            size_t first = msgs.size();
            for (size_t i = 0; i < msgs.size(); ++i)
            {
                auto& m = msgs[i];
                if (m.runId != id) continue;
                if (m.kind == Kind::divider) { hasDivider = true; pinned = pinned || m.expanded; continue; }
                if (m.live != nullptr) hasLive = true;
                if (! m.folded) anyOpen = true;
                if (first == msgs.size()) first = i;
            }
            if (first == msgs.size() || hasLive || pinned || ! anyOpen) continue;
            juce::String ask;
            int actions = 0;
            bool hadErr = false;
            juce::int64 t0 = 0;
            for (auto& m : msgs)
                if (m.runId == id && m.kind != Kind::divider)
                {
                    if (m.kind == Kind::user && ask.isEmpty()) { ask = m.text; t0 = m.at; }
                    if (m.kind == Kind::action || m.kind == Kind::tool) ++actions;
                    if (m.kind == Kind::error) hadErr = true;
                    m.folded = true;
                }
            changed = true;
            if (! hasDivider)
            {
                Msg d;
                d.kind = Kind::divider;
                d.runId = id;
                d.text = (t0 > 0 ? juce::Time (t0).formatted ("%H:%M ") : juce::String())
                       + "\"" + ask.substring (0, 46) + "\"" + (ask.length() > 46 ? "..." : "")
                       + " - " + juce::String (actions) + " action" + (actions == 1 ? "" : "s")
                       + (hadErr ? " - errored" : "");
                d.meta = { hadErr ? "warn" : "dim" };
                msgs.insert (msgs.begin() + (long) first, std::move (d));
            }
        }
        if (changed) content.clearSelection();   // inserts shifted the indices
    }
    void toggleRun (int id)
    {   // expand/collapse in place; expanding one leaves the others folded
        bool nowOpen = false;
        for (auto& m : msgs)
            if (m.kind == Kind::divider && m.runId == id)
            { m.expanded = ! m.expanded; nowOpen = m.expanded; break; }
        for (auto& m : msgs)
            if (m.kind != Kind::divider && m.runId == id)
                m.folded = ! nowOpen;
        content.clearSelection();
        relayout();
    }
    int foldedForRig() const
    { int n = 0; for (auto& m : msgs) n += m.folded ? 1 : 0; return n; }
    int dividersForRig() const
    { int n = 0; for (auto& m : msgs) n += m.kind == Kind::divider ? 1 : 0; return n; }
    void addInner (Kind k, juce::String text, juce::StringArray meta = {})
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
        content.clearSelection();          // dead indices must not haunt the next thread
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
        {   // P63: the pulse readout feeds on the deltas themselves
            const auto nowMs = juce::Time::getMillisecondCounter();
            lastEventMs = nowMs;
            if (! thinking)
            {
                const int len = text.length();
                if (lastDeltaMs != 0 && nowMs > lastDeltaMs && len > lastStreamLen)
                {
                    const double inst = (len - lastStreamLen) / 4.0
                                        / juce::jmax (0.05, (nowMs - lastDeltaMs) / 1000.0);
                    const double a = juce::jlimit (0.05, 0.5, (nowMs - lastDeltaMs) / 3000.0);
                    tokEma = tokEma <= 0.0 ? inst : tokEma + a * (inst - tokEma);
                }
                lastDeltaMs = nowMs;
                lastStreamLen = len;
            }
        }
        // THE TWIN LAW (Chezy 2026-07-16: PLAN + finals doubled): a delta whose
        // text the NEAREST settled agent card already says is an emitter's
        // trailing flush racing the block-complete reply — an echo, never new
        // typing. Dropping it can never lose words: every block-complete reply
        // also lands via add(); this guard only costs echo cards.
        if (! streamOpen)
            for (int back = 0; back < juce::jmin (4, (int) msgs.size()); ++back)
            {
                auto& m = msgs[msgs.size() - 1 - (size_t) back];
                if (m.kind != Kind::agent) continue;
                if (! m.wasStream && (m.text == text || m.text.startsWith (text)
                                      || (m.text.length() >= 1000 && text.startsWith (m.text))))
                    return;
                break;   // only the nearest agent card guards
            }
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
        // climbing counter, one card per run is the whole story). ONE CARD
        // LAW (2026-08-02 "the thinking is ugly"): the old 6-row look-back
        // lost the card behind tool pills and minted stacked twins - walk
        // back to the run boundary (the last USER row), never across it.
        if (thinking)
            for (int back = 0; back < juce::jmin (64, (int) msgs.size()); ++back)
            {
                auto& m = msgs[msgs.size() - 1 - (size_t) back];
                if (m.kind == Kind::user) break;   // a mind never crosses asks
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
    // P63 THE PULSE READOUT (UI_SPEC_100): the liveness pill learns RATE — a
    // chars/4-per-second EMA over the delta stream ("~42 tok/s"), "..." while
    // only thinking pulses arrive, and an honest warn "quiet Ns" after 30s of
    // NO events at all. Feeds ride the existing stream — no new protocol.
    double tokEma = 0.0;
    juce::uint32 lastDeltaMs = 0, lastEventMs = 0;
    int lastStreamLen = 0;
    bool busyWas = false;
    juce::String pulseReadout() const
    {
        if (! agentBusy || agentDead) return {};
        const auto nowMs = juce::Time::getMillisecondCounter();
        if (lastEventMs != 0 && nowMs - lastEventMs > 30000)
            return "quiet " + juce::String ((int) ((nowMs - lastEventMs) / 1000)) + "s";
        if (lastDeltaMs != 0 && nowMs - lastDeltaMs < 4000 && tokEma > 0.5)
            return "~" + juce::String ((int) std::round (tokEma)) + " tok/s";
        return "...";
    }
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
        // THE VOID WEARS THE MARK: short conversations bottom-anchor and leave
        // the upper column bare — the spark breathes there as dormant material
        // (never text, never a banner). Retires the moment the transcript fills.
        if (content.topOffset > 140.0f && vp.getViewPositionY() <= 0)
        {
            const float s = juce::jmin (120.0f, content.topOffset * 0.45f);
            const float sy = 40.0f + (content.topOffset - s) * 0.42f;
            theme::spark (g, { r.getCentreX() - s * 0.5f, sy, s, s },
                          theme::agent.withAlpha (0.055f));
            theme::spark (g, { r.getCentreX() - s * 0.16f, sy + s * 0.30f,
                               s * 0.4f, s * 0.4f },
                          theme::accent.withAlpha (0.045f));
        }
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
            if (const auto rate = pulseReadout(); rate.isNotEmpty())
            {   // P63: the pulse speaks its rate beside the word
                g.setColour ((rate.startsWith ("quiet") ? theme::warn
                                                        : theme::textMute).withAlpha (0.85f));
                g.setFont (theme::mono (8.5f));
                g.drawText (rate, h.toNearestInt().removeFromRight (240).withTrimmedRight (104),
                            juce::Justification::centredRight);
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
        drawCosmoScore (g);   // the working-state MATERIAL: levitating notation
        if (! agentBusy && ! agentDead) return;
        // THE LIVENESS PILL: a floating glass chip, top-centre of the column -
        // the frameless page's only status material (never a banner strip)
        const auto tint = agentDead ? theme::bad : theme::warn;
        const juce::String word = agentDead ? "OFFLINE - restarting" : "composing";
        const auto rate = agentDead ? juce::String() : pulseReadout();   // P63
        const float rw = rate.isEmpty() ? 0.0f
                                        : theme::measure (theme::mono (8.5f), rate) + 12.0f;
        const float tw = theme::measure (theme::ui (10.0f, juce::Font::bold), word);
        const float pw = tw + (agentDead ? 34.0f : 60.0f) + rw;
        juce::Rectangle<float> pill ((float) getWidth() * 0.5f - pw * 0.5f, 6.0f, pw, 22.0f);
        g.setColour (juce::Colour (0xff0c0e15).withAlpha (0.82f));
        g.fillRoundedRectangle (pill, 11.0f);
        g.setColour (juce::Colours::white.withAlpha (0.035f));
        g.fillRoundedRectangle (pill, 11.0f);
        g.setColour (tint.withAlpha (0.248f));
        g.drawRoundedRectangle (pill.reduced (0.5f), 11.0f, 1.0f);
        theme::spark (g, { pill.getX() + 8.0f, pill.getCentreY() - 5.0f, 10.0f, 10.0f },
                      theme::agent.withAlpha (0.9f));
        g.setColour (tint.withAlpha (0.95f));
        g.setFont (theme::ui (10.0f, juce::Font::bold));
        g.drawText (word, pill.withTrimmedLeft (23.0f).toNearestInt(),
                    juce::Justification::centredLeft);
        if (rate.isNotEmpty())
        {   // P63: the rate rides between the word and the dots
            g.setColour ((rate.startsWith ("quiet") ? theme::warn
                                                    : theme::textMute).withAlpha (0.9f));
            g.setFont (theme::mono (8.5f));
            g.drawText (rate, pill.toNearestInt().withTrimmedRight (40),
                        juce::Justification::centredRight);
        }
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
    // ============================ THE COSMO SCORE ============================
    // (Chezy 2026-08-02: "a levitating and cosmo morphing music score notation
    // while the agent is working"). Real Bravura/SMuFL glyphs levitate over the
    // transcript's low air while the agent composes: a breathing staff ribbon,
    // note glyphs that drift, bob and MORPH between durations, cosmic dust with
    // parallax, the tint sliding violet->blue. Pure paint, driven by the 24Hz
    // busy timer, region-bounded, zero cost at rest (cosmoMix gates).
    float cosmoMix = 0.0f;
    juce::uint32 cosmoT0 = juce::Time::getMillisecondCounter();

    static juce::Typeface::Ptr cosmoFace()
    {
       #if SOTADAW_EMBEDDED_FONTS
        static const auto tf = juce::Typeface::createSystemTypefaceFor (
            BinaryData::Bravura_otf, (size_t) BinaryData::Bravura_otfSize);
        return tf;
       #else
        return nullptr;
       #endif
    }

    void drawCosmoScore (juce::Graphics& g)
    {
        if (cosmoMix <= 0.01f) return;
        const float w = (float) getWidth();
        const float bandH = 108.0f;
        const float y0 = (float) getHeight() - bandH;
        if (w < 160.0f || y0 < 40.0f) return;
        const double t = (double) (juce::Time::getMillisecondCounter() - cosmoT0) / 1000.0;
        const float mix = cosmoMix;
        // the tint breathes violet -> deep blue and back (the cosmo drift)
        const float hueW = 0.5f + 0.5f * std::sin ((float) t * 0.23f);
        const auto tint = theme::agent.interpolatedWith (juce::Colour (0xff58b7ff), hueW * 0.55f);
        juce::Graphics::ScopedSaveState save (g);
        g.reduceClipRegion (juce::Rectangle<int> (0, (int) y0, (int) w, (int) bandH));
        // ---- cosmic dust: two parallax depths, deterministic per index
        for (int i = 0; i < 26; ++i)
        {
            const float ph = (float) i * 2.399963f;                 // golden angle
            const float depth = (i % 2 == 0) ? 0.55f : 1.0f;        // far / near
            const float dx = std::fmod (ph * 97.0f + (float) t * (6.0f * depth), w + 24.0f) - 12.0f;
            const float dy = y0 + 14.0f + 80.0f * (0.5f + 0.5f * std::sin (ph * 3.1f + (float) t * (0.20f + 0.07f * depth)));
            const float tw = 0.5f + 0.5f * std::sin ((float) t * (1.1f + 0.13f * (float) (i % 5)) + ph);
            g.setColour (tint.withAlpha (mix * (0.04f + 0.10f * tw) * depth));
            const float r = depth > 0.9f ? 1.6f : 1.0f;
            g.fillEllipse (dx, dy, r, r);
        }
        // ---- the staff ribbon: five lines that undulate as ONE surface
        const float cy = y0 + bandH * 0.52f;
        for (int ln = -2; ln <= 2; ++ln)
        {
            juce::Path p;
            const float gap = 5.2f;
            bool first = true;
            for (float x = -8.0f; x <= w + 8.0f; x += 14.0f)
            {
                const float wave = 7.0f * std::sin (x * 0.011f + (float) t * 0.7f)
                                 + 3.0f * std::sin (x * 0.023f - (float) t * 0.43f);
                const float yy = cy + (float) ln * gap + wave
                               + (float) ln * 1.3f * std::sin (x * 0.007f + (float) t * 0.31f);
                if (first) { p.startNewSubPath (x, yy); first = false; }
                else         p.lineTo (x, yy);
            }
            g.setColour (tint.withAlpha (mix * (ln == 0 ? 0.16f : 0.10f)));
            g.strokePath (p, juce::PathStrokeType (ln == 0 ? 1.1f : 0.8f));
        }
        // ---- the levitating glyphs: drift, bob, sway, and MORPH duration
        const auto tf = cosmoFace();
        // SMuFL (Bravura): gClef E050, metronome-note quarter ECA5 / 8th ECA7 /
        // 16th ECA9 / half ECA3, rests E4E5/E4E6, sharp E262, head E0A4
        static const juce::juce_wchar A[9] = { 0xE050, 0xECA5, 0xECA7, 0xECA9,
                                               0xE4E5, 0xECA5, 0xE262, 0xECA7, 0xE0A4 };
        static const juce::juce_wchar B[9] = { 0xE050, 0xECA7, 0xECA9, 0xECA3,
                                               0xE4E6, 0xECA9, 0xE262, 0xECA5, 0xECA7 };
        for (int i = 0; i < 9; ++i)
        {
            const float ph = (float) i * 0.777f;
            const float speed = 9.0f + 3.5f * (float) (i % 3);
            const float px = std::fmod (ph * 151.0f + (float) t * speed, w + 90.0f) - 45.0f;
            const float bob = 16.0f * std::sin ((float) t * (0.5f + 0.09f * (float) i) + ph * 2.1f);
            const float py = cy + bob + 9.0f * std::sin (px * 0.012f + ph);
            const float sway = 0.16f * std::sin ((float) t * 0.8f + ph * 3.0f);
            const float sz = (i == 0 ? 34.0f : 21.0f + 2.4f * (float) (i % 4));
            // morph: A-form crossfades into B-form and back, per-glyph phase
            const float morph = 0.5f + 0.5f * std::sin ((float) t * (0.6f + 0.05f * (float) i) + ph * 1.7f);
            const float glow = 0.5f + 0.5f * std::sin ((float) t * 1.3f + ph * 5.0f);
            juce::Graphics::ScopedSaveState s2 (g);
            g.addTransform (juce::AffineTransform::rotation (sway, px, py));
            if (tf != nullptr)
            {
                const juce::Font mf (juce::FontOptions (tf).withHeight (sz));
                g.setFont (mf);
                const auto ga = juce::String::charToString (A[i]);
                const auto gb = juce::String::charToString (B[i]);
                // soft halo under the glyph = the levitation light
                g.setColour (tint.withAlpha (mix * 0.10f * glow));
                g.fillEllipse (px - sz * 0.42f, py + sz * 0.18f, sz * 0.84f, sz * 0.20f);
                g.setColour (tint.withAlpha (mix * (0.24f + 0.30f * glow) * (1.0f - morph)));
                g.drawText (ga, juce::Rectangle<float> (px - sz, py - sz, sz * 2.0f, sz * 2.0f)
                                   .toNearestInt(), juce::Justification::centred);
                g.setColour (tint.withAlpha (mix * (0.24f + 0.30f * glow) * morph));
                g.drawText (gb, juce::Rectangle<float> (px - sz, py - sz, sz * 2.0f, sz * 2.0f)
                                   .toNearestInt(), juce::Justification::centred);
            }
            else   // fallback shapes law: no face, still music (heads + stems)
            {
                g.setColour (tint.withAlpha (mix * (0.22f + 0.25f * glow)));
                g.fillEllipse (px - 3.4f, py - 2.6f, 6.8f, 5.2f);
                g.drawLine (px + 3.2f, py, px + 3.2f, py - 14.0f, 1.1f);
            }
        }
        // the band dissolves upward into the transcript - depth, never a box
        g.setGradientFill ({ juce::Colour (0xff0a0b12).withAlpha (0.0f),
                             { 0.0f, y0 + bandH * 0.4f },
                             juce::Colour (0xff0a0b12).withAlpha (mix * 0.20f),
                             { 0.0f, y0 }, false });
        g.fillRect (juce::Rectangle<float> (0.0f, y0, w, bandH * 0.5f));
    }

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
        content.clearSelection();          // indices shifted under the selection
        relayout();
    }

    void timerCallback() override
    {
        if (agentBusy && ! busyWas)
        {   // P63: a fresh run zeroes the pulse (stale silence must not cry wolf)
            tokEma = 0.0; lastDeltaMs = 0; lastStreamLen = 0;
            lastEventMs = juce::Time::getMillisecondCounter();
        }
        busyWas = agentBusy;
        // THE COSMO SCORE eases in while the agent works and dissolves when it
        // rests — repaint stays BOUNDED to the band (lag-campaign law: no
        // full-window storms; zero cost at rest once the fade lands)
        {
            const float cTgt = (agentBusy && ! agentDead) ? 1.0f : 0.0f;
            if (cosmoMix != cTgt || cosmoMix > 0.004f)
            {
                cosmoMix += (cTgt - cosmoMix) * 0.10f;
                if (cosmoMix < 0.004f && cTgt <= 0.0f) cosmoMix = 0.0f;
                if (cosmoMix > 0.0f)
                    repaint (0, juce::jmax (0, getHeight() - 118), getWidth(), 118);
            }
        }
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
        Content() { setWantsKeyboardFocus (true); }   // ctrl+C must reach this surface

        ChatPanel* owner = nullptr;
        float topOffset = 0.0f;         // bottom-anchor: few messages sit by the composer, not in a void
        struct Hit { juce::Rectangle<float> r; int action; };
        std::vector<Hit> hits;
        int flashIdx = -1;              // copy feedback (context menu / ctrl+C)
        juce::uint32 flashAt = 0;
        juce::String flashWord { "copied" };
        int hoverAction = -1;           // buttons/chips light under the mouse

        // ---- THE SELECTION (Chezy 2026-07-16: select text like every other app) ----
        struct SelPt { int msg = -1; int chr = 0; };
        SelPt selA, selB;               // anchor + head, in display-char space
        bool selecting = false, selDragged = false;

        static bool selLess (const SelPt& a, const SelPt& b)
        { return a.msg != b.msg ? a.msg < b.msg : a.chr < b.chr; }
        bool hasSelection() const
        { return selA.msg >= 0 && selB.msg >= 0
                 && ! (selA.msg == selB.msg && selA.chr == selB.chr); }
        void clearSelection()
        {
            if (selA.msg < 0 && selB.msg < 0) return;
            selA = SelPt(); selB = SelPt();
            repaint();
        }

        static int lineLength (const DispLine& dl)
        {
            int n = 0;
            for (auto& s : dl.segs) n += s.t.length();
            return n;
        }
        static int charInLine (const DispLine& dl, float lx)
        {
            int base = 0;
            for (auto& s : dl.segs)
            {
                if (lx < s.x) return base;
                if (lx <= s.x + s.w)
                {   // binary-search the boundary, then the midpoint rule picks a side
                    int lo = 0, hi = s.t.length();
                    while (lo < hi)
                    {
                        const int mid = (lo + hi + 1) / 2;
                        if (s.x + theme::measure (s.f, s.t.substring (0, mid)) <= lx) lo = mid;
                        else hi = mid - 1;
                    }
                    if (lo < s.t.length())
                    {
                        const float w0 = theme::measure (s.f, s.t.substring (0, lo));
                        const float w1 = theme::measure (s.f, s.t.substring (0, lo + 1));
                        if (lx - (s.x + w0) > (w1 - w0) * 0.5f) ++lo;
                    }
                    return base + lo;
                }
                base += s.t.length();
            }
            return base;
        }
        static float xAtChar (const DispLine& dl, int k)
        {
            int base = 0;
            for (auto& s : dl.segs)
            {
                if (k <= base + s.t.length())
                    return s.x + theme::measure (s.f, s.t.substring (0, k - base));
                base += s.t.length();
            }
            return dl.segs.empty() ? 0.0f : dl.segs.back().x + dl.segs.back().w;
        }
        int charAt (const Msg& m, juce::Point<float> pos) const
        {
            const float ly = pos.y - m.txY, lx = pos.x - m.txX;
            int tail = 0;
            for (auto& dl : m.lay)
            {
                if (ly < dl.y) return dl.src;
                if (ly < dl.y + dl.h) return dl.src + charInLine (dl, lx);
                tail = dl.src + lineLength (dl);
            }
            return tail;
        }
        SelPt posToSel (juce::Point<float> pos) const
        {
            const auto& ms = owner->msgs;
            int prev = -1;
            for (int i = 0; i < (int) ms.size(); ++i)
            {
                const auto& m = ms[(size_t) i];
                if (m.lay.empty()) continue;
                if (pos.y < m.yTop) return { i, 0 };
                if (pos.y < m.yTop + m.h) return { i, charAt (m, pos) };
                prev = i;
            }
            if (prev >= 0) return { prev, ms[(size_t) prev].dispText.length() };
            return {};
        }
        int msgIndexAt (float yy) const
        {
            const auto& ms = owner->msgs;
            for (int i = 0; i < (int) ms.size(); ++i)
                if (yy >= ms[(size_t) i].yTop && yy < ms[(size_t) i].yTop + ms[(size_t) i].h)
                    return i;
            return -1;
        }
        bool overText (juce::Point<float> pos) const
        {
            const int i = msgIndexAt (pos.y);
            if (i < 0) return false;
            const auto& m = owner->msgs[(size_t) i];
            for (auto& dl : m.lay)
            {
                if (pos.y - m.txY < dl.y || pos.y - m.txY >= dl.y + dl.h) continue;
                if (dl.segs.empty()) return false;
                const float x0 = m.txX + dl.segs.front().x;
                const float x1 = m.txX + dl.segs.back().x + dl.segs.back().w;
                return pos.x >= x0 - 4.0f && pos.x <= x1 + 6.0f;
            }
            return false;
        }

        juce::String selectionText() const
        {
            if (! hasSelection()) return {};
            auto a = selA, b = selB;
            if (selLess (b, a)) std::swap (a, b);
            juce::String out;
            const auto& ms = owner->msgs;
            bool first = true;
            for (int i = juce::jmax (0, a.msg); i <= b.msg && i < (int) ms.size(); ++i)
            {
                const auto& m = ms[(size_t) i];
                if (m.lay.empty()) continue;
                const int c0 = i == a.msg ? juce::jlimit (0, m.dispText.length(), a.chr) : 0;
                const int c1 = i == b.msg ? juce::jlimit (0, m.dispText.length(), b.chr)
                                          : m.dispText.length();
                if (! first) out << "\n\n";            // a message boundary reads as a blank line
                first = false;
                out << m.dispText.substring (c0, c1);
            }
            return out;
        }
        bool copySelection()
        {
            const auto t = selectionText();
            if (t.isEmpty()) return false;
            juce::SystemClipboard::copyTextToClipboard (t);
            flashIdx = -2; flashWord = "copied";
            flashAt = juce::Time::getMillisecondCounter();
            repaint();
            return true;
        }
        void selectAll()
        {
            const auto& ms = owner->msgs;
            int f = -1, l = -1;
            for (int i = 0; i < (int) ms.size(); ++i)
                if (! ms[(size_t) i].lay.empty()) { if (f < 0) f = i; l = i; }
            if (f < 0) return;
            selA = { f, 0 };
            selB = { l, ms[(size_t) l].dispText.length() };
            repaint();
        }
        void selectMsg (int i)
        {
            if (i < 0 || i >= (int) owner->msgs.size() || owner->msgs[(size_t) i].lay.empty()) return;
            selA = { i, 0 };
            selB = { i, owner->msgs[(size_t) i].dispText.length() };
            repaint();
        }
        void selectWordAt (SelPt p)
        {
            if (p.msg < 0 || p.msg >= (int) owner->msgs.size()) return;
            const auto& t = owner->msgs[(size_t) p.msg].dispText;
            if (t.isEmpty()) return;
            int s = juce::jlimit (0, t.length(), p.chr), e = s;
            const auto wordy = [] (juce::juce_wchar ch)
            { return ch != ' ' && ch != '\n' && ch != '\t'; };
            while (s > 0 && wordy (t[s - 1])) --s;
            while (e < t.length() && wordy (t[e])) ++e;
            if (s == e) return;
            selA = { p.msg, s };
            selB = { p.msg, e };
            repaint();
        }
        // the highlight, drawn UNDER a message's glyphs from the same layout truth
        void paintSelection (juce::Graphics& g, const Msg& m, int idx) const
        {
            if (! hasSelection() || m.lay.empty()) return;
            auto a = selA, b = selB;
            if (selLess (b, a)) std::swap (a, b);
            if (idx < a.msg || idx > b.msg) return;
            const int c0 = idx == a.msg ? a.chr : 0;
            const int c1 = idx == b.msg ? b.chr : m.dispText.length() + 1;
            g.setColour (theme::accent.withAlpha (0.30f));
            for (auto& dl : m.lay)
            {
                const int len = lineLength (dl);
                const int lo = juce::jmax (0, c0 - dl.src);
                const int hi = juce::jmin (len, c1 - dl.src);
                const bool spansLine = c0 <= dl.src && c1 > dl.src + len;
                if (hi < lo || (hi == lo && ! spansLine)) continue;
                float x0 = xAtChar (dl, lo), x1 = xAtChar (dl, hi);
                if (c1 > dl.src + len && &dl != &m.lay.back()) x1 += 5.0f;   // the newline nub
                if (x1 - x0 < 0.5f) x1 = x0 + 2.0f;
                g.fillRoundedRectangle (m.txX + x0 - 1.0f, m.txY + dl.y,
                                        x1 - x0 + 2.0f, dl.h, 2.0f);
            }
        }
        // glyphs from the same layout the selection addresses — they cannot drift
        void drawLay (juce::Graphics& g, const Msg& m) const
        {
            for (auto& dl : m.lay)
                for (auto& s : dl.segs)
                {
                    g.setFont (s.f);
                    g.setColour (s.c);
                    g.drawText (s.t, juce::Rectangle<float> (m.txX + s.x, m.txY + dl.y,
                                                             s.w + 3.0f, dl.h),
                                juce::Justification::centredLeft, false);
                }
        }

        void mouseMove (const juce::MouseEvent& e) override
        {
            int h = -1;
            for (auto& hh : hits)
                if (hh.r.contains (e.position)) { h = hh.action; break; }
            if (h != hoverAction) { hoverAction = h; repaint(); }
            setMouseCursor (h != -1 ? juce::MouseCursor::PointingHandCursor
                            : overText (e.position) ? juce::MouseCursor::IBeamCursor
                                                    : juce::MouseCursor::NormalCursor);
        }
        void mouseExit (const juce::MouseEvent&) override
        {
            if (hoverAction != -1) { hoverAction = -1; repaint(); }
            setMouseCursor (juce::MouseCursor::NormalCursor);
        }

        void mouseDown (const juce::MouseEvent& e) override
        {
            grabKeyboardFocus();
            if (e.mods.isPopupMenu()) { showContextMenu (e); return; }
            selecting = false;
            selDragged = false;
            for (auto& hh : hits)
                if (hh.r.contains (e.position)) return;   // a button press is never a drag-select
            const int clicks = e.getNumberOfClicks();
            const auto sp = posToSel (e.position);
            if (clicks >= 3)      { if (sp.msg >= 0) selectMsg (sp.msg); }
            else if (clicks == 2) selectWordAt (sp);
            else
            {
                clearSelection();
                if (sp.msg >= 0) { selA = selB = sp; selecting = true; }
            }
        }
        void mouseDrag (const juce::MouseEvent& e) override
        {
            if (! selecting) return;
            selDragged = true;
            selB = posToSel (e.position);
            auto& v = owner->vp;                // long selections pull the page along
            const auto rel = v.getLocalPoint (this, e.getPosition());
            v.autoMove = true;                  // an assisted scroll is OURS, not a user pin
            v.autoScroll (rel.x, rel.y, 24, 12);
            v.autoMove = false;
            repaint();
        }

        bool keyPressed (const juce::KeyPress& k) override
        {
            if (k == juce::KeyPress ('c', juce::ModifierKeys::commandModifier, 0))
                return copySelection();
            if (k == juce::KeyPress ('a', juce::ModifierKeys::commandModifier, 0))
            { selectAll(); return true; }
            if (k == juce::KeyPress (juce::KeyPress::escapeKey) && hasSelection())
            { clearSelection(); return true; }
            return false;
        }

        void showContextMenu (const juce::MouseEvent& e)
        {
            const int mi = msgIndexAt (e.position.y);
            juce::PopupMenu menu;
            menu.addItem (1, "Copy selection", hasSelection());
            menu.addItem (2, "Copy message",
                          mi >= 0 && (owner->msgs[(size_t) mi].dispText.isNotEmpty()
                                      || owner->msgs[(size_t) mi].text.isNotEmpty()));
            menu.addItem (3, "Select message", mi >= 0 && ! owner->msgs[(size_t) mi].lay.empty());
            menu.addItem (4, "Select all");
            menu.addSeparator();
            menu.addItem (5, "Copy whole conversation");
            juce::Component::SafePointer<Content> safe (this);
            menu.showMenuAsync (juce::PopupMenu::Options().withTargetScreenArea (
                                    { e.getScreenX(), e.getScreenY(), 1, 1 }),
                                [safe, mi] (int r)
                                { if (safe != nullptr && r != 0) safe->menuAction (r, mi); });
        }
        void menuAction (int r, int mi)
        {
            if (r == 1) copySelection();
            else if (r == 2 && mi >= 0 && mi < (int) owner->msgs.size())
            {
                const auto& m = owner->msgs[(size_t) mi];
                juce::SystemClipboard::copyTextToClipboard (
                    m.dispText.isNotEmpty() ? m.dispText : m.text);
                flashIdx = mi; flashWord = "copied";
                flashAt = juce::Time::getMillisecondCounter();
                repaint();
            }
            else if (r == 3) selectMsg (mi);
            else if (r == 4) selectAll();
            else if (r == 5)
            {
                juce::String all;
                for (auto& m : owner->msgs)
                {
                    if (m.kind == Kind::live) continue;   // components aren't text
                    if (m.kind == Kind::divider) continue;   // P65: derived lines never copy
                    all << (m.kind == Kind::user ? "you: " : m.kind == Kind::tool ? "  tool: "
                            : m.kind == Kind::action ? "  act: "
                            : m.kind == Kind::error ? "ERROR: " : m.kind == Kind::proposal ? "TAKE: " : "producer: ")
                        << m.text << "\n";
                }
                juce::SystemClipboard::copyTextToClipboard (all);
                flashIdx = -2; flashWord = "conversation copied";
                flashAt = juce::Time::getMillisecondCounter();
                repaint();
            }
        }

        void mouseUp (const juce::MouseEvent& e) override
        {
            if (e.mods.isPopupMenu()) return;
            const bool wasDrag = selecting && selDragged && hasSelection();
            selecting = false;
            selDragged = false;
            if (wasDrag) { repaint(); return; }           // the drag WAS the gesture
            for (auto& h : hits)
                if (h.r.contains (e.getPosition().toFloat()))
                {
                    if (h.action == 0 && owner->onAudition) owner->onAudition();
                    if (h.action == 1 && owner->onAccept)   owner->onAccept();
                    if (h.action == 2 && owner->onReject)   owner->onReject();
                    if (h.action == 3 && owner->onPlayTake) owner->onPlayTake();   // #17 ▶
                    if (h.action == 4 && owner->onRetry)    owner->onRetry();      // P64 ↻
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
                    static const char* starters[] = { "hum a topline over the lead",
                                                      "tighten the mix - kick and bass are fighting" };
                    if (h.action >= 10 && h.action < 12 && owner->onSuggest)
                        owner->onSuggest (starters[h.action - 10]);
                    if (h.action >= 15 && h.action < 18 && owner->onDoor)
                        owner->onDoor (h.action - 15);   // THE DOORS act, they never just type
                    if (h.action >= 600 && h.action < 800)   // P65: divider = the run's door
                    {
                        owner->toggleRun (h.action - 600);
                        return;
                    }
                    if (h.action >= 500)   // fold/unfold a long reply
                    {
                        owner->toggleExpand (h.action - 500);
                        return;
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
                const float tw2 = theme::measure (tf, flashWord) + 26.0f;
                juce::Rectangle<float> pill ((float) getWidth() * 0.5f - tw2 * 0.5f,
                                             (float) owner->vp.getViewPositionY() + 4.0f,
                                             tw2, 18.0f);
                g.setColour (theme::inset.withAlpha (0.94f));
                g.fillRoundedRectangle (pill, 9.0f);
                g.setColour (theme::good.withAlpha (0.303f));
                g.drawRoundedRectangle (pill.reduced (0.5f), 9.0f, 1.0f);
                g.setColour (theme::good.withAlpha (0.95f));
                g.setFont (tf);
                g.drawText (flashWord, pill.toNearestInt(), juce::Justification::centred);
            }
            const int w = getWidth();
            // THE COACH IS AN EMPTY-STATE, NOT A SPACE-FILLER (Chezy live 2026-07-10:
            // the hero + starter chips painted into the void ABOVE a bottom-anchored
            // live conversation — chips landed on real rows and their hit-rects stayed
            // CLICKABLE over messages). State gates the coach: it exists only while
            // the transcript is empty; geometry only sizes it.
            // THE COACH GATES ON THE CONVERSATION, NOT THE FEED (2026-08-07: the
            // boot greeting made msgs.empty() forever-false — the coach and its
            // doors were dead code on every real boot). Virgin = no USER ask yet.
            bool coachVirgin = true;
            for (auto& m : owner->msgs)
                if (m.kind == Kind::user) { coachVirgin = false; break; }
            if (coachVirgin && topOffset > 90.0f)
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
                float sy = cy + 60.0f;
                // VERTICAL FLIP (2026-08-07: Chezy's 838-logical window gives a
                // ~298px void — one pixel under the old 300 gate, doors vanished
                // on HIS machine while tall cameras sailed): short voids get
                // COMPACT title-only doors instead of nothing. Degrade, never vanish.
                const bool tallCoach = topOffset > 380.0f;
                const float doorH = tallCoach ? 34.0f : 22.0f;
                const float doorStride = tallCoach ? 40.0f : 28.0f;
                if (topOffset > 250.0f)
                {   // THE DOORS (rebrand 31 §1a): the coach leads with FEATURE
                    // doors — buried rails surfaced as first-class verbs that
                    // ACT on click; the ask chips below only teach the talkback.
                    struct Door { const char* title; const char* sub; };
                    static const Door doors[] = {
                        { "BRING A SONG", "drop any mp3 or wav - it lands as an editable session" },
                        { "MAKE A TRACK", "one click - a full take lands free, instant, offline" },
                        { "FINISH THIS",  "arrange, mix and master what is already here" },
                    };
                    for (int i = 0; i < 3; ++i)
                    {
                        const bool hov = hoverAction == 15 + i;
                        const float dw = juce::jmin (300.0f, (float) w - 24.0f);
                        juce::Rectangle<float> door ((float) w * 0.5f - dw * 0.5f, sy, dw, doorH);
                        // pass 2: the doors wear the design's OWN machined-glass
                        // card (deep seat + sheen + rim) — accent lives in a spine
                        // and the hover light, never a wireframe outline
                        theme::card (g, door,
                                     hov ? theme::panelHi.interpolatedWith (theme::accent, 0.16f)
                                         : theme::panelHi,
                                     10.0f, hov ? 1.25f : 0.85f);
                        g.setColour (theme::accent.withAlpha (hov ? 0.95f : 0.60f));
                        g.fillRoundedRectangle (door.getX() + 1.5f, door.getCentreY() - 7.0f,
                                                2.5f, 14.0f, 1.2f);
                        const auto di = door.toNearestInt();
                        g.setColour (hov ? theme::text : theme::text.withAlpha (0.85f));
                        g.setFont (theme::caps (8.0f));
                        if (tallCoach)
                        {
                            g.drawText (doors[i].title, di.getX(), di.getY() + 4, di.getWidth(), 12,
                                        juce::Justification::centred);
                            g.setColour (theme::textMute.withAlpha (0.85f));
                            g.setFont (theme::ui (9.5f));
                            g.drawText (doors[i].sub, di.getX(), di.getY() + 18, di.getWidth(), 11,
                                        juce::Justification::centred);
                        }
                        else   // compact: the title carries the door alone
                            g.drawText (doors[i].title, di, juce::Justification::centred);
                        hits.push_back ({ door, 15 + i });
                        sy += doorStride;
                    }
                }
                if (topOffset > 460.0f)   // the ask chips need their own clearance
                {
                    static const char* starters[] = { "hum a topline over the lead",
                                                      "tighten the mix - kick and bass are fighting" };
                    sy += 6.0f;
                    g.setFont (theme::ui (11.0f));
                    for (int i = 0; i < 2; ++i)
                    {
                        const bool hov = hoverAction == 10 + i;
                        const auto tw = theme::measure (theme::ui (11.0f), starters[i]) + 30.0f;
                        juce::Rectangle<float> chip ((float) w * 0.5f - tw * 0.5f, sy, tw, 24.0f);
                        // glass pills: tinted body, quiet rim, bright ink
                        g.setColour (theme::accent.withAlpha (hov ? 0.16f : 0.09f));
                        g.fillRoundedRectangle (chip, 12.0f);
                        g.setColour (theme::accent.withAlpha (hov ? 0.40f : 0.22f));
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
                m.yTop = y;                     // the selection's y-map rides the paint walk
                if (m.folded) continue;         // P65: folded members paint nothing
                if (m.kind == Kind::divider)
                {   // P65: the folded run's one-line summary (click = expand in place)
                    const bool dWarn = m.meta.contains ("warn");
                    juce::Rectangle<float> row (14.0f, y + 3.0f, (float) w - 28.0f, m.h - 6.0f);
                    g.setColour (theme::inset.withAlpha (0.55f));
                    g.fillRoundedRectangle (row, 9.0f);
                    g.setColour ((dWarn ? theme::warn : theme::textMute).withAlpha (0.78f));
                    g.setFont (theme::caps (7.5f));
                    g.drawText (juce::String (m.expanded ? "v  " : ">  ") + m.text,
                                row.toNearestInt().reduced (10, 0),
                                juce::Justification::centredLeft);
                    hits.push_back ({ row, 600 + m.runId });
                    y += m.h;
                    continue;
                }
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
                    juce::Rectangle<float> card (10.0f, y, cardW, m.h - 10.0f);
                    theme::card (g, card, theme::panelHi, 9.0f);
                    g.setColour (theme::good.withAlpha (0.303f));
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
                    g.drawText ("TAKE", band.reduced (24, 0).toNearestInt(), juce::Justification::centredLeft);
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
                    {   // body text from the selection layout (one truth with the highlight)
                        auto ta = card.reduced (14.0f, 8.0f).withTrimmedTop (textTop)
                                      .withTrimmedBottom (38.0f);
                        m.txX = ta.getX(); m.txY = ta.getY();
                        juce::Graphics::ScopedSaveState ss (g);
                        g.reduceClipRegion (ta.getSmallestIntegerContainer());
                        paintSelection (g, m, (int) (&m - &owner->msgs[0]));
                        drawLay (g, m);
                    }
                    // action row: Audition (outline) / Accept (filled) / Reject (outline)
                    auto btnRow = card.removeFromBottom (40.0f).reduced (10.0f, 6.0f);
                    const char* labels[] = { "Audition", "KEEP", "PASS" };
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
                    g.setColour (edge.withAlpha (0.248f));
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
                    g.setColour (edge.withAlpha (0.248f));
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
                    g.setColour (theme::agent.withAlpha (0.275f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (theme::agent);
                    g.setFont (theme::ui (10.5f, juce::Font::bold));
                    g.drawText ("THE PRODUCER HEARS", card.reduced (12.0f, 6.0f).toNearestInt(),
                                juce::Justification::topLeft);
                    auto lines = juce::StringArray::fromLines (m.text);
                    // BIGGER + ADAPTIVE: the tensor fills the card width (see tensorRowH)
                    const float rowH = tensorRowH (cardW, m.text);
                    m.txX = card.getX() + 13.0f;
                    m.txY = card.getY() + 24.0f;
                    paintSelection (g, m, (int) (&m - &owner->msgs[0]));
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
                    g.setColour (theme::accentB.withAlpha (0.22f));
                    g.drawRoundedRectangle (card.reduced (0.5f), 9.0f, 1.0f);
                    auto lines = juce::StringArray::fromLines (m.text);
                    juce::String head = lines.isEmpty() ? juce::String ("REPORT") : lines[0];
                    if (head.startsWith ("[") && head.contains ("]"))
                        head = head.substring (1).upToFirstOccurrenceOf ("]", false, false).toUpperCase();
                    g.setColour (theme::accentB);
                    g.setFont (theme::ui (9.5f, juce::Font::bold));
                    g.drawText (head, card.reduced (12.0f, 5.0f).toNearestInt(), juce::Justification::topLeft);
                    m.txX = card.getX() + 12.0f;
                    m.txY = card.getY() + 20.0f;
                    paintSelection (g, m, (int) (&m - &owner->msgs[0]));
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
                        g.setColour (vc.withAlpha (0.248f));
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
                        m.txX = chip.getX() + 18.0f;
                        m.txY = y;
                        paintSelection (g, m, idx);
                        g.setColour (theme::textDim.brighter (0.1f));
                        g.setFont (f2);
                        g.drawText (m.text, chip.withTrimmedLeft (18.0f).toNearestInt(),
                                    juce::Justification::centredLeft);
                    }
                    else
                    {
                        m.txX = 10.0f + juce::jmax (0.0f, (cardW - m.layW) * 0.5f);
                        m.txY = y;
                        paintSelection (g, m, idx);
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
                    g.setColour (theme::agent.withAlpha (0.193f));
                    g.drawRoundedRectangle (pill.reduced (0.5f), 9.0f, 1.0f);
                    g.setColour (theme::agent);
                    g.fillEllipse (pill.getX() + 9.0f, pill.getCentreY() - 2.5f, 5.0f, 5.0f);
                    m.txX = pill.getX() + 21.0f;
                    m.txY = y;
                    paintSelection (g, m, (int) (&m - &owner->msgs[0]));
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
                    g.setColour (fc.withAlpha (0.209f));
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
                    const bool collapsible = m.layH > collapseTextH + 40.0f;
                    const bool clipped = collapsible && ! m.expanded;
                    const float shownH = clipped ? collapseTextH : m.layH;
                    const float ch = shownH + 16.0f + (collapsible ? 18.0f : 0.0f);
                    const float bw = juce::jmin (cardW * 0.87f, m.layW + 28.0f);
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
                        g.setColour (theme::accent.withAlpha (0.248f));
                        g.drawRoundedRectangle (card.reduced (0.5f), 10.0f, 1.0f);
                    }
                    else if (err)
                    {
                        theme::card (g, card, theme::bad.withAlpha (0.13f), 10.0f, 0.0f);
                        g.setColour (theme::bad.withAlpha (0.85f));
                        g.fillRoundedRectangle (card.getX(), card.getY() + 3.0f, 3.0f, card.getHeight() - 6.0f, 1.5f);
                        if (m.meta.contains ("retryable"))
                        {   // P64: weather, not brokenness — the same ask, one click
                            const bool busy = owner->agentBusy;
                            const auto f = theme::caps (7.5f);
                            const float rw2 = theme::measure (f, "RETRY") + 22.0f;
                            juce::Rectangle<float> chip (card.getRight() - rw2 - 8.0f,
                                                         card.getY() + 5.0f, rw2, 15.0f);
                            g.setColour (theme::accent.withAlpha (busy ? 0.10f : 0.22f));
                            g.fillRoundedRectangle (chip, 7.5f);
                            g.setColour (theme::accent.withAlpha (busy ? 0.30f : 0.85f));
                            g.drawRoundedRectangle (chip.reduced (0.5f), 7.5f, 1.0f);
                            g.setFont (f);
                            g.drawText ("RETRY", chip.toNearestInt(), juce::Justification::centred);
                            hits.push_back ({ chip, 4 });
                        }
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
                    m.txX = textArea.getX();
                    m.txY = textArea.getY();
                    {
                        juce::Graphics::ScopedSaveState ss (g);
                        g.reduceClipRegion (textArea.getSmallestIntegerContainer());
                        paintSelection (g, m, idx);
                        drawLay (g, m);
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
                            ? "show all " + juce::String ((int) m.lay.size()) + " lines" : "collapse";
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
                    drawCopied (g, card, idx);
                }
                y += m.h;
            }
        }
    };

    // ---- THE TEXT ENGINE (selection-grade) ----------------------------------
    // The agent writes essays — headings, bullets and table rows get typographic
    // treatment so a long reply reads as a document, not a wall. The engine emits
    // wrapped DispLines of styled Segs (real geometry) instead of a TextLayout:
    // measure() builds them, paint() draws them, the selection addresses them —
    // one truth, so the highlight can never drift off the glyphs.
    struct Run { juce::String t; juce::Font f; juce::Colour c; };

    // INLINE MARKDOWN (CC4-I4 firing 104): agents SPEAK markdown — raw asterisks
    // and backticks in the bubbles were the single loudest 'Windows 98' tell.
    // Parses **bold** and `code` (code = mono, brand-tinted) inside any line.
    static void inlineRuns (std::vector<Run>& out, const juce::String& ln,
                            const juce::Font& f, juce::Colour base)
    {
        int i = 0;
        const auto flush = [&] (const juce::String& seg, bool bold, bool code)
        {
            if (seg.isEmpty()) return;
            if (code)      out.push_back ({ seg, theme::mono (f.getHeight() - 2.0f, juce::Font::bold),
                                            theme::accentB });
            else if (bold) out.push_back ({ seg, theme::ui (f.getHeight(), juce::Font::bold),   // theme bold face
                                            base.brighter (0.22f) });                           // (f.boldened() no-ops
            else           out.push_back ({ seg, f, base });                                    //  without a bold variant)
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
        flush (plain, false, false);
    }

    // one SOURCE line -> styled runs (headings, bullets, numbered lists, tables)
    static std::vector<Run> lineRuns (const juce::String& ln, juce::Colour base)
    {
        std::vector<Run> runs;
        const int pipes = ln.length() - ln.removeCharacters ("|").length();
        const auto body = ln.trimStart();
        const bool numbered = body.length() > 2 && juce::CharacterFunctions::isDigit (body[0])
                              && (body[1] == '.' || (juce::CharacterFunctions::isDigit (body[1]) && body[2] == '.'));
        if (ln.startsWith ("# ") || ln.startsWith ("## ") || ln.startsWith ("### "))
            inlineRuns (runs, ln.fromFirstOccurrenceOf (" ", false, false).trim(),
                        theme::ui (12.5f, juce::Font::bold), base.brighter (0.18f));
        else if (body.startsWith ("- ") || body.startsWith ("* "))
            inlineRuns (runs, juce::String::fromUTF8 ("\xe2\x80\xa2 ") + body.substring (2),
                        theme::ui (12.0f), base.withMultipliedAlpha (0.92f));
        else if (numbered)
        {
            runs.push_back ({ body.upToFirstOccurrenceOf (".", true, false) + " ",
                              theme::ui (12.0f, juce::Font::bold), theme::accent.withAlpha (0.9f) });
            inlineRuns (runs, body.fromFirstOccurrenceOf (".", false, false).trimStart(),
                        theme::ui (12.0f), base);
        }
        else if (pipes >= 2)                          // table row: mono, dimmer, denser
            runs.push_back ({ ln, theme::mono (9.5f), base.withMultipliedAlpha (0.78f) });
        else
            inlineRuns (runs, ln, theme::ui (12.5f), base);
        return runs;
    }

    // greedy word-wrap of styled runs into display lines. Soft wraps do NOT mint
    // newlines in dispText (copy gives logical lines, like a browser); hard source
    // breaks do. plain=true skips markdown (proposal bodies are prose).
    static void layoutText (Msg& m, const juce::String& text, juce::Colour base,
                            float maxW, bool plain = false)
    {
        m.lay.clear(); m.dispText.clear();
        m.layW = 0.0f; m.layH = 0.0f;
        maxW = juce::jmax (24.0f, maxW);
        auto srcLines = juce::StringArray::fromLines (text);
        float y = 0.0f;
        for (int li = 0; li < srcLines.size(); ++li)
        {
            std::vector<Run> runs;
            if (plain) runs.push_back ({ srcLines[li], theme::ui (12.0f), base });
            else       runs = lineRuns (srcLines[li], base);
            DispLine cur; cur.y = y; cur.src = m.dispText.length();
            float x = 0.0f, lineH = (plain ? 12.0f : 12.5f) + 3.2f;
            const auto commitLine = [&] ()
            {
                cur.h = lineH;
                for (auto& s : cur.segs) m.dispText << s.t;
                m.layW = juce::jmax (m.layW, x);
                y += cur.h;
                m.lay.push_back (std::move (cur));
                cur = {}; cur.y = y; cur.src = m.dispText.length();
                x = 0.0f; lineH = (plain ? 12.0f : 12.5f) + 3.2f;
            };
            const auto append = [&] (const juce::String& tok, const juce::Font& f,
                                     juce::Colour c, float tw)
            {
                if (! cur.segs.empty() && cur.segs.back().f == f && cur.segs.back().c == c)
                { cur.segs.back().t << tok; cur.segs.back().w += tw; }
                else
                    cur.segs.push_back ({ tok, f, c, x, tw });
                x += tw;
                lineH = juce::jmax (lineH, f.getHeight() + 3.2f);
            };
            for (auto& r : runs)
            {
                int i = 0;
                const int n = r.t.length();
                while (i < n)
                {   // token = a word plus its trailing spaces (spaces bind backwards)
                    int e = i;
                    while (e < n && r.t[e] != ' ') ++e;
                    while (e < n && r.t[e] == ' ') ++e;
                    juce::String tok = r.t.substring (i, e);
                    i = e;
                    float tw = theme::measure (r.f, tok);
                    if (x > 0.0f && x + tw > maxW) commitLine();
                    while (tw > maxW && tok.length() > 1)
                    {   // an unbreakable monster: hard-chop to the pane
                        int keep = 1;
                        while (keep < tok.length()
                               && theme::measure (r.f, tok.substring (0, keep + 1)) <= maxW)
                            ++keep;
                        append (tok.substring (0, keep), r.f, r.c,
                                theme::measure (r.f, tok.substring (0, keep)));
                        commitLine();
                        tok = tok.substring (keep);
                        tw = theme::measure (r.f, tok);
                    }
                    append (tok, r.f, r.c, tw);
                }
            }
            commitLine();
            if (li + 1 < srcLines.size()) m.dispText << "\n";
        }
        m.layH = y;
    }

    // fixed-pitch line lists (reports, tensors, single-line kinds) — same truth,
    // no wrapping (their painters clip; the copy still carries the whole line)
    template <typename ColourFor>
    static void layLines (Msg& m, const juce::StringArray& lines, const juce::Font& f,
                          float y0, float pitch, ColourFor&& colFor)
    {
        m.lay.clear(); m.dispText.clear();
        m.layW = 0.0f;
        float y = y0;
        for (int i = 0; i < lines.size(); ++i)
        {
            DispLine dl; dl.y = y; dl.h = pitch; dl.src = m.dispText.length();
            if (lines[i].isNotEmpty())
            {
                Seg s; s.t = lines[i]; s.f = f; s.c = colFor (i, lines[i]);
                s.x = 0.0f; s.w = theme::measure (f, s.t);
                m.layW = juce::jmax (m.layW, s.w);
                dl.segs.push_back (std::move (s));
            }
            m.dispText << lines[i];
            if (i + 1 < lines.size()) m.dispText << "\n";
            m.lay.push_back (std::move (dl));
            y += pitch;
        }
        m.layH = y - y0;
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
        m.lay.clear(); m.dispText.clear(); m.layW = 0.0f; m.layH = 0.0f;
        if (m.folded) { m.h = 0.0f; return; }            // P65: folded runs cost nothing
        if (m.wasThink && m.kind == Kind::agent)
        {   // THE MIND IS A WHISPER (2026-08-02): reasoning renders as ONE
            // slim dim italic line - never a stacked wall of raw pulses. The
            // cosmo score carries the "working" feeling; this line carries
            // the tail of the thought.
            m.h = 18.0f;
            auto one = m.text.replaceCharacter ('\n', ' ');
            layLines (m, juce::StringArray { one },
                      theme::ui (9.5f, juce::Font::italic), 14.0f, 13.0f,
                      [] (int, const juce::String&)
                      { return theme::agent.withAlpha (0.55f); });
            return;
        }
        if (m.kind == Kind::divider)
        {   // P65: one fixed-height honest line per folded run
            m.h = 24.0f;
            m.dispText = m.text;
            m.layW = (float) w; m.layH = 14.0f;
            return;
        }
        if (m.kind == Kind::live)        m.h = (float) m.liveH + 16.0f;
        else if (m.kind == Kind::status)
        {
            m.h = 15.0f;   // tight: runs recede
            const bool verdict = m.text.startsWith ("you ACCEPTED") || m.text.startsWith ("you REJECTED");
            layLines (m, juce::StringArray { m.text },
                      verdict ? theme::ui (9.0f, juce::Font::bold) : theme::ui (9.5f),
                      0.0f, m.h, [] (int, const juce::String&) { return theme::textDim; });
        }
        else if (m.kind == Kind::analysis) m.h = 66.0f;
        else if (m.kind == Kind::variants) m.h = 38.0f + 26.0f * (float) (m.meta.size() / 4);
        else if (m.kind == Kind::report)
        {
            auto lines = juce::StringArray::fromLines (m.text);
            m.h = 32.0f + 13.0f * (float) lines.size();
            if (! lines.isEmpty() && lines[0].startsWith ("[") && lines[0].contains ("]"))
                lines.set (0, lines[0].fromFirstOccurrenceOf ("] ", false, false));
            layLines (m, lines, theme::mono (10.0f), 20.0f, 13.0f,
                      [] (int, const juce::String& row)
                      {
                          return row.contains ("PASS") || row.contains ("CLEAN")
                                     ? theme::good.withAlpha (0.9f)
                                 : row.contains ("FAIL") || row.contains ("[X1]") ? theme::warn
                                 : theme::textDim;
                      });
        }
        else if (m.kind == Kind::perception)
        {
            const float rowH = tensorRowH ((float) w - 20.0f, m.text);
            auto lines = juce::StringArray::fromLines (m.text);
            m.h = 34.0f + rowH * (float) lines.size();
            const int n = lines.size();
            layLines (m, lines, theme::mono (rowH - 2.5f), 24.0f, rowH,
                      [n] (int i, const juce::String&)
                      {
                          const float t = n > 2 ? (float) (i - 1) / (float) juce::jmax (1, n - 2) : 0.0f;
                          return i == 0 ? theme::textMute
                                        : juce::Colour::fromHSV (0.58f - 0.55f * (1.0f - t), 0.55f, 0.95f, 0.9f);
                      });
        }
        else if (m.kind == Kind::tool)
        {
            m.h = 25.0f;
            layLines (m, juce::StringArray { m.text }, theme::mono (10.5f), 1.0f, 17.0f,
                      [] (int, const juce::String&) { return theme::textDim; });
        }
        else if (m.kind == Kind::action) m.h = 28.0f;
        else if (m.kind == Kind::proposal)
        {
            const float wave = m.peaks.empty() ? 0.0f : 30.0f;
            layoutText (m, m.text, theme::text, (float) (w - 20) - 28.0f, true);
            m.h = m.layH + 24.0f + 40.0f + 16.0f + 10.0f + (m.meta.isEmpty() ? 0.0f : 22.0f) + wave;
        }
        else
        {
            const auto base = m.kind == Kind::error ? theme::warn.brighter (0.1f) : theme::text;
            layoutText (m, m.text, base, (float) (w - 20) * 0.87f - 26.0f);
            const bool collapsible = m.layH > collapseTextH + 40.0f;
            const float shown = (collapsible && ! m.expanded) ? collapseTextH : m.layH;
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
