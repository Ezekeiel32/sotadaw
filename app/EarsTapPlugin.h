// EarsTapPlugin — THE EARS BUS R1 (E3, docs/EARS_BUS_DESIGN.md): realtime hearing
// for the agent WITHOUT touching the audio thread's real-time law.
//
//   audio callback ── memcpy into an AbstractFifo ring (SPSC, no locks/allocs) ──►
//   consumer thread ── 10 Hz feature frames {rms/peak L R, 4 bands, crest,
//   quick-dBTP, beat, playing} ──► agent/ipc/ears.jsonl (ring-truncated) ──►
//   sidecar NOW block / listen_live tool / dj_listener live kernel.
//
// LAWS (design doc §2): callback copies and does NOTHING else; ring full = frames
// drop, playback never degrades; consumer owns all math + file IO; ears.jsonl is
// gitignored (a live sensor, not telemetry); 1 Hz playing:false heartbeat while
// stopped so readers can tell silence from death. Offline m1 renders count as
// "playing" (isRendering) — the pipe proves headless.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include <atomic>
#include <cstdio>
#include <cmath>
#include <vector>

class EarsTapPlugin : public tracktion::Plugin,
                      private juce::Thread
{
public:
    static const char* getPluginName()          { return "EarsTap"; }
    inline static const char* xmlTypeName = "earsTap";

    EarsTapPlugin (tracktion::PluginCreationInfo info)
        : tracktion::Plugin (info), juce::Thread ("sotadaw-ears"),
          fifo (RING_N), ring ((size_t) RING_N, 0.0f) {}

    ~EarsTapPlugin() override
    {
        stopThread (2000);
        notifyListenersOfDeletion();
    }

    juce::String getName() const override            { return getPluginName(); }
    juce::String getPluginType() override            { return xmlTypeName; }
    juce::String getSelectableDescription() override { return getName(); }

    void initialise (const tracktion::PluginInitialisationInfo& info) override
    {
        fs.store (info.sampleRate);
        debugOn = std::getenv ("SOTADAW_EARS_DEBUG") != nullptr;
        resolveIpcDir();
        if (! isThreadRunning())
            startThread (juce::Thread::Priority::background);
        if (debugOn)
            std::fprintf (stderr, "[ears] tap up fs=%.0f ring=%d -> %s\n",
                          info.sampleRate, RING_N, jsonlPath.toRawUTF8());
    }

    void deinitialise() override { stopThread (2000); }

    // THE TAP (law 1): copy the master block into the ring; store transport
    // atomics. Full ring = partial write = the tail DROPS (hearing degrades
    // gracefully, playback never does). Audio passes through untouched.
    void applyToBuffer (const tracktion::PluginRenderContext& fc) override
    {
        if (fc.destBuffer == nullptr || fc.bufferNumSamples == 0)
            return;
        const int n   = fc.bufferNumSamples;
        const int nch = juce::jmin (2, fc.destBuffer->getNumChannels());
        playing.store (fc.isPlaying || fc.isRendering);
        editSec.store (fc.editTime.getStart().inSeconds());
        // per-block tempo lookup = in-repo precedent (RetunePlugin does the same)
        editBeat.store (edit.tempoSequence.toBeats (fc.editTime.getStart()).inBeats());

        int s1, n1, s2, n2;
        fifo.prepareToWrite (n * 2, s1, n1, s2, n2);
        // the free split can land mid-pair — write only WHOLE stereo pairs across
        // the (s1,n1)/(s2,n2) boundary or every later frame is channel-flipped
        const int pairs = (n1 + n2) / 2;
        auto slot = [&] (int k) -> float&
        { return ring[(size_t) (k < n1 ? s1 + k : s2 + (k - n1))]; };
        for (int i = 0; i < pairs; ++i)
        {
            const int src = fc.bufferStartSample + i;
            slot (i * 2)     = fc.destBuffer->getSample (0, src);
            slot (i * 2 + 1) = fc.destBuffer->getSample (juce::jmin (1, nch - 1), src);
        }
        fifo.finishedWrite (pairs * 2);
    }

private:
    static constexpr int RING_N = 1 << 16;           // interleaved floats (~0.74 s @ 44.1k)
    juce::AbstractFifo fifo;
    std::vector<float> ring;
    std::atomic<double> fs { 44100.0 }, editSec { 0.0 }, editBeat { 0.0 };
    std::atomic<bool> playing { false };
    bool debugOn = false;
    juce::String jsonlPath;
    int lineCount = -1;

    // RBJ biquad — the consumer's band ears (no juce_dsp dependency)
    struct Biquad
    {
        double b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0, z1 = 0, z2 = 0;
        void set (double B0, double B1, double B2, double A0, double A1, double A2)
        { b0 = B0 / A0; b1 = B1 / A0; b2 = B2 / A0; a1 = A1 / A0; a2 = A2 / A0; z1 = z2 = 0; }
        void lowpass (double sr, double f0, double q)
        {
            const double w = 2 * juce::MathConstants<double>::pi * f0 / sr;
            const double c = std::cos (w), a = std::sin (w) / (2 * q);
            set ((1 - c) / 2, 1 - c, (1 - c) / 2, 1 + a, -2 * c, 1 - a);
        }
        void highpass (double sr, double f0, double q)
        {
            const double w = 2 * juce::MathConstants<double>::pi * f0 / sr;
            const double c = std::cos (w), a = std::sin (w) / (2 * q);
            set ((1 + c) / 2, -(1 + c), (1 + c) / 2, 1 + a, -2 * c, 1 - a);
        }
        void bandpass (double sr, double f0, double q)
        {
            const double w = 2 * juce::MathConstants<double>::pi * f0 / sr;
            const double c = std::cos (w), a = std::sin (w) / (2 * q);
            set (a, 0, -a, 1 + a, -2 * c, 1 - a);
        }
        inline double proc (double x)
        { const double y = b0 * x + z1; z1 = b1 * x - a1 * y + z2; z2 = b2 * x - a2 * y; return y; }
    };

    void resolveIpcDir()
    {
        // SOTADAW_IPC = the same isolation convention as the sidecar/UI
        juce::File ipc;
        if (const char* e = std::getenv ("SOTADAW_IPC"))
            ipc = juce::File (juce::String (e));
        else
            ipc = sotadawRootForEars().getChildFile ("agent/ipc");
        ipc.createDirectory();
        jsonlPath = ipc.getChildFile ("ears.jsonl").getFullPathName();
    }

    // SongLoader's sotadawRoot() is declared later in the include graph — keep
    // the tap self-contained with the same walk-up-for-songs/ rule.
    static juce::File sotadawRootForEars()
    {
        auto f = juce::File::getSpecialLocation (juce::File::currentExecutableFile);
        for (int i = 0; i < 8 && f != juce::File(); ++i)
        {
            if (f.getChildFile ("songs").isDirectory()
                && f.getChildFile ("agent").isDirectory())
                return f;
            f = f.getParentDirectory();
        }
        return juce::File::getCurrentWorkingDirectory();
    }

    // THE CONSUMER (laws 2-5): drain at ~10 Hz, fold PCM into one small frame,
    // append a jsonl line, truncate the file when it outgrows ~2000 lines.
    void run() override
    {
        Biquad low, lowmid, mid, high;
        double bandFs = 0;
        std::vector<float> chunk;
        chunk.reserve (RING_N);
        int framesSinceDebug = 0;
        juce::int64 lastHeartbeatMs = 0;

        while (! threadShouldExit())
        {
            wait (100);
            const double sr = fs.load();
            if (sr != bandFs && sr > 0)      // (re)tune the band ears to the stream
            {
                bandFs = sr;
                low.lowpass   (sr, 250.0,  0.707);
                lowmid.bandpass (sr, 447.0, 0.81);   // 250..800
                mid.bandpass  (sr, 1789.0, 0.56);    // 800..4k
                high.highpass (sr, 4000.0, 0.707);
            }

            chunk.clear();
            int s1, n1, s2, n2;
            fifo.prepareToRead (fifo.getNumReady(), s1, n1, s2, n2);
            for (int i = 0; i < n1; ++i) chunk.push_back (ring[(size_t) (s1 + i)]);
            for (int i = 0; i < n2; ++i) chunk.push_back (ring[(size_t) (s2 + i)]);
            fifo.finishedRead (n1 + n2);

            const auto nowMs = juce::Time::currentTimeMillis();
            if (chunk.size() < 4)
            {
                // heartbeat: 1 Hz playing:false so readers can tell silence from death
                if (nowMs - lastHeartbeatMs >= 1000)
                {
                    lastHeartbeatMs = nowMs;
                    writeFrame (nowMs, editBeat.load(), editSec.load(),
                                -120, -120, -120, -120, -120,
                                -120, -120, -120, -120, 0, false);
                }
                continue;
            }

            double sqL = 0, sqR = 0, pkL = 0, pkR = 0, pkQ = 0;
            double bsq[4] = { 0, 0, 0, 0 };
            double prevL = 0, prevR = 0;
            const int frames = (int) chunk.size() / 2;
            for (int i = 0; i < frames; ++i)
            {
                const double l = chunk[(size_t) (i * 2)], r = chunk[(size_t) (i * 2 + 1)];
                sqL += l * l; sqR += r * r;
                pkL = juce::jmax (pkL, std::abs (l)); pkR = juce::jmax (pkR, std::abs (r));
                // quick ISP estimate: per-channel 2x midpoint interpolation peaks
                pkQ = juce::jmax (pkQ, std::abs (l), std::abs (r));
                pkQ = juce::jmax (pkQ, std::abs (0.5 * (l + prevL)), std::abs (0.5 * (r + prevR)));
                prevL = l; prevR = r;
                const double m = 0.5 * (l + r);
                const double bl = low.proc (m), blm = lowmid.proc (m),
                             bm = mid.proc (m), bh = high.proc (m);
                bsq[0] += bl * bl; bsq[1] += blm * blm; bsq[2] += bm * bm; bsq[3] += bh * bh;
            }
            auto db = [] (double v) { return 20.0 * std::log10 (v + 1e-12); };
            const double rmsL = db (std::sqrt (sqL / frames)), rmsR = db (std::sqrt (sqR / frames));
            const double rms  = 0.5 * (rmsL + rmsR);
            const double peak = db (juce::jmax (pkL, pkR));
            writeFrame (nowMs, editBeat.load(), editSec.load(),
                        rmsL, rmsR, db (pkL), db (pkR), db (pkQ),
                        db (std::sqrt (bsq[0] / frames)), db (std::sqrt (bsq[1] / frames)),
                        db (std::sqrt (bsq[2] / frames)), db (std::sqrt (bsq[3] / frames)),
                        peak - rms, playing.load());
            if (debugOn && ++framesSinceDebug >= 10)
            {
                framesSinceDebug = 0;
                std::fprintf (stderr, "[ears] beat=%.1f rms=%.1f peak=%.1f bands=%.0f/%.0f/%.0f/%.0f playing=%d\n",
                              editBeat.load(), rms, peak,
                              db (std::sqrt (bsq[0] / frames)), db (std::sqrt (bsq[1] / frames)),
                              db (std::sqrt (bsq[2] / frames)), db (std::sqrt (bsq[3] / frames)),
                              (int) playing.load());
            }
        }
    }

    void writeFrame (juce::int64 tMs, double beat, double sec,
                     double rmsL, double rmsR, double pkL, double pkR, double dbtpQ,
                     double b0, double b1, double b2, double b3,
                     double crest, bool isPlaying)
    {
        // R6 JAM RELIABILITY: the live organ carries the device's health too —
        // xruns (cumulative since device start; renders have no live device so
        // it reads 0 = the negative control) + callback cpu load. Consumer
        // thread; both reads are atomic-backed in juce/tracktion.
        int xr = 0;
        double cpu = 0.0;
        xr   = juce::jmax (0, edit.engine.getDeviceManager().deviceManager.getXRunCount());
        cpu  = edit.engine.getDeviceManager().getCpuUsage();
        char line[420];
        std::snprintf (line, sizeof (line),
            "{\"t\":%.2f,\"beat\":%.2f,\"sec\":%.2f,\"playing\":%s,"
            "\"rms_db\":[%.1f,%.1f],\"peak_db\":[%.1f,%.1f],\"dbtp_q\":%.1f,"
            "\"bands_db\":[%.1f,%.1f,%.1f,%.1f],\"crest_db\":%.1f,"
            "\"xruns\":%d,\"cpu\":%.2f}\n",
            tMs / 1000.0, beat, sec, isPlaying ? "true" : "false",
            rmsL, rmsR, pkL, pkR, dbtpQ, b0, b1, b2, b3, crest, xr, cpu);
        juce::File f (jsonlPath);
        if (lineCount < 0)      // first write this run: count what's already there
        {
            juce::StringArray existing;
            f.readLines (existing);
            lineCount = existing.size();
        }
        if (lineCount > 2000)   // law 3: the writer ring-truncates its own file
        {
            juce::StringArray keep;
            f.readLines (keep);
            keep.removeRange (0, juce::jmax (0, keep.size() - 1500));
            f.replaceWithText (keep.joinIntoString ("\n") + "\n");
            lineCount = keep.size();
        }
        f.appendText (juce::String (line), false, false, nullptr);
        ++lineCount;
    }
};
