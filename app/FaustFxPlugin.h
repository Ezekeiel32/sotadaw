// FaustFxPlugin — hosts an AOT-compiled Faust EFFECT (N-in/N-out) as a Tracktion plugin.
// Used on track chains and the master bus (e.g. master_limiter). Params set via zone map.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include "FaustInstrumentPlugin.h"   // reuses FaustZoneUI + faust registry

class FaustFxPlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()  { return "FaustFx"; }
    static const char* xmlTypeName;

    FaustFxPlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        dspName.referTo (state, juce::Identifier ("dsp"), getUndoManager(), juce::String());
    }

    ~FaustFxPlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        sampleRate = info.sampleRate;
        rebuildDsp();
        const int bs = juce::jmax (512, info.blockSizeSamples);
        inBuf.setSize (2, bs);
        outBuf.setSize (2, bs);
    }

    void deinitialise() override { fdsp.reset(); }

    // See FaustInstrumentPlugin::prepareZones — params must exist at buildEdit time.
    void prepareZones() { if (fdsp == nullptr) rebuildDsp(); }

    void setZone (const juce::String& name, float value)
    {
        pendingParams[name] = value;
        applyParams();
        for (auto& zp : zoneParams)
            if (zp.second == name.toStdString())
                zp.first->setParameter (value, juce::dontSendNotification);
    }

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr) return;
        if (fdsp == nullptr || loadedName != dspName.get()) rebuildDsp();
        if (fdsp == nullptr) return;

        // Defensive: params are set via setZone() BEFORE the plugin is inserted into
        // the edit; any state-restoration pass between build and playback would reset
        // them to defaults. Reassert the song's explicit values ONCE on first process —
        // automation still owns the zones afterwards.
        if (! paramsReasserted)
        {
            paramsReasserted = true;
            for (auto& [pn, pv] : pendingParams)
                for (auto& zp : zoneParams)
                    if (zp.second == pn.toStdString())
                        zp.first->setParameter (pv, juce::dontSendNotification);
            if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                for (auto& zp : zoneParams)
                    std::fprintf (stderr, "[fxdbg] %s zone=%s param=%f pending=%f nParams=%d\n",
                                  dspName.get().toRawUTF8(), zp.second.c_str(),
                                  zp.first->getCurrentValue(),
                                  pendingParams.count (juce::String (zp.second)) ? pendingParams[juce::String (zp.second)] : -999.0f,
                                  (int) zoneParams.size());
        }

        for (auto& zp : zoneParams)
            if (auto it = ui.zones.find (zp.second); it != ui.zones.end())
                *it->second = (FAUSTFLOAT) zp.first->getCurrentValue();

        const int n = fc.bufferNumSamples;
        if (inBuf.getNumSamples() < n)  { inBuf.setSize (2, n, false, false, true); outBuf.setSize (2, n, false, false, true); }

        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        for (int ch = 0; ch < 2; ++ch)
            inBuf.copyFrom (ch, 0, *fc.destBuffer, juce::jmin (ch, nch - 1), fc.bufferStartSample, n);

        FAUSTFLOAT* ins[2]  = { inBuf.getWritePointer (0),  inBuf.getWritePointer (1) };
        FAUSTFLOAT* outs[2] = { outBuf.getWritePointer (0), outBuf.getWritePointer (1) };
        fdsp->compute (n, ins, outs);

        for (int ch = 0; ch < nch; ++ch)
            fc.destBuffer->copyFrom (ch, fc.bufferStartSample, outBuf, juce::jmin (ch, fdsp->getNumOutputs() - 1), 0, n);
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
        {                                          // JIT it — new fx need no rebuild
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
            applyParams();
            bindZoneParams();
        }
    }

    void bindZoneParams()
    {
        zoneParams.clear();
        for (auto& [name, zi] : ui.info)
        {
            const juce::String id (name);
            auto p = getAutomatableParameterByID (id);
            if (p == nullptr)
            {
                float lo = (float) zi.min, hi = (float) zi.max;
                if (! (lo < hi)) { lo = 0.0f; hi = juce::jmax (1.0f, (float) zi.init); }
                p = addParam (id, id, { lo, hi });
            }
            const auto pend = pendingParams.find (id);
            p->setParameter (pend != pendingParams.end() ? pend->second : (float) *zi.z,
                             juce::dontSendNotification);
            zoneParams.push_back ({ p.get(), name });
        }
    }

    void applyParams()
    {
        for (auto& [k, v] : pendingParams)
            if (ui.has (k.toRawUTF8()))
                ui.set (k.toRawUTF8(), (FAUSTFLOAT) v);
    }

    std::unique_ptr<::dsp> fdsp;
    FaustZoneUI ui;
    juce::AudioBuffer<float> inBuf, outBuf;
    std::map<juce::String, float> pendingParams;
    bool paramsReasserted = false;
    std::vector<std::pair<tracktion::AutomatableParameter*, std::string>> zoneParams;
    juce::String loadedName;
    double sampleRate = 44100.0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FaustFxPlugin)
};
