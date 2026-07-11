// JamPlayer — THE SPEAKERS WIRE for THE LIVE JAM. The proven realtime scheduler
// (tools/jam_live.py) renders phrase N+1 while phrase N plays; this is the one
// wire that is honestly the app's, not the band's: audio to the speakers. Each
// ready phrase wav is PRELOADED into memory on the message thread and chained
// GAPLESSLY on the shared audio device (PreviewPlayer's second-callback pattern
// — the engine keeps its own callback). The band's LISTENING is untouched: the
// EarsTap taps the master graph inside each phrase's render identically whether
// audio goes to a device or a file; only the output sink differs.
//
// B6 THE BANDSTAND: phrases carry a TAIL past their musical length (the send
// reverb's ring-out) — the player chains at the MUSICAL boundary and overlap-adds
// the previous phrase's tail under the next one, so the room never hears a
// chopped-reverb seam. A master gain (the BAND fader) rides the whole wire, and
// finishAfterCurrent() = the graceful STOP: the queue truncates to the playing
// phrase, the band ends ON the phrase like a band.
#pragma once
#include <juce_audio_devices/juce_audio_devices.h>
#include <juce_audio_formats/juce_audio_formats.h>

namespace sotadaw
{

class JamPlayer : public juce::AudioSource
{
public:
    explicit JamPlayer (juce::AudioDeviceManager& dmToUse) : dm (dmToUse)
    {
        fm.registerBasicFormats();
        resampler = std::make_unique<juce::ResamplingAudioSource> (this, false, 2);
    }
    ~JamPlayer() override { stop(); }

    // preload the phrase on the MESSAGE thread (the audio thread never sees a
    // file). musicalSec > 0 = the phrase's MUSICAL length; anything in the wav
    // beyond it is TAIL, overlap-added under the next phrase. 0 = whole file.
    bool enqueue (const juce::File& wav, double musicalSec = 0.0)
    {
        std::unique_ptr<juce::AudioFormatReader> r (fm.createReaderFor (wav));
        if (r == nullptr || r->lengthInSamples <= 0) return false;
        auto buf = std::make_shared<juce::AudioBuffer<float>> (2, (int) r->lengthInSamples);
        r->read (buf.get(), 0, (int) r->lengthInSamples, 0, true, true);
        if (r->numChannels == 1)
            buf->copyFrom (1, 0, *buf, 0, 0, buf->getNumSamples());
        const int total = buf->getNumSamples();
        const int musical = musicalSec > 0.0
            ? juce::jlimit (1, total, (int) std::llround (musicalSec * r->sampleRate))
            : total;
        {
            const juce::SpinLock::ScopedLockType sl (lock);
            phrases.push_back ({ std::move (buf), musical });
            fileRate = r->sampleRate;
        }
        if (! running)
        {
            if (noDevice) { deviceRate = r->sampleRate; running = true; }
            else          start (r->sampleRate);
        }
        else if (! noDevice)
            resampler->setResamplingRatio (r->sampleRate / juce::jmax (1.0, deviceRate));
        return true;
    }

    // THE PUNCH-IN (player half): the scheduler's punch_ready wav replaces the
    // TAIL of a phrase from its interior bar line, entered through a ~16ms
    // crossfade — a band-mate turning mid-bar, never a click. Message thread
    // preloads; the audio thread only flips cursors + one bounded fade.
    // frac = the line's position within the phrase's MUSICAL span (0..1).
    // >100ms past the line the moment is gone and the punch is dropped.
    bool punchIn (int phraseIdx, double frac, const juce::File& wav, double musicalSec = 0.0)
    {
        std::unique_ptr<juce::AudioFormatReader> r (fm.createReaderFor (wav));
        if (r == nullptr || r->lengthInSamples <= 0) return false;
        auto buf = std::make_shared<juce::AudioBuffer<float>> (2, (int) r->lengthInSamples);
        r->read (buf.get(), 0, (int) r->lengthInSamples, 0, true, true);
        if (r->numChannels == 1)
            buf->copyFrom (1, 0, *buf, 0, 0, buf->getNumSamples());
        const int ptotal = buf->getNumSamples();
        const int pmusical = musicalSec > 0.0
            ? juce::jlimit (1, ptotal, (int) std::llround (musicalSec * r->sampleRate))
            : ptotal;
        const juce::SpinLock::ScopedLockType sl (lock);
        if (phraseIdx < 0 || phraseIdx >= (int) phrases.size()) return false;
        const int at = (int) std::llround (juce::jlimit (0.0, 1.0, frac)
                          * (double) phrases[(size_t) phraseIdx].musical);
        if (cur > phraseIdx
            || (cur == phraseIdx && pos > at + (int) (0.1 * fileRate)))
            return false;
        punchBuf = std::move (buf);
        punchMusical = pmusical;
        punchPhrase = phraseIdx;
        punchAt = at;
        punchPos = -1;
        fadeLeft = 0;
        return true;
    }

    // B6 graceful STOP: drop everything QUEUED beyond the playing phrase — the
    // current phrase plays to its end, then the wire starves and the set is over.
    void finishAfterCurrent()
    {
        const juce::SpinLock::ScopedLockType sl (lock);
        if ((int) phrases.size() > cur + 1)
            phrases.resize ((size_t) cur + 1);
        if (punchPhrase > cur)                    // a punch for a dropped phrase
        { punchBuf = nullptr; punchPhrase = -1; punchPos = -1; fadeLeft = 0; }
    }

    // the BAND fader: one gain on the whole wire (audio thread reads it atomically)
    void  setGain (float g)     { gain.store (juce::jlimit (0.0f, 1.5f, g)); }
    float getGain() const       { return gain.load(); }

    void stop()
    {
        if (running)
        {
            player.setSource (nullptr);
            if (! noDevice)
                dm.removeAudioCallback (&player);
            running = false;
        }
        const juce::SpinLock::ScopedLockType sl (lock);
        phrases.clear();
        punchBuf = nullptr; punchPhrase = -1; punchPos = -1; fadeLeft = 0;
        tailBuf = nullptr; tailPos = 0;
        cur = 0; pos = 0;
    }

    bool noDevice = false;   // rig: pump getNextAudioBlock directly, no callback

    bool  active() const        { return running; }
    int   currentPhrase() const { return cur; }
    // set progress in phrase units (e.g. 2.4 = phrase 2, 40% in) for the UI
    double progress() const
    {
        const juce::SpinLock::ScopedLockType sl (lock);
        if (phrases.empty()) return 0.0;
        const int n = juce::jmax (1, phrases[(size_t) juce::jmin (cur, (int) phrases.size() - 1)].musical);
        return (double) cur + (double) pos / (double) n;
    }
    int   queued() const
    {
        const juce::SpinLock::ScopedLockType sl (lock);
        return (int) phrases.size();
    }
    bool  starved() const { return running && starvedFlag; }

private:
    void start (double srcRate)
    {
        deviceRate = dm.getCurrentAudioDevice() != nullptr
                       ? dm.getCurrentAudioDevice()->getCurrentSampleRate() : 44100.0;
        resampler->setResamplingRatio (srcRate / juce::jmax (1.0, deviceRate));
        player.setSource (resampler.get());
        dm.addAudioCallback (&player);
        running = true;
    }

    void prepareToPlay (int, double) override {}
    void releaseResources() override {}

    // the previous phrase's ring-out mixed under the region just written
    void mixTail (juce::AudioBuffer<float>& dst, int dstStart, int n)
    {
        if (tailBuf == nullptr || n <= 0) return;
        const int avail = juce::jmin (n, tailBuf->getNumSamples() - tailPos);
        if (avail > 0)
            for (int ch = 0; ch < dst.getNumChannels(); ++ch)
                dst.addFrom (ch, dstStart, *tailBuf, juce::jmin (ch, 1), tailPos, avail);
        tailPos += avail;
        if (tailPos >= tailBuf->getNumSamples()) { tailBuf = nullptr; tailPos = 0; }
    }
    // a phrase (or punch) crossed its musical end: its remainder becomes THE tail
    void stashTail (const std::shared_ptr<juce::AudioBuffer<float>>& buf, int from)
    {
        if (buf != nullptr && from < buf->getNumSamples()) { tailBuf = buf; tailPos = from; }
        else                                               { tailBuf = nullptr; tailPos = 0; }
    }

    void getNextAudioBlock (const juce::AudioSourceChannelInfo& info) override
    {
        info.clearActiveBufferRegion();
        const juce::SpinLock::ScopedTryLockType sl (lock);   // NEVER block the audio thread
        if (! sl.isLocked()) return;
        int out = 0;
        while (out < info.numSamples && cur < (int) phrases.size())
        {
            auto& ph = phrases[(size_t) cur];
            auto& base = *ph.buf;
            const bool armed = punchBuf != nullptr && cur == punchPhrase;
            if (armed && punchPos < 0 && pos >= punchAt)
            {   // the bar line: enter the punch through the fade
                punchPos = pos - punchAt;
                fadeLeft = fadeLen;
            }
            const bool onPunch = armed && punchPos >= 0;
            if (onPunch && fadeLeft > 0)
            {   // crossfade: base rings out under the punch for ~16ms
                auto& pb = *punchBuf;
                const int n = juce::jmin (juce::jmin (fadeLeft, info.numSamples - out),
                                          juce::jmin (pb.getNumSamples() - punchPos,
                                                      juce::jmax (1, base.getNumSamples() - pos)));
                if (n <= 0) { fadeLeft = 0; continue; }
                for (int ch = 0; ch < info.buffer->getNumChannels(); ++ch)
                {
                    auto* dst = info.buffer->getWritePointer (ch, info.startSample + out);
                    auto* pOld = base.getReadPointer (juce::jmin (ch, 1));
                    auto* pNew = pb.getReadPointer (juce::jmin (ch, 1));
                    for (int i = 0; i < n; ++i)
                    {
                        const float t = (float) (fadeLen - fadeLeft + i) / (float) fadeLen;
                        const float old = pos + i < base.getNumSamples() ? pOld[pos + i] : 0.0f;
                        dst[i] = old * (1.0f - t) + pNew[punchPos + i] * t;
                    }
                }
                mixTail (*info.buffer, info.startSample + out, n);
                pos += n; punchPos += n; fadeLeft -= n; out += n;
                continue;
            }
            auto& b = onPunch ? *punchBuf : base;
            int avail = (onPunch ? punchMusical - punchPos
                                 : ph.musical - pos);
            if (! onPunch && armed)              // stop AT the line so entry is exact
                avail = juce::jmin (avail, punchAt - pos);
            if (avail <= 0)
            {
                if (onPunch)
                {   // punch tail-of-phrase exhausted: ITS ring becomes the tail
                    stashTail (punchBuf, punchMusical);
                    ++cur; pos = 0;
                    punchBuf = nullptr; punchPhrase = -1; punchPos = -1;
                }
                else if (! armed)
                {   // phrase exhausted at its MUSICAL end: chain, ring the remainder
                    stashTail (ph.buf, ph.musical);
                    ++cur; pos = 0;
                }
                continue;                        // armed at the line: loop re-enters as punch
            }
            const int n = juce::jmin (avail, info.numSamples - out);
            for (int ch = 0; ch < info.buffer->getNumChannels(); ++ch)
                info.buffer->copyFrom (ch, info.startSample + out,
                                       b, juce::jmin (ch, 1),
                                       onPunch ? punchPos : pos, n);
            mixTail (*info.buffer, info.startSample + out, n);
            (onPunch ? punchPos : pos) += n;
            out += n;
        }
        if (out < info.numSamples && cur >= (int) phrases.size())
            mixTail (*info.buffer, info.startSample + out, info.numSamples - out);
        const float g = gain.load (std::memory_order_relaxed);
        if (g != 1.0f)
            info.buffer->applyGain (info.startSample, info.numSamples, g);
        // THE DAC GUARD (2026-07-11 "loud horrid sound"): phrases are walled at
        // -1.2 dBTP, but the tail overlap-add SUMS ring + next phrase — a rare
        // over soft-knees into +-1 instead of slamming the converter. |x| <= 0.9
        // passes untouched (the punchplay DC plateaus stay byte-exact).
        for (int ch = 0; ch < info.buffer->getNumChannels(); ++ch)
        {
            auto* d = info.buffer->getWritePointer (ch, info.startSample);
            for (int i = 0; i < info.numSamples; ++i)
            {
                const float ax = std::abs (d[i]);
                if (ax > 0.9f)
                    d[i] = (d[i] > 0 ? 1.0f : -1.0f)
                           * (0.9f + 0.1f * std::tanh ((ax - 0.9f) * 10.0f));
            }
        }
        starvedFlag = out < info.numSamples && cur >= (int) phrases.size() && ! phrases.empty();
    }

    struct Phrase
    {
        std::shared_ptr<juce::AudioBuffer<float>> buf;
        int musical = 0;                          // samples; buf beyond this = tail
    };

    juce::AudioDeviceManager& dm;
    juce::AudioFormatManager fm;
    juce::AudioSourcePlayer player;
    std::unique_ptr<juce::ResamplingAudioSource> resampler;
    mutable juce::SpinLock lock;
    std::vector<Phrase> phrases;
    std::shared_ptr<juce::AudioBuffer<float>> punchBuf;
    std::shared_ptr<juce::AudioBuffer<float>> tailBuf;
    int tailPos = 0;
    int punchPhrase = -1, punchAt = 0, punchPos = -1, punchMusical = 0;
    int fadeLeft = 0;
    static constexpr int fadeLen = 768;          // ~16ms @48k: turn, never click
    int cur = 0, pos = 0;
    double fileRate = 44100.0, deviceRate = 44100.0;
    bool running = false;
    std::atomic<float> gain { 1.0f };
    std::atomic<bool> starvedFlag { false };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (JamPlayer)
};

} // namespace sotadaw
