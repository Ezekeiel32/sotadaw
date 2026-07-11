// SpectralVoicePlugin — LIVE playback of spectral-capture lanes (docs/SPECTRAL_CAPTURE.md).
//
// A spectral lane's notes are PARTIALS: one note = one sinusoid whose pitch-bend +
// gain envelopes live in the capture sidecar (songs/<x>_spectral/.../capture.json),
// keyed by note identity. This plugin loads that sidecar and, when the lane's MIDI
// plays, synthesizes each note's partial with its own envelopes — so muting the
// P_mix clip and unmuting the lanes gives EDITABLE, immediately-audible partials
// (the deterministic tools/spectral.py render stays the byte-exact reference).
//
// source: { "kind": "spectral", "id": "<capture.json relpath>#<lane>" }
//   lane "partials" = the low/mid/high note lanes (this plugin, one instance per lane).
// Matching: noteOn at playhead beat B, pitch P -> captured note with pitch P whose
// start is nearest B (within 0.6 beats). Unmatched notes play a clean sine + AD.
// v0 timing law (same as FaustInstrumentPlugin): MIDI applies at block start.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include <cmath>
#include <map>
#include <memory>
#include <mutex>
#include <vector>

class SpectralVoicePlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()  { return "SpectralVoice"; }
    static const char* xmlTypeName;

    SpectralVoicePlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        captureRef.referTo (state, juce::Identifier ("capture"), getUndoManager(), juce::String());
    }

    ~SpectralVoicePlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }
    bool isSynth() override                          { return true; }
    bool takesMidiInput() override                   { return true; }
    bool producesAudioWhenNoAudioInput() override    { return true; }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        sampleRate = info.sampleRate;
        if (loadedRef != captureRef.get())
            loadCapture();
    }

    void deinitialise() override {}

    void restorePluginStateFromValueTree (const juce::ValueTree& v) override
    {
        tracktion::copyPropertiesToCachedValues (v, captureRef);
    }

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr)
            return;
        if (loadedRef != captureRef.get())
            loadCapture();

        const int n = fc.bufferNumSamples;
        const double beat0 = edit.tempoSequence.toBeats (fc.editTime.getStart()).inBeats();
        const double beat1 = edit.tempoSequence.toBeats (fc.editTime.getEnd()).inBeats();
        const double bps   = n > 0 ? (beat1 - beat0) / n : 0.0;   // beats per sample

        // THE STUCK-NOTE KILL (Chezy 2026-07-08): on the play->stop edge the beat
        // clock freezes, so a voice whose length hasn't elapsed sustains forever.
        // Release held voices on the edge (the 4ms ramp = no click); never during
        // an offline render. Edge, not level, so live preview isn't choked.
        if (wasPlaying && ! fc.isPlaying && ! fc.isRendering)
            for (auto& v : voices) v.releasing = true;
        wasPlaying = fc.isPlaying;

        if (fc.bufferForMidiMessages != nullptr)
        {
            for (const auto& m : *fc.bufferForMidiMessages)
            {
                if (m.isNoteOn())        noteOn  (m.getNoteNumber(), m.getFloatVelocity(), beat0);
                else if (m.isNoteOff())  noteOff (m.getNoteNumber());
                else if (m.isAllNotesOff() || m.isAllSoundOff() || m.isResetAllControllers())
                    for (auto& v : voices) v.releasing = true;
            }
        }
        if (voices.empty())
            return;

        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        float* out[2] = { fc.destBuffer->getWritePointer (0, fc.bufferStartSample),
                          nch > 1 ? fc.destBuffer->getWritePointer (1, fc.bufferStartSample) : nullptr };
        const double dt = 1.0 / (sampleRate > 0 ? sampleRate : 44100.0);

        for (auto& v : voices)
        {
            double ph = v.phase;
            for (int i = 0; i < n; ++i)
            {
                const double tb = (beat0 + i * bps) - v.startBeat;   // beats since note start
                if (tb < 0.0) continue;
                double cents = 0.0, g = 1.0;
                if (v.cap != nullptr)
                {
                    cents = sampleEnv (v.cap->bend, tb, v.bendIx);
                    g     = sampleEnv (v.cap->gain, tb, v.gainIx) * v.cap->peak;
                    if (tb > v.cap->lenBeats) v.done = true;
                }
                else
                {   // clean-sine fallback: 10ms attack, exponential-ish decay
                    const double ts = tb / juce::jmax (1e-9, bps / dt);   // ~seconds
                    g = 0.2 * juce::jmin (1.0, ts / 0.01) * std::exp (-ts / 0.5);
                    if (tb > v.lenBeats) v.done = true;
                }
                if (v.releasing) { v.relGain -= (float) (dt / 0.004); if (v.relGain <= 0) { v.done = true; break; } }
                const double f = v.baseHz * std::exp2 (cents / 1200.0);
                ph += juce::MathConstants<double>::twoPi * f * dt;
                const float s = (float) (g * v.velScale * v.relGain * std::cos (ph));
                out[0][i] += s;
                if (out[1] != nullptr) out[1][i] += s;
            }
            v.phase = std::fmod (ph, juce::MathConstants<double>::twoPi);
        }
        voices.erase (std::remove_if (voices.begin(), voices.end(),
                                      [] (const Voice& v) { return v.done; }),
                      voices.end());
    }

    juce::CachedValue<juce::String> captureRef;   // "<capture.json relpath>#<lane>"

private:
    struct Env { std::vector<float> t, v; };
    struct CapNote
    {
        double startBeat = 0, lenBeats = 0; int pitch = 60; float vel = 0.8f;
        float peak = 0.1f; Env bend, gain;
    };
    struct Voice
    {
        const CapNote* cap = nullptr;
        double startBeat = 0, lenBeats = 0.25, phase = 0, baseHz = 440.0;
        int note = 60; float velScale = 1.0f, relGain = 1.0f;
        bool releasing = false, done = false;
        size_t bendIx = 0, gainIx = 0;
    };

    static double sampleEnv (const Env& e, double t, size_t& ix)
    {
        const size_t N = e.t.size();
        if (N == 0) return 0.0;
        if (N == 1 || t <= e.t[0]) { ix = 0; return e.v[0]; }
        if (t >= e.t[N - 1]) { ix = N - 2; return e.v[N - 1]; }
        while (ix + 2 < N && e.t[ix + 1] <= t) ++ix;        // monotone within a note
        while (ix > 0 && e.t[ix] > t) --ix;                 // (seek back after loops)
        const double a = e.t[ix], b = e.t[ix + 1];
        const double w = b > a ? (t - a) / (b - a) : 0.0;
        return e.v[ix] + (e.v[ix + 1] - e.v[ix]) * w;
    }

    void noteOn (int note, float vel, double beatNow)
    {
        if (voices.size() >= 96) return;                    // partial-count safety
        Voice v;
        v.note = note;
        v.baseHz = juce::MidiMessage::getMidiNoteInHertz (note);
        v.startBeat = beatNow;
        // identity match: same pitch, captured start nearest the playhead
        const CapNote* best = nullptr;
        double bd = 0.6;                                    // beats tolerance
        for (const auto& c : *notes)
            if (c.pitch == note)
            {
                const double d = std::abs (c.startBeat - beatNow);
                if (d < bd) { bd = d; best = &c; }
            }
        if (best != nullptr)
        {
            v.cap = best;
            v.startBeat = beatNow;      // envelopes play from the note head
            v.velScale = best->vel > 1e-6f ? vel / best->vel : 1.0f;
        }
        else
            v.velScale = vel;
        voices.push_back (v);
    }

    void noteOff (int note)
    {
        for (auto& v : voices)
            if (v.note == note && ! v.releasing)
                v.releasing = true;
    }

    static juce::File sotadawRootFile()
    {
        // mirror SongLoader::sotadawRoot(): the repo root that owns agent/sidecar.py
        auto d = juce::File::getSpecialLocation (juce::File::currentExecutableFile);
        for (int up = 0; up < 8; ++up)
        {
            d = d.getParentDirectory();
            if (d.getChildFile ("agent/sidecar.py").existsAsFile())
                return d;
        }
        return juce::File::getCurrentWorkingDirectory();
    }

    // THE SIDECAR PARSE CACHE (2026-07-11): a truth song mounts THREE lanes per
    // deck, all "<capture>.json#partials" — before this, initialise() parsed the
    // same 215-716MB sidecar once PER LANE (12 juce::JSON parses / ~2GB of JSON
    // on aranyanyara). Cache the EXTRACTED note vectors (tens of MB), keyed by
    // resolved path#lane + mtime (re-merges invalidate); the var tree frees at
    // parse end. Voices are cleared on reload — CapNote pointers into a swapped
    // vector would dangle (pre-existing hazard, fixed by the shared_ptr swap).
    using NoteList = std::vector<CapNote>;
    struct CachedLane { juce::int64 mtime = 0; std::shared_ptr<const NoteList> notes; };
    static std::map<juce::String, CachedLane>& laneCache()
    { static std::map<juce::String, CachedLane> c; return c; }
    static std::mutex& laneCacheLock()
    { static std::mutex m; return m; }

    void loadCapture()
    {
        notes = std::make_shared<const NoteList>();
        voices.clear();
        loadedRef = captureRef.get();
        auto ref = loadedRef;
        juce::String lane = "partials";
        if (ref.contains ("#")) { lane = ref.fromLastOccurrenceOf ("#", false, false); ref = ref.upToLastOccurrenceOf ("#", false, false); }
        auto f = juce::File::isAbsolutePath (ref) ? juce::File (ref)
                                                  : sotadawRootFile().getChildFile (ref);
        if (! f.existsAsFile()) return;
        const auto key = f.getFullPathName() + "#" + lane;
        const auto mtime = f.getLastModificationTime().toMilliseconds();
        std::lock_guard<std::mutex> lg (laneCacheLock());
        auto& slot = laneCache()[key];
        if (slot.notes != nullptr && slot.mtime == mtime)
        { notes = slot.notes; return; }
        auto fresh = std::make_shared<NoteList>();
        const auto root = juce::JSON::parse (f.loadFileAsString());
        const auto tracks = root.getProperty ("tracks", juce::var());
        const auto arr = tracks.getProperty (juce::Identifier (lane), juce::var());
        if (auto* a = arr.getArray())
        {
            fresh->reserve ((size_t) a->size());
            for (const auto& nv : *a)
            {
                CapNote c;
                c.startBeat = (double) nv.getProperty ("start", 0.0);
                c.lenBeats  = (double) nv.getProperty ("len", 0.25);
                c.pitch     = (int)    nv.getProperty ("pitch", 60);
                c.vel       = (float) (double) nv.getProperty ("vel", 0.8);
                const auto sp = nv.getProperty ("sp", juce::var());
                c.peak = (float) (double) sp.getProperty ("peak", 0.1);
                auto loadEnv = [] (const juce::var& ev, Env& e)
                {
                    if (auto* pts = ev.getArray())
                        for (const auto& p : *pts)
                            if (auto* xy = p.getArray(); xy != nullptr && xy->size() >= 2)
                            { e.t.push_back ((float) (double) (*xy)[0]); e.v.push_back ((float) (double) (*xy)[1]); }
                };
                loadEnv (sp.getProperty ("bend", juce::var()), c.bend);
                loadEnv (sp.getProperty ("gain", juce::var()), c.gain);
                fresh->push_back (std::move (c));
            }
        }
        slot.mtime = mtime;
        slot.notes = std::shared_ptr<const NoteList> (std::move (fresh));
        notes = slot.notes;
    }

    std::shared_ptr<const NoteList> notes { std::make_shared<const NoteList>() };
    std::vector<Voice> voices;
    juce::String loadedRef { "\x01unloaded" };
    double sampleRate = 44100.0;
    bool wasPlaying = false;             // transport-stop edge -> release held voices

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SpectralVoicePlugin)
};
