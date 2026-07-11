// NamPlugin — V51 THE NAM RAIL: every captured amp/pedal on earth becomes a
// symbolic session object. A .nam file (Neural Amp Modeler capture, open format,
// TONE3000/ToneHunt universe) loads as a track/bus/master insert:
//   fx: {"id": "nam:<capture.nam>", "params": {"input_db": 0, "output_db": 0}}
// Timbre-Law clean: renders our audio through a fixed learned transform — no
// generation, fully deterministic. NAM core stays quarantined behind nam_bridge
// (Eigen never reaches this header's includers).
//
// v1 laws: captures are MONO devices — the insert processes the MONO SUM and
// writes it to both channels (the guitar-rig convention); models trained at a
// different sample rate than the engine still process (tone shifts slightly
// with the rate delta) — the mismatch is REPORTED via SOTADAW_FX_DEBUG, and a
// resampler wrap is the named follow-up.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include <atomic>
#include <cstdio>
#include <memory>
#include <vector>
#include "nam_bridge.h"

class NamPlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()          { return "NamCapture"; }
    inline static const char* xmlTypeName = "namCapture";

    NamPlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        auto* um = getUndoManager();
        fileV.referTo  (state, juce::Identifier ("file"),      um, juce::String());
        inDbV.referTo  (state, juce::Identifier ("input_db"),  um, 0.0f);
        outDbV.referTo (state, juce::Identifier ("output_db"), um, 0.0f);
        inDbP  = addParam ("input_db",  "input_db",  { -24.0f, 24.0f });
        outDbP = addParam ("output_db", "output_db", { -24.0f, 24.0f });
        inDbP->setParameter (inDbV, juce::dontSendNotification);
        outDbP->setParameter (outDbV, juce::dontSendNotification);
    }

    ~NamPlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }

    void setFile (const juce::String& path)          { fileV = path; }
    void setParams (const std::map<juce::String, float>& p)
    {
        for (auto& [k, v] : p)
        {
            if      (k == "input_db")  { inDbV = v;  inDbP->setParameter (v, juce::dontSendNotification); }
            else if (k == "output_db") { outDbV = v; outDbP->setParameter (v, juce::dontSendNotification); }
        }
    }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        const auto path = fileV.get();
        if (path.isNotEmpty() && (model == nullptr || path != loadedPath))
        {
            char err[256] = { 0 };
            model.reset (nam_load (path.toRawUTF8(), err, (int) sizeof (err)));
            loadedPath = path;
            if (model == nullptr)
                std::fprintf (stderr, "[nam] LOAD FAILED %s: %s\n", path.toRawUTF8(), err);
        }
        if (model != nullptr)
        {
            nam_reset (model.get(), info.sampleRate, juce::jmax (64, info.blockSizeSamples));
            if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
            {
                const double er = nam_expected_rate (model.get());
                std::fprintf (stderr, "[nam] %s up (capture rate %.0f, engine %.0f%s)\n",
                              juce::File (path).getFileName().toRawUTF8(), er, info.sampleRate,
                              (er > 0 && std::abs (er - info.sampleRate) > 1.0)
                                  ? " — RATE MISMATCH, tone shifts; resampler wrap = follow-up" : "");
            }
        }
        mono.resize ((size_t) juce::jmax (64, info.blockSizeSamples));
    }

    void deinitialise() override {}

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr || fc.bufferNumSamples == 0 || model == nullptr)
            return;                                       // no model = passthrough
        const int n   = fc.bufferNumSamples;
        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        if ((int) mono.size() < n)
            mono.resize ((size_t) n);
        const float inGain  = juce::Decibels::decibelsToGain (inDbV.get());
        const float outGain = juce::Decibels::decibelsToGain (outDbV.get());
        for (int i = 0; i < n; ++i)
        {
            float s = 0.0f;
            for (int c = 0; c < nch; ++c)
                s += fc.destBuffer->getSample (c, fc.bufferStartSample + i);
            mono[(size_t) i] = inGain * s / (float) nch;  // the mono-sum DI
        }
        nam_process (model.get(), mono.data(), mono.data(), n);
        for (int c = 0; c < nch; ++c)
        {
            auto* d = fc.destBuffer->getWritePointer (c, fc.bufferStartSample);
            for (int i = 0; i < n; ++i)
                d[i] = outGain * mono[(size_t) i];
        }
    }

private:
    struct FreeNam { void operator() (NamHandle* h) const { nam_free (h); } };
    std::unique_ptr<NamHandle, FreeNam> model;
    juce::String loadedPath;
    std::vector<float> mono;
    juce::CachedValue<juce::String> fileV;
    juce::CachedValue<float> inDbV, outDbV;
    tracktion::AutomatableParameter::Ptr inDbP, outDbP;
};
