// PluginGuard — V49 v1 (SPEC v2.6): crash quarantine for external plugins.
//
// THE FLIGHT RECORDER: in-process VST3 hosting means a crashing plugin takes the
// whole app — and with "every VST is a tool" the fleet WILL meet crashers. v1
// makes the blast radius one boot: before any risky external-plugin operation
// (instantiation, state-blob load) stamp a flight file naming the plugin; clear
// it on success. A boot that finds a stale flight file knows the last session
// died INSIDE that operation — the named plugin is promoted to the quarantine
// list and skipped at load (visibly, reversibly). The session itself is already
// safe on disk (crash journal + git).
//
// v2 (Beyond, SPEC V49): per-plugin process bridging, Bitwig-tier.
//
// Wiring (one micro-burst, coordinate via agents_collab):
//   SongLoader makeFaustFxInner/buildTrackSource vst3 branches:
//       if (PluginGuard::isQuarantined (name)) { skip + note; }
//       PluginGuard::begin (name, "instantiate"); ... PluginGuard::end();
//   m1 main() + sotadaw boot:  PluginGuard::promoteStaleFlight() -> log/chip.
//   UI (face-f5's lane): quarantine chip on the rack slot, click = unquarantine.
#pragma once
#include <juce_core/juce_core.h>

namespace sotadaw
{
struct PluginGuard
{
    static juce::File configDir()
    {
        // userApplicationDataDirectory IS ~/.config on Linux (house pattern: lane_heights.json)
        auto d = juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
                     .getChildFile ("sotadaw");
        d.createDirectory();
        return d;
    }

    static juce::File flightFile()     { return configDir().getChildFile ("plugin_flight.json"); }
    static juce::File quarantineFile() { return configDir().getChildFile ("plugin_quarantine.json"); }

    /** Stamp the flight recorder before a risky plugin operation. */
    static void begin (const juce::String& plugin, const juce::String& phase)
    {
        auto* o = new juce::DynamicObject();
        o->setProperty ("plugin", plugin);
        o->setProperty ("phase", phase);
        o->setProperty ("t", juce::Time::getCurrentTime().toISO8601 (true));
        flightFile().replaceWithText (juce::JSON::toString (juce::var (o)));
    }

    /** The operation survived — clear the recorder. */
    static void end()
    {
        flightFile().deleteFile();
    }

    /** V49 v1.5 THE HANG NAMER: the flight that is OPEN right now ("" = none).
        A crash leaves the file for boot promotion; a HANG leaves it while the
        transport stalls — the UI watchdog reads this to NAME the offender. */
    static juce::String currentFlight()
    {
        auto f = flightFile();
        if (! f.existsAsFile())
            return {};
        const auto v = juce::JSON::parse (f.loadFileAsString());
        const auto name = v.getProperty ("plugin", juce::var()).toString();
        const auto phase = v.getProperty ("phase", juce::var()).toString();
        return name.isEmpty() ? juce::String() : name + " (" + phase + ")";
    }

    /** Boot-time: a stale flight file means the last session died inside a plugin
        operation. Promote that plugin to quarantine. Returns its name ("" = clean boot). */
    static juce::String promoteStaleFlight()
    {
        auto f = flightFile();
        if (! f.existsAsFile())
            return {};

        auto v = juce::JSON::parse (f.loadFileAsString());
        const auto name = v.getProperty ("plugin", juce::var()).toString();
        f.deleteFile();

        if (name.isEmpty() || isQuarantined (name))
            return name;

        auto list = readList();
        list.append (name);
        quarantineFile().replaceWithText (juce::JSON::toString (list));
        return name;
    }

    static bool isQuarantined (const juce::String& plugin)
    {
        const auto list = readList();   // the array pointer lives INSIDE this var
        if (auto* arr = list.getArray())
            for (auto& e : *arr)
                if (e.toString().equalsIgnoreCase (plugin))
                    return true;
        return false;
    }

    /** The user's "retry" door — remove a plugin from quarantine. */
    static void unquarantine (const juce::String& plugin)
    {
        auto list = readList();
        if (auto* arr = list.getArray())
        {
            arr->removeIf ([&] (const juce::var& e) { return e.toString().equalsIgnoreCase (plugin); });
            quarantineFile().replaceWithText (juce::JSON::toString (list));
        }
    }

private:
    static juce::var readList()
    {
        auto f = quarantineFile();
        if (f.existsAsFile())
        {
            auto v = juce::JSON::parse (f.loadFileAsString());
            if (v.isArray())
                return v;
        }
        return juce::var (juce::Array<juce::var>());
    }
};
} // namespace sotadaw
