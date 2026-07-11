// PreviewPlayer — plays short wavs (preset auditions) alongside the engine by
// adding a second audio callback on the shared device. Self-contained.
#pragma once
#include <juce_audio_devices/juce_audio_devices.h>
#include <juce_audio_formats/juce_audio_formats.h>

namespace sotadaw
{

class PreviewPlayer
{
public:
    explicit PreviewPlayer (juce::AudioDeviceManager& dmToUse) : dm (dmToUse)
    {
        fm.registerBasicFormats();
        player.setSource (&transport);
        dm.addAudioCallback (&player);
    }
    ~PreviewPlayer()
    {
        dm.removeAudioCallback (&player);
        transport.setSource (nullptr);
    }

    void play (const juce::File& wav)
    {
        stop();
        if (auto* reader = fm.createReaderFor (wav))
        {
            source.reset (new juce::AudioFormatReaderSource (reader, true));
            transport.setSource (source.get(), 0, nullptr, reader->sampleRate);
            transport.setPosition (0);
            transport.start();
        }
    }
    void stop()
    {
        transport.stop();
        transport.setSource (nullptr);
        source.reset();
    }

private:
    juce::AudioDeviceManager& dm;
    juce::AudioFormatManager fm;
    juce::AudioTransportSource transport;
    juce::AudioSourcePlayer player;
    std::unique_ptr<juce::AudioFormatReaderSource> source;
};

} // namespace sotadaw
