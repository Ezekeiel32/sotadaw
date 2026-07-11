// FaustInstrumentPlugin — hosts an AOT-compiled Faust instrument as a Tracktion synth plugin.
// The instrument is chosen by the "dsp" state property (name from faust_gen registry).
// MIDI -> Faust zones: noteOn sets freq/gain + gate=1 (with a short gate-low pre-roll to
// retrigger/choke when already playing), noteOff of the current note sets gate=0.
// v0 timing: MIDI is applied at block start (blocks are ~10ms; fine for offline render).
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include <map>
#include <memory>
#include <set>
#include "faust_gen/faust_registry.h"
#include "FaustJit.h"

// Captures Faust control zones by leaf label (with ranges, for automation binding).
struct FaustZoneUI : public UI
{
    struct Info { FAUSTFLOAT* z = nullptr; FAUSTFLOAT init = 0, min = 0, max = 1; };
    std::map<std::string, FAUSTFLOAT*> zones;
    std::map<std::string, Info> info;
    void openTabBox (const char*) override {}
    void openHorizontalBox (const char*) override {}
    void openVerticalBox (const char*) override {}
    void closeBox() override {}
    void addButton (const char* l, FAUSTFLOAT* z) override { zones[l] = z; info[l] = { z, 0, 0, 1 }; *z = 0; }
    void addCheckButton (const char* l, FAUSTFLOAT* z) override { zones[l] = z; info[l] = { z, 0, 0, 1 }; *z = 0; }
    void addVerticalSlider (const char* l, FAUSTFLOAT* z, FAUSTFLOAT init, FAUSTFLOAT mn, FAUSTFLOAT mx, FAUSTFLOAT) override { zones[l] = z; info[l] = { z, init, mn, mx }; *z = init; }
    void addHorizontalSlider (const char* l, FAUSTFLOAT* z, FAUSTFLOAT init, FAUSTFLOAT mn, FAUSTFLOAT mx, FAUSTFLOAT) override { zones[l] = z; info[l] = { z, init, mn, mx }; *z = init; }
    void addNumEntry (const char* l, FAUSTFLOAT* z, FAUSTFLOAT init, FAUSTFLOAT mn, FAUSTFLOAT mx, FAUSTFLOAT) override { zones[l] = z; info[l] = { z, init, mn, mx }; *z = init; }
    void addHorizontalBargraph (const char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT) override {}
    void addVerticalBargraph (const char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT) override {}
    void addSoundfile (const char*, const char*, Soundfile**) override {}
    void declare (FAUSTFLOAT*, const char*, const char*) override {}
    void set (const char* k, FAUSTFLOAT v) { auto it = zones.find (k); if (it != zones.end()) *it->second = v; }
    bool has (const char* k) const { return zones.count (k) > 0; }
};

class FaustInstrumentPlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()  { return "FaustInstrument"; }
    static const char* xmlTypeName;

    FaustInstrumentPlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        dspName.referTo (state, juce::Identifier ("dsp"), getUndoManager(), juce::String());
    }

    ~FaustInstrumentPlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }
    bool isSynth() override                          { return true; }
    bool takesMidiInput() override                   { return true; }
    bool producesAudioWhenNoAudioInput() override    { return true; }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        sampleRate = info.sampleRate;
        rebuildDsp();
        scratch.setSize (2, juce::jmax (512, info.blockSizeSamples));
    }

    void deinitialise() override { fdsp.reset(); }

    // Make zones + AutomatableParameters exist NOW (SongLoader needs params at buildEdit time
    // to attach automation curves; initialise() later re-inits at the real sample rate).
    void prepareZones() { if (fdsp == nullptr) rebuildDsp(); }

    void setZone (const juce::String& name, float value)
    {
        pendingParams[name] = value;
        if (fdsp != nullptr)
        {
            ui.set (name.toRawUTF8(), (FAUSTFLOAT) value);
            for (auto& zp : zoneParams)
                if (zp.second == name.toStdString())
                    zp.first->setParameter (value, juce::dontSendNotification);
        }
    }

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr)
            return;
        if (fdsp == nullptr || loadedName != dspName.get())
            rebuildDsp();
        if (fdsp == nullptr)
            return;

        // Mirror FaustFxPlugin: a state-restoration pass between buildEdit and playback
        // can reset AutomatableParameters to defaults, and the param->zone copy below
        // would then erase the song's explicit source params. Reassert ONCE on first
        // process; automation owns the zones afterwards.
        if (! paramsReasserted)
        {
            paramsReasserted = true;
            for (auto& [pn, pv] : pendingParams)
                for (auto& zp : zoneParams)
                    if (zp.second == pn.toStdString())
                        zp.first->setParameter (pv, juce::dontSendNotification);
        }

        // automation/params -> zones (freq/gain/gate stay MIDI-owned)
        for (auto& zp : zoneParams)
            if (auto it = ui.zones.find (zp.second); it != ui.zones.end())
                *it->second = (FAUSTFLOAT) zp.first->getCurrentValue();

        const int n = fc.bufferNumSamples;
        if (scratch.getNumSamples() < n)
            scratch.setSize (2, n, false, false, true);

        // THE STUCK-NOTE KILL (Chezy 2026-07-08): stopping playback mid-note never
        // delivers the note-off scheduled at the note's end, so the gate hangs and
        // the voice sustains forever (only re-arming record cleared it). The graph
        // keeps pumping silence after a stop, so catch the play->stop EDGE here and
        // release the held gate. Edge, not level: live MIDI-keyboard preview plays
        // with isPlaying=false continuously and must NOT be choked. Never during an
        // offline render (it lays its own note-offs).
        if (wasPlaying && ! fc.isPlaying && ! fc.isRendering && currentNote >= 0)
        {
            if (ui.has ("gate")) ui.set ("gate", 0.0f);
            currentNote = -1;
        }
        wasPlaying = fc.isPlaying;

        int cursor = 0;
        if (fc.bufferForMidiMessages != nullptr)
        {
            for (const auto& m : *fc.bufferForMidiMessages)
            {
                if (m.isNoteOn())
                {
                    if (ui.has ("gate") && *ui.zones["gate"] > 0.5f && cursor + 8 <= n)
                    {
                        ui.set ("gate", 0.0f);          // choke/retrigger pre-roll
                        computeSeg (fc, cursor, 8);
                        cursor += 8;
                    }
                    if (ui.has ("freq")) ui.set ("freq", (FAUSTFLOAT) juce::MidiMessage::getMidiNoteInHertz (m.getNoteNumber()));
                    if (ui.has ("gain")) ui.set ("gain", (FAUSTFLOAT) m.getFloatVelocity());
                    if (ui.has ("gate")) ui.set ("gate", 1.0f);
                    currentNote = m.getNoteNumber();
                }
                else if (m.isNoteOff() && m.getNoteNumber() == currentNote)
                {
                    if (ui.has ("gate")) ui.set ("gate", 0.0f);
                    currentNote = -1;
                }
                // PANIC: honor the standard all-notes-off / all-sound-off / reset
                // controllers (a host stop, a MIDI panic button) — any voice dies.
                else if (m.isAllNotesOff() || m.isAllSoundOff()
                         || m.isResetAllControllers())
                {
                    if (ui.has ("gate")) ui.set ("gate", 0.0f);
                    currentNote = -1;
                }
            }
        }
        computeSeg (fc, cursor, n - cursor);
    }

    void restorePluginStateFromValueTree (const juce::ValueTree& v) override
    {
        tracktion::copyPropertiesToCachedValues (v, dspName);
    }

    juce::CachedValue<juce::String> dspName;

private:
    void rebuildDsp()
    {
        fdsp.reset (createFaustDsp (dspName.get().toStdString()));
        if (fdsp == nullptr)                       // not in the AOT registry:
        {                                          // JIT it — new voices need no rebuild
            std::string jitErr;
            fdsp.reset (sotadaw::createJitFaustDsp (dspName.get().toStdString(), jitErr));
            if (fdsp == nullptr && std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                std::fprintf (stderr, "[fxdbg] JIT failed for %s: %s\n",
                              dspName.get().toRawUTF8(), jitErr.c_str());
        }
        loadedName = dspName.get();
        if (fdsp != nullptr)
        {
            fdsp->init ((int) (sampleRate > 0 ? sampleRate : 44100.0));
            ui.zones.clear();
            ui.info.clear();
            fdsp->buildUserInterface (&ui);
            for (auto& [k, v] : pendingParams)
                ui.set (k.toRawUTF8(), (FAUSTFLOAT) v);
            bindZoneParams();
        }
    }

    void bindZoneParams()
    {
        static const std::set<std::string> reserved { "freq", "gain", "gate" };
        const bool dbg = std::getenv ("SOTADAW_FX_DEBUG") != nullptr;
        zoneParams.clear();
        for (auto& [name, zi] : ui.info)
        {
            if (reserved.count (name) > 0) continue;
            const juce::String id (name);
            auto p = getAutomatableParameterByID (id);
            if (p == nullptr)
            {
                float lo = (float) zi.min, hi = (float) zi.max;
                if (! (lo < hi)) { lo = 0.0f; hi = juce::jmax (1.0f, (float) zi.init); }
                p = addParam (id, id, { lo, hi });
            }
            if (p == nullptr)
            {
                if (dbg) std::fprintf (stderr, "[fxdbg] inst %s: addParam FAILED for '%s'\n",
                                       loadedName.toRawUTF8(), name.c_str());
                continue;
            }
            const auto pend = pendingParams.find (id);
            p->setParameter (pend != pendingParams.end() ? pend->second : (float) *zi.z,
                             juce::dontSendNotification);
            zoneParams.push_back ({ p.get(), name });
        }
        if (dbg)
            std::fprintf (stderr, "[fxdbg] inst '%s' @%p: %d zones -> %d bound params (list size %d)\n",
                          dspName.get().toRawUTF8(), (void*) this, (int) ui.info.size(),
                          (int) zoneParams.size(), getAutomatableParameters().size());
    }

    void computeSeg (const tracktion::PluginRenderContext& fc, int offset, int len)
    {
        if (len <= 0)
            return;
        FAUSTFLOAT* outs[2] = { scratch.getWritePointer (0), scratch.getWritePointer (1) };
        fdsp->compute (len, nullptr, outs);
        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        for (int ch = 0; ch < nch; ++ch)
            fc.destBuffer->addFrom (ch, fc.bufferStartSample + offset,
                                    scratch, juce::jmin (ch, fdsp->getNumOutputs() - 1), 0, len);
    }

    std::unique_ptr<::dsp> fdsp;
    FaustZoneUI ui;
    juce::AudioBuffer<float> scratch;
    juce::String loadedName;
    double sampleRate = 44100.0;
    int currentNote = -1;
    bool wasPlaying = false;             // transport-stop edge -> release hanging gate
    std::map<juce::String, float> pendingParams;
    bool paramsReasserted = false;
    std::vector<std::pair<tracktion::AutomatableParameter*, std::string>> zoneParams;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FaustInstrumentPlugin)
};
