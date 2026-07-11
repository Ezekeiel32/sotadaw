// ClapPlugin — V50 CLAP HOSTING: host any .clap plugin as a session insert.
// JUCE/Tracktion host VST3/AU/LADSPA but NOT clap; this is a direct C-ABI host
// (clap_bridge) — the same doorway pattern as NamPlugin. A .clap effect loads as:
//   fx: {"id": "clap:<path/to/plugin.clap>", "params": {"index": 0}}
// stereo-in -> the plugin -> stereo-out, fixed preset (no automation/GUI/state in
// v1 — the audio insert is the provable core; params/preset are the follow-up).
// CLAP core stays quarantined behind clap_bridge (SongLoader never sees clap/*.h).
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include <cstdio>
#include <memory>
#include <vector>
#include "clap_bridge.h"

class ClapPlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()          { return "ClapHost"; }
    inline static const char* xmlTypeName = "clapHost";

    ClapPlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        auto* um = getUndoManager();
        fileV.referTo  (state, juce::Identifier ("file"),  um, juce::String());
        indexV.referTo (state, juce::Identifier ("index"), um, 0);
        mixV.referTo   (state, juce::Identifier ("mix"),   um, 1.0f);
        mixP = addParam ("mix", "mix", { 0.0f, 1.0f });
        mixP->setParameter (mixV, juce::dontSendNotification);
    }

    ~ClapPlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }

    void setFile (const juce::String& path)          { fileV = path; }
    void setParams (const std::map<juce::String, float>& p)
    {
        for (auto& [k, v] : p)
        {
            if      (k == "index") indexV = (int) v;
            else if (k == "mix") { mixV = v; mixP->setParameter (v, juce::dontSendNotification); }
        }
    }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        const auto path = fileV.get();
        if (path.isNotEmpty() && (model == nullptr || path != loadedPath || indexV.get() != loadedIndex))
        {
            char err[256] = { 0 };
            model.reset (clap_load (path.toRawUTF8(), indexV.get(), err, (int) sizeof (err)));
            loadedPath = path; loadedIndex = indexV.get();
            if (model == nullptr)
                std::fprintf (stderr, "[clap] LOAD FAILED %s: %s\n", path.toRawUTF8(), err);
        }
        const int mb = juce::jmax (64, info.blockSizeSamples);
        if (model != nullptr)
        {
            if (! clap_activate (model.get(), info.sampleRate, mb))
                std::fprintf (stderr, "[clap] activate failed for %s\n", path.toRawUTF8());
            else if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                std::fprintf (stderr, "[clap] %s up (%.0f Hz, block %d)\n",
                              clap_name (model.get()), info.sampleRate, mb);
        }
        wetL.assign ((size_t) mb, 0.0f); wetR.assign ((size_t) mb, 0.0f);
    }

    void deinitialise() override {}

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr || fc.bufferNumSamples == 0 || model == nullptr)
            return;                                       // no model = passthrough
        const int n   = fc.bufferNumSamples;
        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        if ((int) wetL.size() < n) { wetL.resize ((size_t) n); wetR.resize ((size_t) n); }

        const float* inL = fc.destBuffer->getReadPointer (0, fc.bufferStartSample);
        const float* inR = fc.destBuffer->getReadPointer (juce::jmin (1, nch - 1), fc.bufferStartSample);
        clap_process_audio (model.get(), inL, inR, wetL.data(), wetR.data(), n);

        const float mix = juce::jlimit (0.0f, 1.0f, mixV.get());
        for (int c = 0; c < nch; ++c)
        {
            auto* d = fc.destBuffer->getWritePointer (c, fc.bufferStartSample);
            const float* wet = (c == 0) ? wetL.data() : wetR.data();
            for (int i = 0; i < n; ++i)
                d[i] = (1.0f - mix) * d[i] + mix * wet[i];
        }
    }

    void restorePluginStateFromValueTree (const juce::ValueTree&) override {}

private:
    struct FreeClap { void operator() (ClapHandle* h) const { clap_unload (h); } };
    std::unique_ptr<ClapHandle, FreeClap> model;
    juce::String loadedPath;
    int loadedIndex = -1;
    std::vector<float> wetL, wetR;
    juce::CachedValue<juce::String> fileV;
    juce::CachedValue<int> indexV;
    juce::CachedValue<float> mixV;
    tracktion::AutomatableParameter::Ptr mixP;
};
