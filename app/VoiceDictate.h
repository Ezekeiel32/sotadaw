// VoiceDictate.h — THE VOICE MODE v3 (Chezy 2026-07-16, the final contract:
// "the transcribed words need to appear in the prompt bar in REALTIME! no
// send until the user presses send!"). Toggle it (mic click or /voice) and
// just TALK: while you speak, the current utterance re-transcribes every
// ~0.5s and PAINTS LIVE into the prompt bar (onPartial); a ~1.1s pause
// FOLDS those words into the host's ledger (onFinalSent) and the beam-5
// quality pass later upgrades that exact segment (onFinal, by gen) — words
// APPEND forever, they are never replaced by the next sentence. NOTHING is
// ever sent — Send belongs to the user.
//
// The machinery: arecord runs CONTINUOUSLY while the mode is on (no gap
// between utterances); a VAD state machine on the live RMS (adaptive noise
// floor, ~200ms speech onset, 0.37s pre-roll, ~1.1s end-of-speech hangover)
// delimits utterances by byte offsets in the growing raw file; partial
// slices ride the warm ear's file IPC at beam 1 (the realtime lane), finals
// at beam 5. Newest-wins: a superseded partial's answer is ignored by gen
// ordering. A silent mic diagnoses itself ("check the input device") instead
// of playing dead. State is MATERIAL: waiting = green breath, speaking =
// red level ring, a violet orbit while any transcription is in flight.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class VoiceMicButton : public juce::Button, private juce::Timer
{
public:
    std::function<void (const juce::String&)> onPartial;      // live words, replace the tail
    std::function<void (int)> onFinalSent;                    // a final left for the ear: FOLD the tail NOW
    std::function<void (int, const juce::String&)> onFinal;   // beam-5 answer for that gen ("" = keep folded words)
    std::function<void (const juce::String&)> onNote;         // honest one-liners -> activity log
    std::function<void()> onStateChange;                      // host mirrors the placeholder

    enum class Phase { off, waiting, speaking, thinking };

    VoiceMicButton() : juce::Button ("voice")
    {
        setTooltip ("voice mode (/voice) - click, then just talk: a pause sends each ask; "
                    "click again to exit (local whisper, no cloud)");
    }
    ~VoiceMicButton() override
    {
        // THE DYING-CALLBACK LAW (ASAN 2026-07-16, the corruption writer): this
        // destructor runs mid-~MainComponent, when sibling components (promptBox!)
        // may already be corpses — hardCancel used to fire onStateChange, whose
        // host lambda wrote into the freed TextEditor's String: a heap-poisoning
        // UAF that crashed every shutdown-after (Chezy's 10:17 crash, the ghost
        // rig's hangs/SEGVs/tcache aborts). A dying component calls NOBODY.
        onPartial = nullptr;
        onFinalSent = nullptr;
        onFinal = nullptr;
        onNote = nullptr;
        onStateChange = nullptr;
        hardCancel (false);
        if (server.isRunning()) server.kill();   // the warm ear dies with the window
    }

    void setRoot (juce::File r)
    {
        root = r;
        if (const char* e = std::getenv ("SOTADAW_IPC"))   // rigs isolate their IPC yard
            ipc = juce::File (juce::String (e));
        else
            ipc = r.getChildFile ("agent/ipc");
    }
    juce::File takeFile() const { return ipc.getChildFile ("voice_take.raw"); }   // rig feed door

    // THE WARM BOOT (Chezy live 2026-07-16: "took 15 seconds to transcribe one
    // word" — the whisper model LOAD was the whole latency; every partial sent
    // during it died unanswered). The ear now loads WITH THE APP and stays
    // resident for the app's life (the server ppid-watches us and dies with the
    // window; the dtor kills it on clean exit). Auto-gated: only boxes that have
    // actually used voice pay the resident model; SOTADAW_STT_PREWARM=1 forces,
    // =0 forbids; sandbox rigs never hold one.
    void prewarm()
    {
        if (root == juce::File() || voiceMode) return;
        if (std::getenv ("SOTADAW_SANDBOX") != nullptr) return;
        const char* pw = std::getenv ("SOTADAW_STT_PREWARM");
        if (pw != nullptr && juce::String (pw) == "0") return;
        if ((pw == nullptr || juce::String (pw) != "1")
            && ! stampFile().existsAsFile()
            && ! ipc.getChildFile ("voice_take.raw").existsAsFile()) return;
        if (ensureServer() && onNote)
            onNote ("[voice] warming the ear in the background - the mic will be instant");
    }

    Phase state() const
    {
        if (voiceMode) return phase;
        return pendingJobs > 0 ? Phase::thinking : Phase::off;
    }
    bool inVoiceMode() const { return voiceMode; }

    void clicked() override
    {
        if (voiceMode)             enterOrExit (false);   // soft exit: pending words still land
        else if (pendingJobs > 0)  hardCancel (true);     // post-exit limbo: click = give up the wait
        else                       enterOrExit (true);
    }

    void paintButton (juce::Graphics& g, bool over, bool) override
    {
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        const auto ph = state();
        const float ms = (float) (juce::Time::getMillisecondCounter() % 100000u);
        const auto tint = ph == Phase::speaking ? theme::bad
                        : ph == Phase::waiting  ? theme::good
                        : ph == Phase::thinking ? theme::accent
                        : over ? theme::text : theme::textDim;
        if (ph == Phase::speaking)
            theme::glowRing (g, r, theme::bad, 5.0f + 7.0f * lvl, 0.8f + 1.2f * lvl);
        else if (ph == Phase::waiting)
        {   // the open ear: a slow green breath, nudged by the room's own level
            const float breath = 0.5f + 0.5f * std::sin (ms * 0.0021f);
            theme::glowRing (g, r, theme::good, 4.5f + 2.5f * breath + 4.0f * lvl,
                             0.5f + 0.5f * breath);
        }
        else if (ph == Phase::thinking || over)
            theme::glowRing (g, r, theme::accent, 6.0f, ph == Phase::thinking ? 1.1f : 0.7f);
        g.setColour (theme::inset.withAlpha (0.96f));
        g.fillRoundedRectangle (r, 8.0f);
        g.setGradientFill ({ juce::Colours::white.withAlpha (0.07f), r.getTopLeft(),
                             juce::Colours::white.withAlpha (0.0f),
                             { r.getX(), r.getY() + r.getHeight() * 0.5f }, false });
        g.fillRoundedRectangle (r, 8.0f);
        g.setColour ((ph == Phase::speaking ? theme::bad
                      : ph == Phase::waiting ? theme::good : theme::accent)
                         .withAlpha (ph == Phase::off ? (over ? 0.45f : 0.18f) : 0.75f));
        g.drawRoundedRectangle (r.reduced (0.5f), 8.0f, 1.0f);

        // the mic: capsule + stirrup + stem, drawn (never a font glyph)
        const auto c = r.getCentre();
        const float s = juce::jmin (r.getWidth(), r.getHeight());
        const float capW = s * 0.26f, capH = s * 0.42f;
        g.setColour (tint.withAlpha (ph == Phase::off ? 0.85f : 1.0f));
        g.fillRoundedRectangle (c.x - capW * 0.5f, c.y - capH * 0.78f, capW, capH, capW * 0.5f);
        juce::Path st1;                                        // the stirrup
        st1.addArc (c.x - capW * 0.92f, c.y - capH * 0.55f, capW * 1.84f, capH * 1.06f,
                    juce::MathConstants<float>::pi * 0.62f,
                    juce::MathConstants<float>::pi * 1.38f, true);
        g.strokePath (st1, { s * 0.055f, juce::PathStrokeType::curved,
                             juce::PathStrokeType::rounded });
        g.drawLine (c.x, c.y + capH * 0.50f, c.x, c.y + capH * 0.74f, s * 0.055f);
        g.drawLine (c.x - capW * 0.55f, c.y + capH * 0.78f,
                    c.x + capW * 0.55f, c.y + capH * 0.78f, s * 0.055f);

        if (ph == Phase::speaking)
        {   // live level: two side arcs breathe with the voice
            for (int k = 0; k < 2; ++k)
            {
                const float side = k == 0 ? -1.0f : 1.0f;
                const float amp = juce::jlimit (0.12f, 1.0f, lvl * (k == 0 ? 1.0f : 0.8f));
                g.setColour (theme::bad.withAlpha (0.25f + 0.6f * amp));
                juce::Path arc;
                arc.addArc (c.x + side * capW * (1.1f + 0.5f * amp) - 2.0f, c.y - capH * 0.5f,
                            4.0f, capH * 0.72f,
                            side < 0 ? juce::MathConstants<float>::pi * 1.15f
                                     : juce::MathConstants<float>::pi * 0.15f,
                            side < 0 ? juce::MathConstants<float>::pi * 1.85f
                                     : juce::MathConstants<float>::pi * 0.85f, true);
                g.strokePath (arc, { 1.3f + amp, juce::PathStrokeType::curved,
                                     juce::PathStrokeType::rounded });
            }
        }
        if (pendingJobs > 0)
        {   // the orbit: a transcription in flight (rides ANY phase)
            const float ph2 = (float) (juce::Time::getMillisecondCounter() % 1100u)
                            / 1100.0f * juce::MathConstants<float>::twoPi;
            juce::Path orbit;
            orbit.addArc (r.getX() + 3.0f, r.getY() + 3.0f,
                          r.getWidth() - 6.0f, r.getHeight() - 6.0f,
                          ph2, ph2 + juce::MathConstants<float>::pi * 0.9f, true);
            g.setColour (theme::accent.withAlpha (0.85f));
            g.strokePath (orbit, { 1.6f, juce::PathStrokeType::curved,
                                   juce::PathStrokeType::rounded });
        }
    }

private:
    static juce::File stampFile()   // "this box uses voice" -> future boots prewarm
    {
        return juce::File::getSpecialLocation (juce::File::userHomeDirectory)
                 .getChildFile (".config/sotadaw/voice_used");
    }

    // THE WARM EAR: spawn the whisper server the moment the mode opens, so the
    // model loads WHILE the user speaks their first ask — each utterance then
    // costs only the decode (~0.6s measured). flags 0 = no pipes: HuggingFace
    // download bars must never fill a pipe we forgot to drain. Answers ride
    // file IPC (voice_req/res.json, atomic renames, gen tokens).
    bool ensureServer()   // returns true when it had to SPAWN (a cold ear)
    {
        if (server.isRunning() || root == juce::File()) return false;
        auto py = root.getChildFile (".venv/bin/python");
        const auto esc = [] (const juce::String& s) { return s.replace ("'", "'\\''"); };
        // stderr lands in a LOG (a silent /dev/null server was undebuggable live).
        // The resident ear lives as long as the APP (24h idle cap is a backstop;
        // the server exits when its parent dies) — a 600s self-exit used to make
        // the SECOND ask of the evening pay the 10s model load all over again.
        const auto cmd = "SOTADAW_STT_IDLE_S=\"${SOTADAW_STT_IDLE_S:-86400}\" "
                         "exec '" + esc (py.existsAsFile() ? py.getFullPathName()
                                                           : juce::String ("python3"))
                       + "' '" + esc (root.getChildFile ("tools/voice_dictate.py").getFullPathName())
                       + "' --serve --dir '" + esc (ipc.getFullPathName())
                       + "' >> '" + esc (ipc.getChildFile ("voice_ear.log").getFullPathName())
                       + "' 2>&1";
        return server.start (juce::StringArray { "/bin/bash", "-c", cmd }, 0);
    }

    void enterOrExit (bool enter)
    {
        if (! enter)
        {   // soft exit: the ear closes; an utterance already transcribing still
            // lands in the prompt (words are never lost — and never sent)
            voiceMode = false;
            phase = Phase::off;
            reapRecorder();
            stopTimerIfIdle();
            setTooltip ("voice mode (/voice) - click, then just talk: your words land in "
                        "the prompt as you speak; Send stays yours (local whisper, no cloud)");
            if (onNote) onNote ("[voice] voice mode off");
            if (onStateChange) onStateChange();
            repaint();
            return;
        }
        if (root == juce::File()) return;
        const bool coldEar = ensureServer();
        ipc.getChildFile ("voice_req.json").deleteFile();   // ancient answers can't haunt
        ipc.getChildFile ("voice_res.json").deleteFile();
        rawFile = ipc.getChildFile ("voice_take.raw");
        rawFile.getParentDirectory().createDirectory();
        rawFile.deleteFile();
        if (! startRecorder())
        {
            if (onNote) onNote ("[voice] could not start the mic (parec/arecord/ffmpeg missing?)");
            return;
        }
        if (onNote) onNote ("[voice] ear: " + backend);
        stampFile().getParentDirectory().createDirectory();
        stampFile().create();                     // this box talks: prewarm from now on
        lastGrowth = juce::Time::getMillisecondCounter();
        readPosGrowthMark = 0;                    // fresh take: last session's size must not haunt
        recRestarted = false;
        voiceMode = true;
        phase = Phase::waiting;
        t0 = juce::Time::getMillisecondCounter();
        readPos = 0;
        lvl = 0.0f;
        noiseFloor = 0.004f;
        maxRmsSeen = 0.0f;
        silenceWarned = false;
        speechTicks = silenceTicks = ticksSinceReq = 0;
        uttStart = -1;
        lastAdoptedGen = gen.load();
        awaitingGen = -1;
        setTooltip ("voice mode ON - your words land in the prompt as you speak; "
                    "Send stays yours; click to exit");
        startTimerHz (24);
        if (onNote) onNote (coldEar
            ? "[voice] voice mode ON - warming the ear (~10s, first use) - talk away, "
              "your words will catch up"
            : "[voice] voice mode ON - talk; words land in the prompt; press Send when ready");
        if (onStateChange) onStateChange();
        repaint();
    }

    // a REAL input, never an output monitor: the default source is trusted only
    // when it isn't a .monitor; otherwise the first non-monitor source wins.
    // (A monitor default makes "voice" transcribe the SONG — the silent trap.)
    static juce::String pickSource()
    {
        juce::ChildProcess p;
        if (p.start (juce::StringArray { "/usr/bin/pactl", "get-default-source" }))
        {
            const auto def = p.readAllProcessOutput().trim();
            p.waitForProcessToFinish (500);
            if (def.isNotEmpty() && ! def.endsWith (".monitor")) return def;
        }
        juce::ChildProcess l;
        if (l.start (juce::StringArray { "/usr/bin/pactl", "list", "sources", "short" }))
        {
            const auto lines = juce::StringArray::fromLines (l.readAllProcessOutput());
            l.waitForProcessToFinish (500);
            for (auto& ln : lines)
            {
                const auto cols = juce::StringArray::fromTokens (ln, "\t ", "");
                if (cols.size() > 1 && ! cols[1].endsWith (".monitor")) return cols[1];
            }
        }
        return {};
    }

    bool startRecorder()
    {
        if (std::getenv ("SOTADAW_VOICE_FAKEREC") != nullptr)
        {   // rig seam: the camera writes the take file itself (no audio device)
            rawFile.create();
            return true;
        }
        // BACKEND LADDER (Chezy live 2026-07-16: arecord through the pipewire-ALSA
        // shim STALLS TO ZEROS then dies beside the running JUCE/ALSA engine —
        // his take: 1s of real voice, then digital silence). parec is a native
        // PipeWire client and shares the card honestly — it leads; arecord and
        // ffmpeg remain the fallbacks for parec-less boxes.
        const auto q = rawFile.getFullPathName().replace ("'", "'\\''");
        juce::String cmd;
        if (juce::File ("/usr/bin/parec").existsAsFile())
        {
            const auto src = pickSource();
            backend = "parec" + (src.isNotEmpty() ? " <- " + src : juce::String());
            // --latency-msec: parec's default 2s flush starves a 24Hz VAD — the
            // take must GROW in near-realtime for words to paint while speaking
            cmd = "exec parec --format=s16le --rate=16000 --channels=1 --latency-msec=40"
                  + (src.isNotEmpty() ? " --device='" + src.replace ("'", "'\\''") + "'"
                                      : juce::String())
                  + " > '" + q + "'";
        }
        else if (juce::File ("/usr/bin/arecord").existsAsFile())
        {
            backend = "arecord";
            cmd = "exec arecord -q -t raw -f S16_LE -r 16000 -c 1 > '" + q + "'";
        }
        else
        {
            backend = "ffmpeg";
            cmd = "exec ffmpeg -nostdin -loglevel quiet -f pulse -i default -ac 1 -ar 16000 "
                  "-f s16le -y '" + q + "'";
        }
        return rec.start (juce::StringArray { "/bin/bash", "-c", cmd }, 0);
    }

    void reapRecorder()   // kill + WAIT: zombies made isRunning() lie all evening
    {
        if (rec.isRunning()) rec.kill();
        rec.waitForProcessToFinish (300);
    }

    void hardCancel (bool announce)
    {
        ++epoch;                                  // orphan every in-flight transcription
        pendingJobs = 0;
        voiceMode = false;
        phase = Phase::off;
        reapRecorder();
        stopTimer();
        if (announce && onNote) onNote ("[voice] cancelled");
        if (onStateChange) onStateChange();
        repaint();
    }

    void stopTimerIfIdle()
    {
        if (! voiceMode && pendingJobs <= 0) stopTimer();
    }

    // slice [from, to) out of the growing take into its own raw file
    juce::File sliceUtterance (juce::int64 from, juce::int64 to, int myGen)
    {
        auto out = ipc.getChildFile ("voice_utt_" + juce::String (myGen) + ".raw");
        out.deleteFile();
        juce::FileInputStream in (rawFile);
        juce::FileOutputStream os (out);
        if (! in.openedOk() || ! os.openedOk()) return {};
        in.setPosition (from);
        juce::HeapBlock<char> buf (65536);
        juce::int64 left = to - from;
        while (left > 0)
        {
            const int got = in.read (buf.getData(), (int) juce::jmin ((juce::int64) 65536, left));
            if (got <= 0) break;
            os.write (buf.getData(), (size_t) got);
            left -= got;
        }
        os.flush();
        return out;
    }

    // send one utterance slice to the warm ear. Partials ride beam 1 and poll
    // briefly with NO fallback (a superseded partial may simply never be
    // answered — newest wins); finals ride beam 5, wait longer, and keep the
    // one-shot fallback. Adoption is gen-ordered on the message thread so a
    // stale partial can never overwrite newer words.
    //
    // FOLD AT SEND (Chezy live 2026-07-16: "IT OVERRIDES NEW INCOMING STT...
    // deletes the one before!"): a final's beam-5 answer can arrive AFTER the
    // next utterance's partials (a slow/cold decode always lost that race and
    // its whole sentence vanished). So the WORDS fold into the host's ledger
    // the moment the final is SENT (onFinalSent — the live tail is already on
    // screen); the answer later upgrades ITS OWN segment by gen, whenever and
    // in whatever order it lands. Words can never be out-raced again.
    void sendSlice (juce::int64 from, juce::int64 to, bool isFinal)
    {
        const int myGen = ++gen;
        if (isFinal)
        {
            lastAdoptedGen = juce::jmax (lastAdoptedGen, myGen);   // stale partials of THIS utterance die here
            if (onFinalSent) onFinalSent (myGen);                  // fold now — whatever befalls the slice
        }
        auto utt = sliceUtterance (from, to, myGen);
        if (utt == juce::File())
        {
            if (isFinal && onNote) onNote ("[voice] could not slice the take (disk?)");
            return;
        }
        {   // ask THE WARM EAR (atomic rename — the server tolerates torn writes)
            auto* o = new juce::DynamicObject();
            o->setProperty ("raw", utt.getFullPathName());
            o->setProperty ("rate", 16000);
            o->setProperty ("gen", myGen);
            o->setProperty ("beam", isFinal ? 5 : 1);
            const auto js = juce::JSON::toString (juce::var (o), true);
            auto tmp = ipc.getChildFile ("voice_req.json.tmp");
            tmp.replaceWithText (js);
            tmp.moveFileTo (ipc.getChildFile ("voice_req.json"));
        }
        awaitingGen = myGen;
        awaitingSince = juce::Time::getMillisecondCounter();
        ++pendingJobs;
        if (onStateChange) onStateChange();
        repaint();
        const auto rt = root;
        const auto ipcDir = ipc;
        const int myEpoch = epoch.load();
        juce::Component::SafePointer<VoiceMicButton> safe (this);
        juce::Thread::launch ([safe, myGen, myEpoch, isFinal, utt, rt, ipcDir]
        {
            juce::String text, note;
            bool answered = false, gotText = false;
            auto adopt = [&] (const juce::var& v)
            {
                if (auto* obj = v.getDynamicObject())
                {
                    const auto e = obj->getProperty ("error").toString();
                    if (e.isNotEmpty()) { if (isFinal) note = "[voice] " + e; }
                    else
                    {
                        text = obj->getProperty ("text").toString().trim();
                        gotText = true;                 // "" is a real answer (clears)
                    }
                    return true;
                }
                return false;
            };
            {   // warm path: the first utterance pays whatever model load remains
                auto res = ipcDir.getChildFile ("voice_res.json");
                const auto t1 = juce::Time::getMillisecondCounter();
                const juce::uint32 budget = isFinal ? 30000u : 6000u;
                while (juce::Time::getMillisecondCounter() - t1 < budget)
                {
                    if (res.existsAsFile())
                    {
                        juce::var v = juce::JSON::parse (res.loadFileAsString());   // NAMED var
                        if (auto* obj = v.getDynamicObject())
                        {
                            const int rg = (int) obj->getProperty ("gen");
                            if (rg == myGen)
                            {
                                res.deleteFile();
                                answered = adopt (v);
                                break;
                            }
                            if (rg > myGen) break;      // superseded: a newer answer owns the file
                        }
                    }
                    juce::Thread::sleep (isFinal ? 100 : 60);
                }
            }
            if (! answered && isFinal)
            {   // the warm ear never answered a FINAL: honest one-shot fallback
                auto py = rt.getChildFile (".venv/bin/python");
                const juce::String pyPath = py.existsAsFile() ? py.getFullPathName()
                                                              : juce::String ("python3");
                juce::ChildProcess tr;
                if (! tr.start (juce::StringArray {
                        pyPath, rt.getChildFile ("tools/voice_dictate.py").getFullPathName(),
                        "--raw", utt.getFullPathName() }))
                    note = "[voice] could not run voice_dictate.py";
                else
                {
                    const auto out = tr.readAllProcessOutput();   // worker thread: blocking drain
                    // a COLD one-shot needs ~13s of model load — the old 5s kill
                    // murdered every last-resort answer on a busy box
                    if (! tr.waitForProcessToFinish (20000)) tr.kill();
                    juce::String jsonLine;
                    for (auto& ln : juce::StringArray::fromLines (out))
                        if (ln.trimStart().startsWith ("{")) jsonLine = ln.trim();
                    juce::var v = juce::JSON::parse (jsonLine);   // NAMED var (lifetime law)
                    if (! adopt (v))
                        note = "[voice] transcriber said nothing parseable";
                }
            }
            utt.deleteFile();
            auto wav = utt.getSiblingFile (utt.getFileNameWithoutExtension() + ".wav");
            wav.deleteFile();
            juce::MessageManager::callAsync ([safe, myGen, myEpoch, isFinal, gotText, text, note]
            {
                if (safe == nullptr) return;
                if (myEpoch != safe->epoch.load()) return;        // hard-cancelled: ignore
                safe->pendingJobs = juce::jmax (0, safe->pendingJobs - 1);
                if (safe->awaitingGen == myGen) safe->awaitingGen = -1;
                if (note.isNotEmpty() && safe->onNote) safe->onNote (note);
                if (isFinal)
                {   // finals ALWAYS deliver, by gen — the host upgrades exactly
                    // the segment this final folded, in any arrival order; an
                    // unanswered/empty final keeps the folded beam-1 words
                    if (safe->onFinal) safe->onFinal (myGen, gotText ? text : juce::String());
                }
                else if (gotText && myGen > safe->lastAdoptedGen)
                {   // gen-ordered partials: stale words never overwrite newer
                    safe->lastAdoptedGen = myGen;
                    if (text.isNotEmpty() && safe->onPartial)
                        safe->onPartial (text);
                }
                safe->stopTimerIfIdle();
                if (safe->onStateChange) safe->onStateChange();
                safe->repaint();
            });
        });
    }

    void timerCallback() override
    {
        if (voiceMode)
        {
            const auto now = juce::Time::getMillisecondCounter();
            const auto size = rawFile.getSize();
            float rms = 0.0f;
            if (size > readPos)
            {   // RMS over the NEW bytes this tick (the VAD's evidence)
                juce::FileInputStream in (rawFile);
                if (in.openedOk())
                {
                    const int n = (int) juce::jmin ((juce::int64) 65536, size - readPos);
                    in.setPosition (size - n);
                    juce::HeapBlock<juce::int16> buf ((size_t) (n / 2));
                    const int got = in.read (buf.getData(), n) / 2;
                    double acc = 0.0;
                    for (int i = 0; i < got; ++i)
                        acc += (double) buf[i] * (double) buf[i];
                    rms = got > 0 ? (float) std::sqrt (acc / got) / 32768.0f : 0.0f;
                }
                readPos = size;
            }
            const float target = juce::jlimit (0.0f, 1.0f, rms * 9.0f);
            lvl += (target - lvl) * 0.45f;
            maxRmsSeen = juce::jmax (maxRmsSeen, rms);

            // ---- THE VAD: adaptive floor, onset run, end-of-speech hangover ----
            const bool loud = rms > juce::jmax (0.006f, noiseFloor * 3.5f);
            if (! loud && phase == Phase::waiting)
                noiseFloor = juce::jmax (0.002f, noiseFloor * 0.985f + rms * 0.015f);
            if (phase == Phase::waiting)
            {
                if (loud)
                {
                    if (speechTicks == 0)                          // remember where speech began
                        uttStart = juce::jmax ((juce::int64) 0, size - 24000);   // ~0.75s pre-roll
                        // (0.37s clipped first words when onset detection landed
                        //  late in the tick phase — "Make the drop" lost its head)
                    if (++speechTicks >= 5)                        // ~200ms of real voice
                    {
                        phase = Phase::speaking;
                        silenceTicks = 0;
                        ticksSinceReq = 0;
                        uttPartials = 0;
                        if (onStateChange) onStateChange();
                    }
                }
                else
                    speechTicks = 0;                               // a click, not a word
                // janitor: recycle a silent, monstrous take file (~20 min of mode-on)
                if (speechTicks == 0 && size > 38 * 1024 * 1024)
                {
                    reapRecorder();
                    rawFile.deleteFile();
                    if (startRecorder()) { readPos = 0; readPosGrowthMark = 0; uttStart = -1; lastGrowth = now; }
                    else { hardCancel (false); if (onNote) onNote ("[voice] recorder died on recycle"); return; }
                }
            }
            else if (phase == Phase::speaking)
            {
                if (loud) { silenceTicks = 0; ++speechTicks; }
                else ++silenceTicks;
                // REALTIME (the contract): while you speak, the growing utterance
                // re-transcribes at beam 1 — the FIRST words at ~0.33s, then every
                // ~0.5s. One request in flight at a time; newest wins.
                if (++ticksSinceReq >= (uttPartials == 0 ? 8 : 12)
                    && silenceTicks < 26 && canSend())
                {
                    ticksSinceReq = 0;
                    ++uttPartials;
                    sendSlice (juce::jmax ((juce::int64) 0, uttStart), size, false);
                }
                // THE ROLLING FREEZE (Chezy live 2026-07-16: room chatter never
                // pauses — the utterance slice grew for MINUTES, every decode blew
                // its budget, and the prompt starved while the log filled). Past
                // ~14s the utterance folds AT A BREATH (~0.25s lull) and continues
                // as a NEW utterance mid-speech — the ledger's gen-upgrades make
                // the seam invisible; 22s is the no-breath hard roll.
                const juce::int64 uttBytes = size - juce::jmax ((juce::int64) 0, uttStart);
                if (silenceTicks < 26
                    && (uttBytes > 32000 * (silenceTicks >= 6 ? 14 : 22))
                    && canSend())
                {
                    const juce::int64 from = juce::jmax ((juce::int64) 0, uttStart);
                    uttStart = size;                               // the monologue rolls on
                    ticksSinceReq = 0;
                    uttPartials = 0;
                    sendSlice (from, size, true);                  // fold + beam-5, mid-speech
                }
                if (silenceTicks >= 26)                            // ~1.1s pause: the words FREEZE
                {                                                  // (frozen, NEVER sent — Send is yours)
                    const juce::int64 from = juce::jmax ((juce::int64) 0, uttStart);
                    phase = Phase::waiting;
                    speechTicks = silenceTicks = ticksSinceReq = 0;
                    uttStart = -1;
                    if (onStateChange) onStateChange();
                    sendSlice (from, size, true);                  // beam-5 quality final
                }
            }
            // a dead-silent mode diagnoses itself instead of playing dead
            if (! silenceWarned && now - t0 > 3500 && maxRmsSeen < 0.004f)
            {
                silenceWarned = true;
                if (onNote) onNote ("[voice] the mic is silent - check the input device "
                                    "and its level (Settings > Audio & MIDI)");
            }
            // GROWTH IS LIFE (the zombie lesson: isRunning() lied about a dead
            // arecord for a whole evening — unreaped corpses still "exist").
            // A capture stream that stops WRITING is dead whatever the PID says:
            // reconnect it once, and if it dies again, say so and stand down.
            if (size > readPosGrowthMark)
            {
                readPosGrowthMark = size;
                lastGrowth = now;
                recRestarted = false;              // real bytes = a healthy ear again
            }
            else if (now - lastGrowth > 2200
                     && std::getenv ("SOTADAW_VOICE_FAKEREC") == nullptr)
            {
                if (! recRestarted)
                {
                    recRestarted = true;
                    reapRecorder();
                    if (startRecorder())
                    {
                        lastGrowth = now;
                        if (onNote) onNote ("[voice] the ear stalled - reconnected ("
                                            + backend + ")");
                    }
                    else
                    {
                        hardCancel (false);
                        if (onNote) onNote ("[voice] the recorder died and would not "
                                            "restart (device busy?)");
                        return;
                    }
                }
                else
                {
                    hardCancel (false);
                    if (onNote) onNote ("[voice] the recorder keeps dying - voice mode "
                                        "off (is another app holding the mic?)");
                    return;
                }
            }
        }
        repaint();
    }

    // one partial in flight at a time; a lost answer frees the lane after 2.5s
    bool canSend() const
    {
        return awaitingGen < 0
               || juce::Time::getMillisecondCounter() - awaitingSince > 2500;
    }

    bool voiceMode = false;
    Phase phase = Phase::off;
    int pendingJobs = 0;
    juce::ChildProcess rec, server;   // the continuous take + THE WARM EAR
    juce::File root, ipc, rawFile;
    juce::int64 readPos = 0, uttStart = -1, readPosGrowthMark = 0;
    juce::uint32 t0 = 0, awaitingSince = 0, lastGrowth = 0;
    float lvl = 0.0f, noiseFloor = 0.004f, maxRmsSeen = 0.0f;
    int speechTicks = 0, silenceTicks = 0, ticksSinceReq = 0, uttPartials = 0;
    int lastAdoptedGen = 0, awaitingGen = -1;
    bool silenceWarned = false, recRestarted = false;
    juce::String backend;             // which capture rail the ear rides (activity-logged)
    std::atomic<int> gen { 0 };       // per-slice request token (warm-ear matching)
    std::atomic<int> epoch { 0 };     // hard-cancel fence: bumping orphans all workers
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (VoiceMicButton)
};
