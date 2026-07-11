// RetunePlugin — CONTEXT-TUNE LIVE (V45 P4): realtime chord-following autotune insert.
// The industry first the SPEC names: a live tuner whose allowed notes come from the
// ARRANGEMENT — SongLoader compiles the other tracks' notes into a per-half-beat
// pitch-class grid; at play time the current beat picks the chord, YIN detects the
// voice, and signalsmith-stretch (MIT, formant-preserving) shifts to the nearest
// allowed pitch. Fallback ladder per window: chord grid -> key scale -> chromatic.
// Latency = stretch input+output latency, reported via getLatencySeconds() (engine PDC).
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include "signalsmith-stretch.h"

class RetunePlugin : public tracktion::Plugin
{
public:
    static const char* getPluginName()  { return "SotaRetune"; }
    static const char* xmlTypeName;

    RetunePlugin (tracktion::PluginCreationInfo info) : tracktion::Plugin (info)
    {
        auto* um = getUndoManager();
        amountV.referTo   (state, juce::Identifier ("amount"),   um, 1.0f);
        retuneMsV.referTo (state, juce::Identifier ("retuneMs"), um, 8.0f);
        keyRootV.referTo  (state, juce::Identifier ("keyRoot"),  um, -1);
        keyMinorV.referTo (state, juce::Identifier ("keyMinor"), um, 0);
        gridV.referTo     (state, juce::Identifier ("grid"),     um, juce::String());
        amountP = addParam ("amount",   "amount",   { 0.0f, 1.0f });
        retuneP = addParam ("retuneMs", "retuneMs", { 0.0f, 400.0f });
        amountP->setParameter (amountV, juce::dontSendNotification);
        retuneP->setParameter (retuneMsV, juce::dontSendNotification);
    }

    ~RetunePlugin() override { notifyListenersOfDeletion(); }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }
    double getLatencySeconds() override               { return latencySec; }

    void setParams (const std::map<juce::String, float>& p)
    {
        for (auto& [k, v] : p)
        {
            if      (k == "amount")   { amountV = v;   amountP->setParameter (v, juce::dontSendNotification); }
            else if (k == "retuneMs") { retuneMsV = v; retuneP->setParameter (v, juce::dontSendNotification); }
        }
    }

    // grid: one uint16 pc-mask per half-beat (bit pc set = allowed); key = scale fallback
    void setContext (const juce::String& gridCsv, int keyRoot, bool keyMinor)
    {
        gridV = gridCsv; keyRootV = keyRoot; keyMinorV = keyMinor ? 1 : 0;
        parseGrid();
    }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        fs = info.sampleRate;
        stretch.presetCheaper (2, (float) fs);
        stretch.setTransposeFactor (1.0f, 8000.0f / (float) fs);
        stretch.setFormantSemitones (0.0f, true);        // formants stay put (no chipmunk)
        latencySec = (stretch.inputLatency() + stretch.outputLatency()) / fs;
        ana.assign (ANA_N, 0.0f);
        anaPos = 0;
        smoothRatio = 1.0;
        lastTau = 0;
        parseGrid();
        const int bs = juce::jmax (512, info.blockSizeSamples);
        scratch.setSize (2, bs);
        scratchOut.setSize (2, bs);
        if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
            std::fprintf (stderr, "[retune] init fs=%.0f latency=%.1fms grid=%d cells key=%d/%d\n",
                          fs, latencySec * 1000.0, (int) grid.size(), keyRootV.get(), keyMinorV.get());
    }

    void deinitialise() override {}

    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr || fc.bufferNumSamples == 0) return;
        const int n   = fc.bufferNumSamples;
        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        if (scratch.getNumSamples() < n)
        {
            scratch.setSize (2, n, false, false, true);
            scratchOut.setSize (2, n, false, false, true);
        }

        // 1) analysis ring (mono, decimated x2)
        for (int i = 0; i < n; i += 2)
        {
            float sum = 0;
            for (int c = 0; c < nch; ++c) sum += fc.destBuffer->getSample (c, fc.bufferStartSample + i);
            ana[anaPos] = sum / (float) nch;
            anaPos = (anaPos + 1) & (ANA_N - 1);
        }

        // 2) detect + choose target ratio
        float conf = 0.0f;
        const float f0 = yin (conf);
        double targetRatio = 1.0;
        int dbgTarget = -1; double dbgBeat = -1;
        if (f0 > 0 && conf > 0.55f)
        {
            const double sungMidi = 69.0 + 12.0 * std::log2 (f0 / 440.0);
            const double beat = edit.tempoSequence.toBeats (fc.editTime.getStart()).inBeats();
            const int target = nearestAllowed (sungMidi, beat);
            dbgTarget = target; dbgBeat = beat;
            if (target > 0)
            {
                const double tHz = 440.0 * std::pow (2.0, (target - 69.0) / 12.0);
                const double amt = juce::jlimit (0.0f, 1.0f, amountP->getCurrentValue());
                targetRatio = std::pow (tHz / f0, amt);
                targetRatio = juce::jlimit (std::pow (2.0, -7.0 / 12.0),
                                            std::pow (2.0,  7.0 / 12.0), targetRatio);
            }
        }
        // 3) glide (one-pole, tau = retuneMs; unvoiced relaxes to 1 quickly)
        const double tauMs = (f0 > 0 && conf > 0.55f)
                               ? juce::jmax (1.0f, retuneP->getCurrentValue()) : 30.0;
        const double alpha = 1.0 - std::exp (-(n / fs) * 1000.0 / tauMs);
        smoothRatio += alpha * (targetRatio - smoothRatio);
        stretch.setTransposeFactor ((float) smoothRatio, 8000.0f / (float) fs);

        // 4) shift 1:1 through the stretch (formant-preserving). NOT in-place:
        // process() consumes input lazily while emitting output.
        const float* inPtrs[2]; float* outPtrs[2];
        for (int c = 0; c < 2; ++c)
        {
            const int src = juce::jmin (c, nch - 1);
            scratch.copyFrom (c, 0, *fc.destBuffer, src, fc.bufferStartSample, n);
            inPtrs[c]  = scratch.getReadPointer (c);
            outPtrs[c] = scratchOut.getWritePointer (c);
        }
        stretch.process (inPtrs, n, outPtrs, n);
        for (int c = 0; c < nch; ++c)
            fc.destBuffer->copyFrom (c, fc.bufferStartSample, scratchOut, c, 0, n);
        if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr && ++dbgBlocks % 40 == 1)
            std::fprintf (stderr, "[retune] blk=%d f0=%.1f conf=%.2f beat=%.2f mask=%x target=%d ratio=%.4f in=%.3f out=%.3f\n",
                          dbgBlocks, f0, conf, dbgBeat,
                          dbgBeat >= 0 ? maskAt (dbgBeat) : 0, dbgTarget, smoothRatio,
                          scratch.getRMSLevel (0, 0, n), scratchOut.getRMSLevel (0, 0, n));
    }

    void restorePluginStateFromValueTree (const juce::ValueTree& v) override
    {
        tracktion::copyPropertiesToCachedValues (v, amountV, retuneMsV, keyRootV, keyMinorV, gridV);
        parseGrid();
    }

private:
    static constexpr int ANA_N = 4096;               // mono ring at fs/2 (~186ms @44.1k)
    static constexpr double GRID_STEP = 0.5;         // beats per grid cell

    void parseGrid()
    {
        grid.clear();
        juce::StringArray parts;
        parts.addTokens (gridV.get(), ",", "");
        for (auto& p : parts)
            grid.push_back ((juce::uint16) p.getIntValue());
        scaleMask = 0;
        const int root = keyRootV.get();
        if (root >= 0)
        {
            static const int majd[7] = { 0, 2, 4, 5, 7, 9, 11 };
            static const int mind[7] = { 0, 2, 3, 5, 7, 8, 10 };
            for (int i = 0; i < 7; ++i)
                scaleMask |= (juce::uint16) (1u << ((root + (keyMinorV.get() ? mind[i] : majd[i])) % 12));
        }
    }

    juce::uint16 maskAt (double beat) const
    {
        if (! grid.empty())
        {
            const int i = (int) std::floor (beat / GRID_STEP);
            if (i >= 0 && i < (int) grid.size() && grid[(size_t) i] != 0)
                return grid[(size_t) i];
        }
        return scaleMask != 0 ? scaleMask : (juce::uint16) 0x0FFF;   // chromatic last
    }

    int nearestAllowed (double sungMidi, double beat) const
    {
        // blended live rule: allowed = chord ∪ scale (chromatic only if neither);
        // non-chord tones pay +0.6 semitones — chord pulls, scale stays reachable
        // (matches the offline Viterbi's prox/chord/scale balance).
        juce::uint16 chordMask = 0;
        if (! grid.empty())
        {
            const int i = (int) std::floor (beat / GRID_STEP);
            if (i >= 0 && i < (int) grid.size()) chordMask = grid[(size_t) i];
        }
        juce::uint16 allowed = (juce::uint16) (chordMask | scaleMask);
        if (allowed == 0) allowed = 0x0FFF;
        int best = -1; double bestScore = 1e9;
        const int base = (int) std::lround (sungMidi);
        for (int p = base - 11; p <= base + 11; ++p)
        {
            if (p < 24 || p > 108 || ((allowed >> (p % 12)) & 1) == 0) continue;
            double sc = std::abs (p - sungMidi);
            if (chordMask != 0 && ((chordMask >> (p % 12)) & 1) == 0) sc += 0.6;
            if (sc < bestScore) { bestScore = sc; best = p; }
        }
        return best;
    }

    // YIN on the decimated ring: window 768 @fs/2, taus for 60..1300 Hz, CMND + parabolic
    float yin (float& confOut)
    {
        const double fs2 = fs * 0.5;
        const int W = 768;
        const int tauMin = juce::jmax (2, (int) (fs2 / 1300.0));
        const int tauMax = juce::jmin (ANA_N - W - 2, (int) (fs2 / 60.0));
        float buf[ANA_N];
        const int need = W + tauMax + 1;
        for (int i = 0; i < need; ++i)
            buf[i] = ana[(size_t) ((anaPos - need + i + 2 * ANA_N) & (ANA_N - 1))];
        double rms = 0;
        for (int i = need - W; i < need; ++i) rms += buf[i] * buf[i];
        if (std::sqrt (rms / W) < 1e-4) { confOut = 0; return 0.0f; }

        double running = 0; int bestTau = 0; double bestVal = 1e9;
        std::vector<double>& cm = cmndBuf;
        cm.assign ((size_t) tauMax + 1, 1.0);
        for (int tau = tauMin; tau <= tauMax; ++tau)
        {
            double d = 0;
            const float* a = buf + (need - W - tau);
            const float* b = buf + (need - W);
            for (int i = 0; i < W; ++i) { const double df = a[i] - b[i]; d += df * df; }
            running += d;
            const double cmnd = d * tau / (running > 1e-12 ? running : 1e-12);
            cm[(size_t) tau] = cmnd;
            if (cmnd < bestVal) { bestVal = cmnd; bestTau = tau; }
        }
        if (bestTau <= 0 || bestVal > 0.35) { confOut = 0; return 0.0f; }
        // subharmonic bias fix: the FUNDAMENTAL is the SMALLEST lag whose dip is
        // nearly as deep as the global best (dips repeat at every period multiple)
        int useTau = bestTau;
        const double thresh = juce::jmax (0.10, bestVal * 1.35);
        for (int tau = tauMin + 1; tau < bestTau; ++tau)
            if (cm[(size_t) tau] < thresh
                && cm[(size_t) tau] <= cm[(size_t) tau - 1]
                && cm[(size_t) tau] <= cm[(size_t) tau + 1]) { useTau = tau; break; }
        // parabolic refine around the chosen lag
        double tauF = (double) useTau;
        if (useTau > tauMin && useTau < tauMax)
        {
            const double c0 = cm[(size_t) useTau - 1], c1 = cm[(size_t) useTau], c2 = cm[(size_t) useTau + 1];
            const double den = c0 + c2 - 2.0 * c1;
            if (std::abs (den) > 1e-12) tauF += 0.5 * (c0 - c2) / den;
        }
        confOut = (float) (1.0 - bestVal);
        return (float) (fs2 / tauF);
    }

    signalsmith::stretch::SignalsmithStretch<float> stretch;
    juce::AudioBuffer<float> scratch, scratchOut;
    std::vector<float> ana;
    std::vector<double> cmndBuf;
    int anaPos = 0, lastTau = 0, dbgBlocks = 0;
    double fs = 44100.0, smoothRatio = 1.0, latencySec = 0.0;
    std::vector<juce::uint16> grid;
    juce::uint16 scaleMask = 0;

    juce::CachedValue<float> amountV, retuneMsV;
    juce::CachedValue<int> keyRootV, keyMinorV;
    juce::CachedValue<juce::String> gridV;
    tracktion::AutomatableParameter::Ptr amountP, retuneP;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (RetunePlugin)
};
