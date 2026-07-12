// song.json v2 -> te::Edit. THE single builder, used by m1 (render) and the UI (playback).
//
// v2 schema (v0/v1-compatible):
// { "version": 2, "bpm": 142, "key": "F minor", "lengthBars": 8,
//   "swing": {"grid": "16th", "amount": 0.56},           // 0.5 = straight
//   "sections": [{"name": "intro", "startBar": 0}],
//   "masterGainDb": 0.0,
//   "master": [{"type": "faustfx", "id": "master_limiter", "params": {"ceiling": -1.0}}],
//   "buses": [{"id": "verb", "gainDb": 0, "fx": [{"id": "fx_reverb", "params": {...}}]}],
//   "automation": [{"target": "masterGainDb", "points": [{"beat":0,"v":-6},{"beat":32,"v":0}]}],
//   "tracks": [{
//     "name": "808", "gainDb": -3, "pan": 0,
//     "source": {"kind": "faust", "id": "kick_808", "params": {"decay": 0.4}}   // or v0: "instrument"
//              | {"kind": "sample", "kit": "gm_drums"}
//              | {"kind": "vst3", "plugin": "Dexed", "params": {"cutoff": 0.6}},
//     "fx": [{"id": "fx_widen", "params": {"width": 0.4}}],                // optional track FX
//     "sends": [{"bus": "verb", "gainDb": -12}],
//     "automation": [{"target": "fx[0].width",          // gainDb | pan | fx[i].<param> | source.<param>
//                     "points": [{"beat": 0, "v": 0.0}, {"beat": 16, "v": 0.9}]}],
//     "notes": [{"start": 0, "len": 1.4, "pitch": 29, "vel": 1.0}] }] }
// Automation values are in REAL units (dB for gainDb, the zone's own range for faust params,
// 0..1 normalized for vst3 params). Point curve -1..1 shapes the segment leaving it:
// 0 = linear, >0 = late-bloom (hold then accelerate), <0 = early-jump. Engine-verified.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include "FaustInstrumentPlugin.h"
#include "SpectralVoicePlugin.h"
#include "FaustFxPlugin.h"
#include "RetunePlugin.h"
#include "EarsTapPlugin.h"
#include "NamPlugin.h"
#include "ClapPlugin.h"
#include "PluginGuard.h"

namespace sotadaw
{
namespace te = tracktion;

struct SongNote  { double start = 0, len = 0.25; int pitch = 60; double vel = 0.8;
                   double chance = 1.0; };   // HB5: render-time inclusion probability (seeded, reproducible)

// PER-NOTE CHANCE (HB5): a note with chance<1 is included in a render by a deterministic
// hash of its own identity — so renders are REPRODUCIBLE (the generative-seed law), and
// chance=0.5 keeps a fixed ~half. Re-roll variation by nudging note starts / a future seed.
inline bool noteIncluded (const SongNote& n, int idx)
{
    if (n.chance >= 0.999) return true;
    if (n.chance <= 0.001) return false;
    juce::uint32 h = (juce::uint32) (n.pitch * 2654435761u)
                   ^ (juce::uint32) ((juce::int64) (n.start * 480.0) * 40503u)
                   ^ (juce::uint32) (idx * 2246822519u);
    h ^= h >> 13; h *= 0x5bd1e995u; h ^= h >> 15;
    return (double) (h & 0xffffffu) / (double) 0x1000000u < n.chance;
}
// type: "faustfx" (default, id = dsp name) | "eq" (Tracktion 4-band) | "comp" (Tracktion compressor)
// bypass: true = plugin created but disabled (A/B in the rack; renders honor it too)
struct SongFx    { juce::String id; juce::String type { "faustfx" }; juce::String preset;
                   bool bypass = false; std::map<juce::String, float> params; };
// audio on the timeline: stems, chops, recorded takes. file relative to repo root or absolute.
// lengthBeats 0 = rest of file. offsetSec = start offset INTO the file.
struct SongAudioClip { juce::String file; double startBeat = 0, lengthBeats = 0, offsetSec = 0, gainDb = 0,
                       sourceBpm = 0;      // >0 = WARP: stretch to follow the song tempo
                       juce::String stretch;  // V46: "" = hq (signalsmith when patched in), "fast" = SoundTouch
                       double fadeInBeats = 0, fadeOutBeats = 0;   // V46: edge fades (0 = none)
                       juce::String fadeCurve;                     // linear (default) | convex | concave | s
                       juce::var tuning; };// CONTEXT-TUNE provenance {style,source,report} — OPAQUE round-trip
struct SongAutoPoint { double beat = 0, v = 0, curve = 0; };
struct SongAuto  { juce::String target; std::vector<SongAutoPoint> points; };
struct SongSend  { juce::String bus; double gainDb = -6; };
struct SongBus   { juce::String id; double gainDb = 0; std::vector<SongFx> fx; };
struct SongSource
{
    juce::String kind { "faust" };    // faust | sample | vst3 | audio
    juce::String id;                  // faust dsp name | kit name | plugin name
    juce::String preset;              // vst3: path to a captured state blob (library/presets/*.preset)
    std::map<juce::String, float> params;
};
struct SongSlot                        // launcher cell: a loopable pattern (present=false = empty cell)
{
    bool present = false;
    juce::String name;
    double lengthBeats = 16;
    std::vector<SongNote> notes;
    juce::String audioFile;            // audio loop slot (stems->slots): file wins over notes
    double offsetSec = 0;              // where in the file this loop starts
    double sourceBpm = 0;              // >0 = warp the loop to the song tempo
    juce::String stretch;              // V46: "" = hq (signalsmith when patched in), "fast" = SoundTouch
    juce::String follow;               // scene-story grammar (Live 12 law): "next" |
                                       // "any" | "stop" — what the launcher does when
                                       // this clip finishes; empty = loop as today
    double followChance = 1.0;         // WF13 law: probability the follow fires
                                       // (else the clip runs again) — weighted
                                       // engine actions, 1.0 = always
};
struct SongTrack
{
    juce::String name;
    SongSource source;                 // kind: faust | sample | vst3 | audio (audio = clips only, no synth)
    double gainDb = 0, pan = 0;
    bool muted = false;
    bool locked = false;   // EDIT LOCK: the agent may never modify this track (sidecar-enforced)
    juce::String color;    // "#rrggbb" — the channel's OWN colour (empty = position ring)
    std::vector<SongFx> fx;
    std::vector<SongSend> sends;
    std::vector<SongAuto> automation;
    std::vector<SongNote> notes;
    std::vector<SongAudioClip> audioClips;
    std::vector<SongSlot> slots;       // launcher column cells (index = scene)
    juce::String grooveName;           // provenance tag from apply_groove (feel is baked in notes)
    double grooveAmount = 0;
};
struct SongSection { juce::String name; double startBar = 0; };
struct SongMidiMap { int cc = -1; juce::String track, param; };   // W7: CC -> named param on a track ("master" = master chain)
struct SongTempoPoint { double bar = 0, bpm = 120, curve = 1; };  // tempo map: curve shapes the span FROM this point:
                                                                  // 1 = hold then step at the next point (default), 0 = linear ramp, <0 = early jump
// THE CHORD TRACK (BEST_DAW_30 #2): chords[] {bar 1-based, chord "Am7", conf}
// has NINE python writers (chordvote/suggest/reharm/finish/import) and until
// now zero engine READERS — the retune grid re-inferred harmony from notes
// while the declared truth rode along unread. Parsed here; serialization stays
// the passthrough (extras) — this build never rewrites another layer's field.
struct SongChord { double bar = 1; int rootPc = 0; int mask = 0; };

// THE WORLD GRID (BEST_DAW_30 #1): meterMap[] {bar, num, den} — the tempoMap's
// twin. Until now the entire world was HARD 4/4 (a carnatic tala, a waltz, a
// 7/8 prog riff were unrepresentable). Notes stay QUARTER-BEAT absolute (zero
// migration; absent map = exactly yesterday); the map redefines what a BAR is:
// ruler/roll bars, engine time-signatures (click, MIDI/DAW exports), and every
// bar->beat conversion route through barStartBeat()/beatsInBar().
struct SongMeterPoint { double bar = 0; int num = 4, den = 4; };

// THE MODULATION GRAPH (BEST_DAW_30 #3): motion/keying as song objects. The
// vendored engine always had the machinery (LFOModifier / EnvelopeFollower-
// Modifier + AutomatableParameter::addModifier) — nothing in the schema could
// reach it: fx_pump faked sidechain as a beat-clock duck and no track could
// key another's dynamics. modulators[] rides the automation target DSL:
//   {"kind":"lfo","target":"tracks.pads.fx[0].cutoff","rateHz":0.5|"sync":"1/4",
//    "depth":0.4,"shape":0,"phase":0,"bipolar":1}
//   {"kind":"follower","source":"kick","target":"tracks.bass.gainDb",
//    "attackMs":4,"releaseMs":110,"depth":-0.6}   // negative depth = the DUCK
struct SongModulator
{
    juce::String kind { "lfo" }, target, source, sync;
    double rateHz = 1.0, depth = 0.5, phase = 0.0, shape = 0.0;
    double attackMs = 10.0, releaseMs = 150.0;
    bool bipolar = true;
};

// "Am7" / "F#m7b5" / "Cmaj9" / "Gsus4" -> root pc + pitch-class mask. Tolerant:
// an unknown suffix lands on the major triad (never drops a declared chord).
inline bool parseChordSymbol (const juce::String& sym, int& rootPc, int& mask)
{
    static const int base[7] = { 9, 11, 0, 2, 4, 5, 7 };        // A B C D E F G
    const auto s = sym.trim();
    if (s.isEmpty()) return false;
    const auto c0 = (juce::juce_wchar) juce::CharacterFunctions::toUpperCase (s[0]);
    if (c0 < 'A' || c0 > 'G') return false;
    rootPc = base[c0 - 'A'];
    int i = 1;
    while (i < s.length() && (s[i] == '#' || s[i] == 'b'))
        { rootPc = (rootPc + (s[i] == '#' ? 1 : 11)) % 12; ++i; }
    const auto q = s.substring (i).trim().toLowerCase().removeCharacters (" ()");
    const int r = rootPc;
    auto pcs = [r] (std::initializer_list<int> iv)
    { int m = 0; for (int v : iv) m |= (1 << ((r + v) % 12)); return m; };
    if      (q.startsWith ("m7b5"))                          mask = pcs ({0, 3, 6, 10});
    else if (q.startsWith ("dim7"))                          mask = pcs ({0, 3, 6, 9});
    else if (q.startsWith ("dim"))                           mask = pcs ({0, 3, 6});
    else if (q.startsWith ("aug"))                           mask = pcs ({0, 4, 8});
    else if (q.startsWith ("sus2"))                          mask = pcs ({0, 2, 7});
    else if (q.startsWith ("sus"))                           mask = pcs ({0, 5, 7});
    else if (q.startsWith ("maj9"))                          mask = pcs ({0, 4, 7, 11, 2});
    else if (q.startsWith ("maj7"))                          mask = pcs ({0, 4, 7, 11});
    else if (q.startsWith ("madd9"))                         mask = pcs ({0, 3, 7, 2});
    else if (q.startsWith ("m9") || q.startsWith ("min9"))   mask = pcs ({0, 3, 7, 10, 2});
    else if (q.startsWith ("m7") || q.startsWith ("min7"))   mask = pcs ({0, 3, 7, 10});
    else if (q.startsWith ("m6") || q.startsWith ("min6"))   mask = pcs ({0, 3, 7, 9});
    else if (q.startsWith ("m") || q.startsWith ("min"))     mask = pcs ({0, 3, 7});
    else if (q.startsWith ("add9"))                          mask = pcs ({0, 4, 7, 2});
    else if (q.startsWith ("9"))                             mask = pcs ({0, 4, 7, 10, 2});
    else if (q.startsWith ("7"))                             mask = pcs ({0, 4, 7, 10});
    else if (q.startsWith ("6"))                             mask = pcs ({0, 4, 7, 9});
    else if (q.startsWith ("5"))                             mask = pcs ({0, 7});
    else                                                     mask = pcs ({0, 4, 7});
    return true;
}

struct Song
{
    int version = 1;
    double bpm = 120, lengthBars = 4, masterGainDb = 0;
    juce::String key, swingGrid { "16th" };
    double swingAmount = 0.5;
    std::vector<SongTempoPoint> tempoMap;   // extra tempo points after the base bpm (bar 0)
    std::vector<SongChord> chords;          // the harmonic spine (read-only here; extras serializes)
    std::vector<SongModulator> modulators;  // LFO/follower motion + keyed sidechain (#3)
    std::vector<SongMeterPoint> meterMap;   // THE WORLD GRID (#1): sorted at parse
    std::vector<SongSection> sections;
    std::vector<SongMidiMap> midiMap;   // hardware bindings (learned in-app or agent-written)
    std::vector<SongFx> master;
    std::vector<SongBus> buses;
    std::vector<SongAuto> automation;   // song-level: masterGainDb | master[i].<param>
    juce::var provenance;               // V37b: accept-path history — OPAQUE, round-trips verbatim
    juce::var loopMeta;                 // _loop {genre,seed}: infill provenance — opaque too
    juce::var extras;                   // THE UNDROPPABLE LAW (2026-07-10): every top-level
                                        // field this build doesn't model (chords[], lyrics,
                                        // future python annotations) — round-trips verbatim
    juce::StringArray sceneNames;       // performance view scenes (launcher columns)
    std::vector<SongTrack> tracks;
    // quarter-note beats in the bar CONTAINING `bar` (4.0 forever when no map)
    double beatsInBar (double bar) const
    {
        double per = 4.0;
        for (auto& mp : meterMap)
            if (mp.bar <= bar + 1e-9)
                per = mp.num * (4.0 / mp.den);
            else
                break;                       // meterMap is sorted at parse
        return per;
    }

    // quarter-beat position where bar N starts, under the meter map
    double barStartBeat (double bar) const
    {
        if (meterMap.empty())
            return bar * 4.0;
        double beat = 0.0, prevBar = 0.0, per = 4.0;
        for (auto& mp : meterMap)
        {
            if (mp.bar >= bar) break;
            if (mp.bar > prevBar)
            {
                beat += (mp.bar - prevBar) * per;
                prevBar = mp.bar;
            }
            per = mp.num * (4.0 / mp.den);
        }
        return beat + (bar - prevBar) * per;
    }

    double totalBeats() const
    {
        return meterMap.empty() ? lengthBars * 4.0 : barStartBeat (lengthBars);
    }
};

inline std::map<juce::String, float> parseParams (const juce::var& v)
{
    std::map<juce::String, float> out;
    if (auto* obj = v.getDynamicObject())
        for (auto& p : obj->getProperties())
            out[p.name.toString()] = (float) (double) p.value;
    return out;
}

// points accepted as [{"beat":b,"v":x}] or [[b,x]] shorthand
inline void parseAutomation (const juce::var& av, std::vector<SongAuto>& out)
{
    auto* arr = av.getArray();
    if (arr == nullptr) return;
    for (auto& a : *arr)
    {
        SongAuto sa;
        sa.target = a.getProperty ("target", "").toString();
        if (auto* pts = a.getProperty ("points", juce::var()).getArray())
            for (auto& p : *pts)
            {
                if (auto* pa = p.getArray())
                {
                    if (pa->size() >= 2)
                        sa.points.push_back ({ (double) (*pa)[0], (double) (*pa)[1],
                                               pa->size() > 2 ? (double) (*pa)[2] : 0.0 });
                }
                else
                    sa.points.push_back ({ (double) p.getProperty ("beat", 0.0),
                                           (double) p.getProperty ("v", 0.0),
                                           (double) p.getProperty ("curve", 0.0) });
            }
        std::sort (sa.points.begin(), sa.points.end(),
                   [] (auto& x, auto& y) { return x.beat < y.beat; });
        if (sa.target.isNotEmpty() && ! sa.points.empty())
            out.push_back (std::move (sa));
    }
}

inline void parseFxList (const juce::var& fv, std::vector<SongFx>& out)
{
    if (auto* fxs = fv.getArray())
        for (auto& f : *fxs)
        {
            SongFx fx;
            fx.type = f.getProperty ("type", "faustfx").toString();
            fx.id = f.getProperty ("id", fx.type).toString();
            fx.preset = f.getProperty ("preset", "").toString();
            fx.bypass = (bool) f.getProperty ("bypass", false);
            fx.params = parseParams (f.getProperty ("params", juce::var()));
            if (fx.type == "faustfx" && fx.id == "faustfx") continue;   // faust needs a dsp id
            out.push_back (std::move (fx));
        }
}

inline bool parseSong (const juce::File& f, Song& s)
{
    auto v = juce::JSON::parse (f.loadFileAsString());
    if (v.isVoid()) return false;

    s.version = (int) v.getProperty ("version", 0);
    s.bpm = (double) v.getProperty ("bpm", 120.0);
    s.key = v.getProperty ("key", "").toString();
    s.lengthBars = (double) v.getProperty ("lengthBars", 4.0);
    s.masterGainDb = (double) v.getProperty ("masterGainDb", 0.0);

    auto sw = v.getProperty ("swing", juce::var());
    s.swingGrid = sw.getProperty ("grid", "16th").toString();
    s.swingAmount = (double) sw.getProperty ("amount", 0.5);

    s.tempoMap.clear();
    if (auto* tm = v.getProperty ("tempoMap", juce::var()).getArray())
        for (auto& tv : *tm)
            s.tempoMap.push_back ({ (double) tv.getProperty ("bar", 0.0),
                                    (double) tv.getProperty ("bpm", s.bpm),
                                    (double) tv.getProperty ("curve", 1.0) });

    s.sections.clear();
    if (auto* secs = v.getProperty ("sections", juce::var()).getArray())
        for (auto& sv : *secs)
            s.sections.push_back ({ sv.getProperty ("name", "").toString(),
                                    (double) sv.getProperty ("startBar", 0.0) });

    s.chords.clear();                       // THE CHORD TRACK: declared harmony, parsed
    if (auto* chs = v.getProperty ("chords", juce::var()).getArray())
        for (auto& cv : *chs)
        {
            SongChord c;
            c.bar = (double) cv.getProperty ("bar", 1.0);
            if (parseChordSymbol (cv.getProperty ("chord", "").toString(), c.rootPc, c.mask))
                s.chords.push_back (c);
        }

    s.meterMap.clear();                     // THE WORLD GRID (#1)
    if (auto* mm = v.getProperty ("meterMap", juce::var()).getArray())
    {
        for (auto& mv : *mm)
        {
            SongMeterPoint mp;
            mp.bar = (double) mv.getProperty ("bar", 0.0);
            mp.num = juce::jlimit (1, 32, (int) mv.getProperty ("num", 4));
            mp.den = (int) mv.getProperty ("den", 4);
            if (mp.den != 1 && mp.den != 2 && mp.den != 4 && mp.den != 8 && mp.den != 16)
                mp.den = 4;
            if (mp.bar >= 0)
                s.meterMap.push_back (mp);
        }
        std::sort (s.meterMap.begin(), s.meterMap.end(),
                   [] (const SongMeterPoint& a, const SongMeterPoint& b) { return a.bar < b.bar; });
    }

    s.modulators.clear();                   // THE MODULATION GRAPH (#3)
    if (auto* mods = v.getProperty ("modulators", juce::var()).getArray())
        for (auto& mv : *mods)
        {
            SongModulator m;
            m.kind      = mv.getProperty ("kind", "lfo").toString().toLowerCase();
            m.target    = mv.getProperty ("target", "").toString();
            m.source    = mv.getProperty ("source", "").toString();
            m.sync      = mv.getProperty ("sync", "").toString();
            m.rateHz    = (double) mv.getProperty ("rateHz", 1.0);
            m.depth     = (double) mv.getProperty ("depth", 0.5);
            m.phase     = (double) mv.getProperty ("phase", 0.0);
            m.shape     = (double) mv.getProperty ("shape", 0.0);
            m.attackMs  = (double) mv.getProperty ("attackMs", 10.0);
            m.releaseMs = (double) mv.getProperty ("releaseMs", 150.0);
            m.bipolar   = (bool) mv.getProperty ("bipolar", true);
            if (m.target.isNotEmpty())
                s.modulators.push_back (m);
        }

    s.provenance = v.getProperty ("provenance", juce::var());
    s.loopMeta   = v.getProperty ("_loop", juce::var());

    s.midiMap.clear();
    if (auto* mm = v.getProperty ("midiMap", juce::var()).getArray())
        for (auto& bv : *mm)
            s.midiMap.push_back ({ (int) bv.getProperty ("cc", -1),
                                   bv.getProperty ("track", "").toString(),
                                   bv.getProperty ("param", "").toString() });

    s.master.clear();
    if (auto* ms = v.getProperty ("master", juce::var()).getArray())
        for (auto& mv : *ms)
        {
            SongFx fx;
            const auto type = mv.getProperty ("type", "faustfx").toString();
            fx.type = (type == "eq" || type == "comp") ? type : juce::String ("faustfx");
            fx.id = mv.getProperty ("id", type == "limiter" ? "master_limiter" : type).toString();
            fx.preset = mv.getProperty ("preset", "").toString();
            fx.bypass = (bool) mv.getProperty ("bypass", false);
            fx.params = parseParams (mv.getProperty ("params", juce::var()));
            if (type == "limiter" && fx.params.find ("ceiling") == fx.params.end())
                fx.params["ceiling"] = -1.0f;
            if (fx.id.isNotEmpty() || fx.type != "faustfx")
                s.master.push_back (std::move (fx));
        }

    s.buses.clear();
    if (auto* bs = v.getProperty ("buses", juce::var()).getArray())
        for (auto& bv : *bs)
        {
            SongBus b;
            b.id = bv.getProperty ("id", "").toString();
            b.gainDb = (double) bv.getProperty ("gainDb", 0.0);
            parseFxList (bv.getProperty ("fx", juce::var()), b.fx);
            if (b.id.isNotEmpty())
                s.buses.push_back (std::move (b));
        }

    s.automation.clear();
    parseAutomation (v.getProperty ("automation", juce::var()), s.automation);

    s.tracks.clear();
    if (auto* arr = v.getProperty ("tracks", juce::var()).getArray())
    {
        for (auto& tv : *arr)
        {
            SongTrack t;
            auto sv = tv.getProperty ("source", juce::var());
            if (sv.isObject())
            {
                t.source.kind = sv.getProperty ("kind", "faust").toString();
                t.source.id = sv.getProperty ("id",
                                sv.getProperty ("kit",
                                  sv.getProperty ("plugin", juce::var()))).toString();
                t.source.preset = sv.getProperty ("preset", "").toString();
                t.source.params = parseParams (sv.getProperty ("params", juce::var()));
            }
            else // v0 compat
            {
                t.source.kind = "faust";
                t.source.id = tv.getProperty ("instrument", "kick_808").toString();
            }
            t.name = tv.getProperty ("name", t.source.id).toString();
            t.gainDb = (double) tv.getProperty ("gainDb", 0.0);
            t.pan = (double) tv.getProperty ("pan", 0.0);
            t.muted = (bool) tv.getProperty ("muted", false);
            t.locked = (bool) tv.getProperty ("locked", false);
            t.color = tv.getProperty ("color", "").toString();

            if (auto* clips = tv.getProperty ("audioClips", juce::var()).getArray())
                for (auto& cv : *clips)
                {
                    SongAudioClip ac;
                    ac.file = cv.getProperty ("file", "").toString();
                    ac.startBeat = (double) cv.getProperty ("startBeat", 0.0);
                    ac.lengthBeats = (double) cv.getProperty ("lengthBeats", 0.0);
                    ac.offsetSec = (double) cv.getProperty ("offsetSec", 0.0);
                    ac.gainDb = (double) cv.getProperty ("gainDb", 0.0);
                    ac.sourceBpm = (double) cv.getProperty ("sourceBpm", 0.0);
                    ac.stretch = cv.getProperty ("stretch", "").toString();
                    ac.fadeInBeats = (double) cv.getProperty ("fadeInBeats", 0.0);
                    ac.fadeOutBeats = (double) cv.getProperty ("fadeOutBeats", 0.0);
                    ac.fadeCurve = cv.getProperty ("fadeCurve", "").toString();
                    ac.tuning = cv.getProperty ("tuning", juce::var());
                    if (ac.file.isNotEmpty()) t.audioClips.push_back (std::move (ac));
                }

            parseFxList (tv.getProperty ("fx", juce::var()), t.fx);

            if (auto* sends = tv.getProperty ("sends", juce::var()).getArray())
                for (auto& sdv : *sends)
                {
                    SongSend sd { sdv.getProperty ("bus", "").toString(),
                                  (double) sdv.getProperty ("gainDb", -6.0) };
                    if (sd.bus.isNotEmpty()) t.sends.push_back (std::move (sd));
                }

            parseAutomation (tv.getProperty ("automation", juce::var()), t.automation);

            if (auto* notes = tv.getProperty ("notes", juce::var()).getArray())
                for (auto& nv : *notes)
                    t.notes.push_back ({ (double) nv.getProperty ("start", 0.0),
                                         (double) nv.getProperty ("len", 0.25),
                                         (int) nv.getProperty ("pitch", 60),
                                         (double) nv.getProperty ("vel", 0.8),
                                         (double) nv.getProperty ("chance", 1.0) });

            {
                auto gv = tv.getProperty ("groove", juce::var());
                if (gv.isObject())
                {
                    t.grooveName = gv.getProperty ("name", "").toString();
                    t.grooveAmount = (double) gv.getProperty ("amount", 1.0);
                }
            }
            if (auto* slots = tv.getProperty ("slots", juce::var()).getArray())
                for (auto& slv : *slots)
                {
                    SongSlot sl;
                    if (slv.isObject())
                    {
                        sl.present = true;
                        sl.name = slv.getProperty ("name", "").toString();
                        sl.lengthBeats = (double) slv.getProperty ("lengthBeats", 16.0);
                        sl.audioFile = slv.getProperty ("audioFile", "").toString();
                        sl.offsetSec = (double) slv.getProperty ("offsetSec", 0.0);
                        sl.sourceBpm = (double) slv.getProperty ("sourceBpm", 0.0);
                        sl.stretch = slv.getProperty ("stretch", "").toString();
                        sl.follow = slv.getProperty ("follow", "").toString();
                        sl.followChance = juce::jlimit (0.0, 1.0,
                            (double) slv.getProperty ("followChance", 1.0));
                        if (auto* sn = slv.getProperty ("notes", juce::var()).getArray())
                            for (auto& nv : *sn)
                                sl.notes.push_back ({ (double) nv.getProperty ("start", 0.0),
                                                      (double) nv.getProperty ("len", 0.25),
                                                      (int) nv.getProperty ("pitch", 60),
                                                      (double) nv.getProperty ("vel", 0.8) });
                    }
                    t.slots.push_back (std::move (sl));
                }
            s.tracks.push_back (std::move (t));
        }
    }
    s.sceneNames.clear();
    if (auto* scenes = v.getProperty ("scenes", juce::var()).getArray())
        for (auto& scv : *scenes)
            s.sceneNames.add (scv.isObject() ? scv.getProperty ("name", "").toString()
                                             : scv.toString());
    // THE UNDROPPABLE LAW: capture the top-level keys the reads above don't
    // model, so songToVar re-emits them verbatim — a UI save must never destroy
    // what another layer wrote (chords[] has 9 python writers, write_lyrics one).
    {
        static const char* modeled[] = { "version", "bpm", "key", "lengthBars",
            "masterGainDb", "swing", "tempoMap", "sections", "provenance", "_loop",
            "midiMap", "master", "buses", "automation", "tracks", "scenes" };
        auto* ex = new juce::DynamicObject();
        juce::var exv (ex);
        if (auto* obj = v.getDynamicObject())
            for (auto& p : obj->getProperties())
            {
                bool known = false;
                for (auto* m : modeled)
                    if (p.name.toString() == m) { known = true; break; }
                if (! known)
                    ex->setProperty (p.name, p.value);
            }
        s.extras = ex->getProperties().isEmpty() ? juce::var() : exv;
    }

    return ! s.tracks.empty();
}

// Swing: shift on-grid odd subdivisions late. 0.5 = straight, 0.56 ~= gentle, 0.62 ~= hard.
inline double applySwing (double startBeats, const Song& s)
{
    if (s.swingAmount <= 0.5) return startBeats;
    const double sub = s.swingGrid == "8th" ? 0.5 : 0.25;
    const auto idx = (long long) std::llround (startBeats / sub);
    if (std::abs (startBeats - idx * sub) > 1e-6) return startBeats;  // already off-grid (manual groove)
    if ((idx & 1) == 0) return startBeats;
    return startBeats + (s.swingAmount - 0.5) * 2.0 * sub;
}

inline juce::File sotadawRoot();   // defined below; the behaviour needs it first

// The engine's default EditLimits cap the MASTER chain at 4 plugins — the 5th+
// insert silently no-ops (metal-eval forensics: a 5-fx master lost its brickwall
// AND the level meter; peak hit 0dBFS "through" a wall that wasn't there).
// Both binaries must construct te::Engine with this behaviour.
struct SotadawEngineBehaviour : public te::EngineBehaviour
{
    te::EditLimits getEditLimits() override
    {
        te::EditLimits l;
        l.maxNumMasterPlugins = 16;   // fx chain + trims + wall + meter, with headroom
        return l;
    }

    // THE AUDIO SURVIVES THE STORM (LAG DOSSIER v2 wave 2): tracktion's graph pool
    // asks for realtime priority but unprivileged Linux DENIES SCHED_RR — the pool
    // ran normal-priority while the pipewire device thread ran RT. Priority
    // inversion: under box load the RT callback starves waiting on non-RT helpers
    // and playback shreds into stuttering snippets (Chezy live, 2026-07-10).
    // setNumThreads(count - 1): returning 1 = ZERO pool threads = the whole graph
    // processes inline on the RT device thread. The UI sets the env default to 1
    // at boot; heavy sessions can raise it (SOTADAW_AUDIO_THREADS=4); m1 never
    // sets it, so offline renders keep every core.
    int getNumberOfCPUsToUseForAudio() override
    {
        if (const char* n = std::getenv ("SOTADAW_AUDIO_THREADS"))
            return juce::jlimit (1, juce::jmax (1, juce::SystemStats::getNumCpus()),
                                 juce::String (n).getIntValue());
        return juce::jmax (1, juce::SystemStats::getNumCpus());
    }

    // I7 (docs/IMPROVEMENTS_2026_07_07.md): wave-input recordings used to land in
    // the CWD — Tracktion consults the behaviour FIRST, and our edits have no
    // project/editFileRetriever to override it, so the repo root collected 193
    // mic_Take_*.wav orphans. All raw takes now land in songs/.recordings
    // (gitignored); the UI's harvest copies keepers into songs/takes and removes
    // the raw original.
    juce::File getDefaultFolderForAudioRecordings (te::Edit&) override
    {
        auto d = sotadawRoot().getChildFile ("songs").getChildFile (".recordings");
        d.createDirectory();
        return d;
    }
};

inline void registerSotadawPlugins (te::Engine& engine)
{
    engine.getPluginManager().createBuiltInType<te::ToneGeneratorPlugin>();
    engine.getPluginManager().createBuiltInType<FaustInstrumentPlugin>();
    engine.getPluginManager().createBuiltInType<SpectralVoicePlugin>();
    engine.getPluginManager().createBuiltInType<FaustFxPlugin>();
    engine.getPluginManager().createBuiltInType<RetunePlugin>();
    engine.getPluginManager().createBuiltInType<EarsTapPlugin>();
    engine.getPluginManager().createBuiltInType<NamPlugin>();
    engine.getPluginManager().createBuiltInType<ClapPlugin>();
}

inline juce::File sotadawRoot()
{
    if (const char* r = std::getenv ("SOTADAW_ROOT"))    // packaged builds: workspace lives in
        return juce::File (juce::String (r));            // ~/.local/share/sotadaw (see AppRun)
    // The baked path is the BUILD machine's source dir — a container build bakes
    // /src, which exists nowhere else (the Inspiron ran with root=/src: no songs,
    // no agent, sidecar respawn loop). Trust it only if it's really a workspace;
    // otherwise self-locate by walking up from the executable
    // (<root>/app/build/<target>_artefacts/Release/<bin> → 4 parents up).
    static const juce::File resolved = []
    {
        const juce::File baked ((juce::String (SOTADAW_ROOT)));
        if (baked.getChildFile ("agent/sidecar.py").existsAsFile())
            return baked;
        auto d = juce::File::getSpecialLocation (juce::File::currentExecutableFile)
                     .getParentDirectory();
        for (int i = 0; i < 8 && ! d.isRoot(); ++i, d = d.getParentDirectory())
            if (d.getChildFile ("agent/sidecar.py").existsAsFile())
                return d;
        return baked;
    }();
    return resolved;
}

// PORT_SPEC.md: the ONE python resolver — repo venv first (POSIX and Windows
// layouts differ), then the platform's conventional interpreter name.
inline juce::String pythonExe()
{
   #if JUCE_WINDOWS
    auto venv = sotadawRoot().getChildFile (".venv/Scripts/python.exe");
    if (venv.existsAsFile()) return venv.getFullPathName();
    return "python";
   #else
    auto venv = sotadawRoot().getChildFile (".venv/bin/python");
    if (venv.existsAsFile()) return venv.getFullPathName();
    return "python3";
   #endif
}

inline juce::String loadKitInto (te::SamplerPlugin& sampler, const juce::String& kitName)
{
    auto kitDir = sotadawRoot().getChildFile ("kits").getChildFile (kitName);
    auto v = juce::JSON::parse (kitDir.getChildFile ("kit.json").loadFileAsString());
    auto* samples = v.getProperty ("samples", juce::var()).getArray();
    if (samples == nullptr) return "kit not found or empty: " + kitName;
    // identity kits (source_kit.py drum/phrase/pitched) carry a kit-level
    // openEnded flag: without it the sampler gates every sound at note-off,
    // amputating ring/reverb-tail the imported audio actually has.
    const bool kitOpenEnded = (bool) v.getProperty ("openEnded", false);

    int index = 0;
    for (auto& sv : *samples)
    {
        auto file = kitDir.getChildFile (sv.getProperty ("file", "").toString());
        if (! file.existsAsFile()) continue;
        auto err = sampler.addSound (file.getFullPathName(),
                                     file.getFileNameWithoutExtension(),
                                     0.0, 0.0,
                                     (float) (double) sv.getProperty ("gainDb", 0.0));
        if (err.isNotEmpty()) return err;
        sampler.setSoundParams (index,
                                (int) sv.getProperty ("keyNote", 60),
                                (int) sv.getProperty ("minNote", 0),
                                (int) sv.getProperty ("maxNote", 127));
        sampler.setSoundOpenEnded (index, kitOpenEnded);
        ++index;
    }
    return {};
}

// VST3 support: scan results persisted to app/plugins_cache.xml
inline juce::File pluginCacheFile() { return sotadawRoot().getChildFile ("app/plugins_cache.xml"); }

inline void loadKnownPlugins (te::Engine& engine)
{
    if (auto xml = juce::parseXML (pluginCacheFile()))
        engine.getPluginManager().knownPluginList.recreateFromXml (*xml);
}

// vst3 source/fx params: match PROCESSOR parameters (real display names) and
// convert through each param's own text conversion (natural -> normalized) with
// a toggle guard (enums reject numeric text -> 0 -> nonzero-raw sets direct).
// Never the 0..1 automatable layer: 'Amplifier Gain -5' -> clamp 0 = -inf dB
// was Odin's silencer.
inline void applyVst3Params (te::ExternalPlugin* ep, const std::map<juce::String, float>& params)
{
    auto* inst = ep != nullptr ? ep->getAudioPluginInstance() : nullptr;
    if (inst == nullptr) return;
    auto norm = [] (juce::String str)
    { return str.toLowerCase().retainCharacters ("abcdefghijklmnopqrstuvwxyz0123456789"); };
    for (auto& [pname, pval] : params)
        for (auto* pp : inst->getParameters())
            if (norm (pp->getName (64)) == norm (pname)
                || norm (pp->getName (64)).contains (norm (pname)))
            {
                float nv = pp->getValueForText (juce::String (pval, 6));
                if (nv == 0.0f && pval != 0.0f)
                    nv = juce::jlimit (0.0f, 1.0f, (float) pval);
                if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                    std::fprintf (stderr, "[fxdbg] param '%s' -> '%s' raw=%f norm=%f\n",
                                  pname.toRawUTF8(), pp->getName (64).toRawUTF8(),
                                  (double) pval, nv);
                pp->setValueNotifyingHost (nv);
                break;
            }
}

inline te::Plugin::Ptr makeFaustFxInner (te::Edit& edit, const SongFx& fx)
{
    // vst3 fx: {"id": "vst3:<plugin name>"} anywhere a faust fx goes (tracks,
    // buses, master) — the Dragonfly/Airwindows rail the recipes teach.
    if (fx.id.startsWith ("vst3:"))
    {
        const auto want = fx.id.substring (5).trim();
        auto& list = edit.engine.getPluginManager().knownPluginList;
        for (const auto& desc : list.getTypes())
            if (desc.name.containsIgnoreCase (want))
            {
                if (PluginGuard::isQuarantined (desc.name))   // V49: died last session — skip
                    return {};
                PluginGuard::begin (desc.name, "fx-instantiate");
                auto plugin = edit.getPluginCache().createNewPlugin (te::ExternalPlugin::xmlTypeName, desc);
                if (auto* ep = dynamic_cast<te::ExternalPlugin*> (plugin.get()))
                {
                    if (fx.preset.isNotEmpty())        // state blob (e.g. synthesized surgefx)
                    {
                        auto pf = juce::File::isAbsolutePath (fx.preset)
                                    ? juce::File (fx.preset)
                                    : juce::File (sotadawRoot()).getChildFile (fx.preset);
                        juce::MemoryBlock blob;
                        if (pf.existsAsFile() && pf.loadFileAsData (blob))
                            if (auto* inst = ep->getAudioPluginInstance())
                                inst->setStateInformation (blob.getData(), (int) blob.getSize());
                    }
                    applyVst3Params (ep, fx.params);
                }
                PluginGuard::end();
                return plugin;
            }
        return {};
    }
    // THE NAM RAIL (V51): {"id": "nam:<capture.nam>"} — a captured amp/pedal as
    // an insert (mono-sum DI convention; input_db/output_db params). Path is
    // absolute or repo-relative.
    if (fx.id.startsWith ("nam:"))
    {
        const auto want = fx.id.substring (4).trim();
        auto nf = juce::File::isAbsolutePath (want)
                    ? juce::File (want)
                    : juce::File (sotadawRoot()).getChildFile (want);
        auto plugin = edit.getPluginCache().createNewPlugin (NamPlugin::xmlTypeName, {});
        if (auto* np = dynamic_cast<NamPlugin*> (plugin.get()))
        {
            np->setFile (nf.getFullPathName());
            np->setParams (fx.params);
        }
        return plugin;
    }
    // CLAP HOSTING (V50): {"id": "clap:<plugin.clap>"} — host any .clap as an
    // insert (direct C-ABI host, not via JUCE/tracktion). params.index picks the
    // sub-plugin, params.mix = dry/wet. Path is absolute or repo-relative.
    if (fx.id.startsWith ("clap:"))
    {
        const auto want = fx.id.substring (5).trim();
        auto cf = juce::File::isAbsolutePath (want)
                    ? juce::File (want)
                    : juce::File (sotadawRoot()).getChildFile (want);
        auto plugin = edit.getPluginCache().createNewPlugin (ClapPlugin::xmlTypeName, {});
        if (auto* cp = dynamic_cast<ClapPlugin*> (plugin.get()))
        {
            cp->setFile (cf.getFullPathName());
            cp->setParams (fx.params);
        }
        return plugin;
    }
    // fx_retune: CONTEXT-TUNE LIVE (V45 P4). Grid/key context is injected by the
    // track builder after creation (it needs the whole Song); params land here.
    if (fx.id == "fx_retune")
    {
        auto plugin = edit.getPluginCache().createNewPlugin (RetunePlugin::xmlTypeName, {});
        if (auto* rt = dynamic_cast<RetunePlugin*> (plugin.get()))
            rt->setParams (fx.params);
        return plugin;
    }
    // Tracktion built-ins: eq (4-band shelves + 2 mids) and comp — friendly JSON keys
    if (fx.type == "eq")
    {
        auto plugin = edit.getPluginCache().createNewPlugin (te::EqualiserPlugin::xmlTypeName, {});
        if (auto* eq = dynamic_cast<te::EqualiserPlugin*> (plugin.get()))
            for (auto& [k, v] : fx.params)
            {
                if      (k == "loFreq")   eq->setLowFreq (v);
                else if (k == "loGain")   eq->setLowGain (v);
                else if (k == "hiFreq")   eq->setHighFreq (v);
                else if (k == "hiGain")   eq->setHighGain (v);
                else if (k == "midFreq")  eq->setMidFreq1 (v);
                else if (k == "midGain")  eq->setMidGain1 (v);
                else if (k == "midQ")     eq->setMidQ1 (v);
                else if (k == "midFreq2") eq->setMidFreq2 (v);
                else if (k == "midGain2") eq->setMidGain2 (v);
                else if (k == "midQ2")    eq->setMidQ2 (v);
            }
        return plugin;
    }
    if (fx.type == "comp")
    {
        auto plugin = edit.getPluginCache().createNewPlugin (te::CompressorPlugin::xmlTypeName, {});
        if (auto* cp = dynamic_cast<te::CompressorPlugin*> (plugin.get()))
            for (auto& [k, v] : fx.params)
            {
                auto set = [&] (const char* id, float val)
                { if (auto p = cp->getAutomatableParameterByID (id)) p->setParameter (val, juce::sendNotification); };
                // engine-native traps: "threshold" is a GAIN [0.01..1] and "ratio" is
                // 1/N [0..0.95] — convert friendly dB / N:1, else "ratio": 4 clamps to 1:1
                if      (k == "threshold") set ("threshold", juce::Decibels::decibelsToGain (v));
                else if (k == "ratio")     set ("ratio", v > 0.01f ? 1.0f / v : 1.0f);
                else if (k == "attack")    set ("attack", v);
                else if (k == "release")   set ("release", v);
                else if (k == "outputDb")  set ("output gain", v);
            }
        return plugin;
    }
    auto plugin = edit.getPluginCache().createNewPlugin (FaustFxPlugin::xmlTypeName, {});
    if (auto* fp = dynamic_cast<FaustFxPlugin*> (plugin.get()))
    {
        fp->dspName = fx.id;
        fp->prepareZones();   // zones + automatable params exist from now on
        for (auto& [k, v] : fx.params) fp->setZone (k, v);
    }
    return plugin;
}

inline te::Plugin::Ptr makeFaustFx (te::Edit& edit, const SongFx& fx)
{
    auto plugin = makeFaustFxInner (edit, fx);
    if (plugin != nullptr && fx.bypass)
        plugin->setEnabled (false);
    return plugin;
}

inline juce::String buildTrackSource (te::Engine& engine, te::Edit& edit, te::AudioTrack& track, const SongTrack& t)
{
    if (t.source.kind == "audio")
        return {};   // clips only — no instrument; volume/fx/sends still apply
    if (t.source.kind == "spectral")
    {
        // LIVE spectral lanes: the plugin reads the capture sidecar itself
        // (id = "<capture.json relpath>#<lane>"), synthesizing each lane
        // note's partial with its own bend/gain envelopes.
        auto plugin = edit.getPluginCache().createNewPlugin (SpectralVoicePlugin::xmlTypeName, {});
        if (auto* sv = dynamic_cast<SpectralVoicePlugin*> (plugin.get()))
            sv->captureRef = t.source.id;
        if (plugin != nullptr)
            track.pluginList.insertPlugin (plugin, 0, nullptr);
        return {};
    }
    if (t.source.kind == "faust")
    {
        auto plugin = edit.getPluginCache().createNewPlugin (FaustInstrumentPlugin::xmlTypeName, {});
        if (auto* fp = dynamic_cast<FaustInstrumentPlugin*> (plugin.get()))
        {
            fp->dspName = t.source.id;
            fp->prepareZones();
            for (auto& [k, v] : t.source.params) fp->setZone (k, v);
        }
        track.pluginList.insertPlugin (plugin, 0, nullptr);
        return {};
    }
    if (t.source.kind == "sample")
    {
        auto plugin = edit.getPluginCache().createNewPlugin (te::SamplerPlugin::xmlTypeName, {});
        auto* sp = dynamic_cast<te::SamplerPlugin*> (plugin.get());
        if (sp == nullptr) return "sampler unavailable";
        track.pluginList.insertPlugin (plugin, 0, nullptr);
        return loadKitInto (*sp, t.source.id);
    }
    if (t.source.kind == "vst3")
    {
        auto& list = engine.getPluginManager().knownPluginList;
        for (const auto& desc : list.getTypes())
        {
            if (desc.name.containsIgnoreCase (t.source.id))
            {
                if (PluginGuard::isQuarantined (desc.name))   // V49: died last session — skip loudly
                    return "QUARANTINED after last-session crash: " + desc.name
                         + " (retry: delete " + PluginGuard::quarantineFile().getFullPathName() + ")";
                PluginGuard::begin (desc.name, "source-instantiate");
                auto plugin = edit.getPluginCache().createNewPlugin (te::ExternalPlugin::xmlTypeName, desc);
                if (plugin == nullptr) { PluginGuard::end(); return "could not instantiate " + desc.name; }
                track.pluginList.insertPlugin (plugin, 0, nullptr);
                if (auto* ep = dynamic_cast<te::ExternalPlugin*> (plugin.get()))
                {
                    if (t.source.preset.isNotEmpty())   // captured state blob = OUR patch format
                    {
                        auto pf = juce::File::isAbsolutePath (t.source.preset)
                                    ? juce::File (t.source.preset)
                                    : sotadawRoot().getChildFile (t.source.preset);
                        juce::MemoryBlock blob;
                        if (pf.existsAsFile() && pf.loadFileAsData (blob))
                            if (auto* inst = ep->getAudioPluginInstance())
                                inst->setStateInformation (blob.getData(), (int) blob.getSize());
                    }
                    applyVst3Params (ep, t.source.params);
                }
                PluginGuard::end();
                return {};
            }
        }
        return "vst3 not found in scan cache: " + t.source.id + " (run: m1 scan-plugins)";
    }
    return "unknown source kind: " + t.source.kind;
}

// Resolve an automation target string to a parameter (+ dB->fader-position transform flag).
inline te::AutomatableParameter* resolveAutoTarget (const juce::String& target,
                                                    te::VolumeAndPanPlugin* vol,
                                                    te::Plugin* source,
                                                    const std::vector<te::Plugin*>& fxPlugs,
                                                    bool& isVolumeDb, juce::String& err)
{
    isVolumeDb = false;
    if (target == "gainDb")
    {
        isVolumeDb = true;
        return vol != nullptr ? vol->volParam.get() : nullptr;
    }
    if (target == "pan")
        return vol != nullptr ? vol->panParam.get() : nullptr;

    auto paramOn = [&err] (te::Plugin* p, const juce::String& id) -> te::AutomatableParameter*
    {
        if (p == nullptr) { err = "no plugin for target"; return nullptr; }
        if (auto byId = p->getAutomatableParameterByID (id))
            return byId.get();
        for (auto ap : p->getAutomatableParameters())         // vst3: fuzzy name match
            if (ap->getParameterName().containsIgnoreCase (id))
                return ap;
        err = "param not found: " + id + " on " + p->getName();
        return nullptr;
    };

    if (target.startsWith ("fx[") && target.contains ("]."))
    {
        const int idx = target.fromFirstOccurrenceOf ("fx[", false, false).getIntValue();
        const auto id = target.fromFirstOccurrenceOf ("].", false, false);
        if (idx < 0 || idx >= (int) fxPlugs.size()) { err = "fx index out of range: " + target; return nullptr; }
        return paramOn (fxPlugs[(size_t) idx], id);
    }
    if (target.startsWith ("source."))
        return paramOn (source, target.fromFirstOccurrenceOf ("source.", false, false));

    err = "unknown automation target: " + target;
    return nullptr;
}

inline void addAutomationCurve (te::Edit& edit, te::AutomatableParameter* param,
                                const SongAuto& a, bool isVolumeDb)
{
    auto& curve = param->getCurve();
    for (auto& pt : a.points)
    {
        const auto tpos = edit.tempoSequence.toTime (te::BeatPosition::fromBeats (pt.beat));
        const float val = isVolumeDb ? te::decibelsToVolumeFaderPosition ((float) pt.v)
                                     : (float) pt.v;
        curve.addPoint (tpos, val, (float) pt.curve, nullptr);
    }
}

// ---- CONTEXT-TUNE LIVE grid: the other tracks' notes -> per-half-beat pc masks ----
inline bool retuneKeyPcs (const juce::String& key, int& root, bool& minor)
{
    static const int base[7] = { 9, 11, 0, 2, 4, 5, 7 };        // A B C D E F G
    const auto k = key.trim();
    if (k.isEmpty()) return false;
    const auto c0 = (juce::juce_wchar) juce::CharacterFunctions::toUpperCase (k[0]);
    if (c0 < 'A' || c0 > 'G') return false;
    root = base[c0 - 'A'];
    int i = 1;
    if (i < k.length() && (k[i] == '#' || k[i] == 'b')) { root = (root + (k[i] == '#' ? 1 : 11)) % 12; ++i; }
    minor = k.substring (i).trim().toLowerCase().startsWith ("min")
            || k.substring (i).trim().toLowerCase() == "m";
    return true;
}

inline juce::String computeRetuneGrid (const Song& s, const juce::String& hostTrack)
{
    const int cells = (int) std::ceil (s.totalBeats() / 0.5) + 8;
    std::vector<std::array<double, 12>> w ((size_t) cells);
    for (auto& c : w) c.fill (0.0);
    for (auto& tr : s.tracks)
    {
        if (tr.name == hostTrack) continue;
        const auto id = (tr.source.id + " " + tr.name).toLowerCase();
        if (id.contains ("kick") || id.contains ("snare") || id.contains ("clap")
            || id.contains ("hat") || id.contains ("perc") || id.contains ("ride")
            || id.contains ("crash") || id.contains ("shak") || id.contains ("cym")
            || id.contains ("tom")) continue;
        for (auto& nt : tr.notes)
        {
            const double wt = (nt.pitch < 48 ? 2.0 : 1.0) * juce::jmax (0.1, nt.vel);
            const int i0 = juce::jmax (0, (int) (nt.start / 0.5));
            const int i1 = juce::jmin (cells, (int) std::ceil ((nt.start + nt.len) / 0.5));
            for (int i = i0; i < i1; ++i)
            {
                const double ov = juce::jmin (nt.start + nt.len, (i + 1) * 0.5)
                                  - juce::jmax (nt.start, i * 0.5);
                if (ov > 0) w[(size_t) i][(size_t) (((nt.pitch % 12) + 12) % 12)] += ov * wt;
            }
        }
    }
    // THE SPINE OUTRANKS INFERENCE (BEST_DAW_30 #2): declared chords[] own
    // their spans cell-for-cell; note inference covers only undeclared spans
    // and remains the whole story when no chord track exists (never removed).
    std::vector<int> declared ((size_t) cells, 0);
    if (! s.chords.empty())
    {
        auto sorted = s.chords;
        std::sort (sorted.begin(), sorted.end(),
                   [] (const SongChord& a, const SongChord& b) { return a.bar < b.bar; });
        for (size_t ci = 0; ci < sorted.size(); ++ci)
        {
            const double b0 = (sorted[ci].bar - 1.0) * 4.0;      // the wire is 1-based bars
            const double b1 = ci + 1 < sorted.size() ? (sorted[ci + 1].bar - 1.0) * 4.0
                                                     : (double) cells * 0.5;
            const int i0 = juce::jlimit (0, cells, (int) (b0 / 0.5));
            const int i1 = juce::jlimit (0, cells, (int) std::ceil (b1 / 0.5));
            for (int i = i0; i < i1; ++i)
                declared[(size_t) i] = sorted[ci].mask;
        }
    }
    juce::StringArray out;
    for (int ci = 0; ci < cells; ++ci)
    {
        auto& c = w[(size_t) ci];
        int mask = declared[(size_t) ci];
        if (mask == 0)
        {
            double mx = 0; for (double v : c) mx = juce::jmax (mx, v);
            if (mx > 0)
                for (int pc = 0; pc < 12; ++pc)
                    if (c[(size_t) pc] >= 0.25 * mx) mask |= (1 << pc);
        }
        out.add (juce::String (mask));
    }
    if (std::getenv ("SOTADAW_RETUNE_GRID_DEBUG") != nullptr)
        std::fprintf (stderr, "[retunegrid] %s cells=%d declared=%d first8=%s\n",
                      hostTrack.toRawUTF8(), cells,
                      (int) std::count_if (declared.begin(), declared.end(),
                                           [] (int m) { return m != 0; }),
                      out.joinIntoString (",").substring (0, 40).toRawUTF8());
    return out.joinIntoString (",");
}

inline std::unique_ptr<te::Edit> buildEdit (te::Engine& engine, const Song& s,
                                            te::Edit::EditRole role, juce::String* errorOut = nullptr)
{
    using namespace tracktion::literals;
    // SOTADAW_PERF=1: phase-timed build — one printed line telling the EDIT-DELTA
    // campaign WHERE the rebuild milliseconds live. Accumulation is a handful of
    // clock reads (ns); behavior is untouched.
    const auto pfT0 = juce::Time::getHighResolutionTicks();
    auto pfMs = [] (juce::int64 t0) { return 1000.0 * (double) (juce::Time::getHighResolutionTicks() - t0)
                                             / (double) juce::Time::getHighResolutionTicksPerSecond(); };
    double pfSetup = 0, pfSource = 0, pfFx = 0, pfAutom = 0, pfMidi = 0, pfClips = 0, pfSlots = 0, pfBuses = 0;
    auto edit = te::Edit::createSingleTrackEdit (engine, role);
    edit->ensureNumberOfAudioTracks ((int) (s.tracks.size() + s.buses.size()));
    juce::String errors;                   // collected build warnings (meter/mod/fx)
    edit->tempoSequence.getTempo (0)->setBpm (s.bpm);
    for (auto& tp : s.tempoMap)            // TEMPO IS A CURVE: ramps/switches; everything
        if (tp.bar > 0 && tp.bpm >= 20 && tp.bpm <= 400)   // downstream places in beats, so
            edit->tempoSequence.insertTempo (               // notes/clips/automation follow;
                te::BeatPosition::fromBeats (s.barStartBeat (tp.bar)), // #1: bar->beat rides the
                tp.bpm, (float) juce::jlimit (-1.0, 1.0, tp.curve));   // meter map (4/4 = old math)
    // THE WORLD GRID (#1): meterMap -> engine time signatures. Bars stop lying:
    // the click, MIDI/DAWproject exports and every bar boundary the engine
    // reports now speak the real meter. Notes stay quarter-beat absolute.
    for (auto& mp : s.meterMap)
    {
        // v1 boundary (measured 2026-07-12): engine BeatPositions are
        // DENOMINATOR-beats — a 7/8 timesig re-denominates every note/clip/
        // automation position this build feeds in quarter-beats (an 18-beat
        // song rendered 4.5s: 0.25s eighth-beats). den==4 meters (3/4, 5/4,
        // 7/4...) are exact with zero conversion; den 8/16 keep OUR bar math
        // (ruler/roll truth) and enter the engine with the quarter<->engine
        // conversion boundary leg. Loud, never silent.
        if (mp.den != 4)
        {
            errors << "meterMap: " << mp.num << "/" << mp.den
                   << " shapes bars in-app; engine time-signature lands with "
                      "the conversion-boundary leg (den==4 meters are live)\n";
            continue;
        }
        te::TimeSigSetting::Ptr tsg;
        if (mp.bar <= 0)
            tsg = edit->tempoSequence.getTimeSig (0);
        else
            tsg = edit->tempoSequence.insertTimeSig (
                      te::BeatPosition::fromBeats (s.barStartBeat (mp.bar)));
        if (tsg != nullptr)
        {
            tsg->numerator = mp.num;
            tsg->denominator = mp.den;
        }
    }
    if (! s.meterMap.empty() && std::getenv ("SOTADAW_GRID_DEBUG") != nullptr)
        for (auto ts : edit->tempoSequence.getTimeSigs())
            std::fprintf (stderr, "[worldgrid] timesig %d/%d at beat %.2f\n",
                          (int) ts->numerator, (int) ts->denominator,
                          ts->startBeatNumber.get().inBeats());
    edit->getMasterVolumePlugin()->setVolumeDb ((float) s.masterGainDb);

    // master chain in array order. APPEND (-1) each one: explicit indices past the list's
    // initial size silently drop the plugin from the graph (the 4th fx never processed —
    // found the hard way when a brickwall limiter didn't limit).
    // SECOND EDITION of that bug (metal eval forensics): with a built-in (eq/comp) mid-chain
    // in a 5-fx master, the LAST insert can still silently vanish from the graph. VERIFY
    // every plugin landed and re-insert stragglers — never trust a silent insert.
    std::vector<te::Plugin*> masterFxPlugs;
    {
        std::vector<te::Plugin::Ptr> created;   // create ALL first: a built-in insert can
        for (auto& mfx : s.master)              // poison later createNewPlugin calls
        {
            auto plugin = makeFaustFx (*edit, mfx);
            if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                std::fprintf (stderr, "[fxdbg] create %s(%s) -> %s\n", mfx.id.toRawUTF8(),
                              mfx.type.toRawUTF8(), plugin == nullptr ? "NULL" : "ok");
            created.push_back (plugin);
        }
        for (auto& plugin : created)
        {
            if (plugin == nullptr) continue;
            masterFxPlugs.push_back (plugin.get());
            edit->getMasterPluginList().insertPlugin (plugin, -1, nullptr);
            if (! edit->getMasterPluginList().getPlugins().contains (plugin.get())
                && std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                std::fprintf (stderr, "[fxdbg] INSERT FAILED for %s\n", plugin->getName().toRawUTF8());
        }
    }
    // master level meter LAST so the UI reads post-chain levels
    {
        auto meter = edit->getPluginCache().createNewPlugin (te::LevelMeterPlugin::xmlTypeName, {});
        if (meter != nullptr)
            edit->getMasterPluginList().insertPlugin (meter, -1, nullptr);
    }
    // THE EARS BUS (E3 R1): the master tap rides after the meter — every play or
    // render streams 10 Hz feature frames to agent/ipc/ears.jsonl (EarsTapPlugin.h)
    {
        auto ears = edit->getPluginCache().createNewPlugin (EarsTapPlugin::xmlTypeName, {});
        if (ears != nullptr)
            edit->getMasterPluginList().insertPlugin (ears, -1, nullptr);
    }
    if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
    {
        auto plugs = edit->getMasterPluginList().getPlugins();
        std::fprintf (stderr, "[fxdbg] master list size=%d:", (int) plugs.size());
        for (auto* p : plugs)
            std::fprintf (stderr, " %s", p->getName().toRawUTF8());
        std::fprintf (stderr, "\n");
    }

    auto audioTracks = te::getAudioTracks (*edit);

    // performance view: scenes + clip slots (launcher columns), quantised to the bar
    {
        int numScenes = s.sceneNames.size();
        for (auto& t : s.tracks)
            numScenes = juce::jmax (numScenes, (int) t.slots.size());
        if (numScenes > 0)
        {
            edit->getLaunchQuantisation().type = te::LaunchQType::bar;
            auto& sceneList = edit->getSceneList();
            sceneList.ensureNumberOfScenes (numScenes);
            auto scenes = sceneList.getScenes();
            for (int sc = 0; sc < scenes.size() && sc < s.sceneNames.size(); ++sc)
                scenes[sc]->name = s.sceneNames[sc];
        }
    }
    const auto songEnd = edit->tempoSequence.toTime (te::BeatPosition::fromBeats (s.totalBeats() + 4.0));

    // bus numbers are 1-based; assigned before tracks so sends can reference them
    std::map<juce::String, int> busNum;
    for (size_t b = 0; b < s.buses.size(); ++b)
        busNum[s.buses[b].id] = (int) b + 1;

    // #3 modulator resolution context, collected while tracks build
    struct ModCtx { te::AudioTrack* track = nullptr; te::VolumeAndPanPlugin* vol = nullptr;
                    te::Plugin* source = nullptr; std::vector<te::Plugin*> fxPlugs; };
    std::map<juce::String, ModCtx> modCtx;

    pfSetup = pfMs (pfT0);
    int i = 0;
    for (auto& t : s.tracks)
    {
        auto track = audioTracks[i++];
        track->setName (t.name);

        const auto pfS = juce::Time::getHighResolutionTicks();
        auto err = buildTrackSource (engine, *edit, *track, t);
        pfSource += pfMs (pfS);
        if (err.isNotEmpty()) errors << t.name << ": " << err << "\n";
        te::Plugin* sourcePlug = [&]() -> te::Plugin*
        {
            auto plugs = track->pluginList.getPlugins();
            return plugs.isEmpty() ? nullptr : plugs.getFirst().get();
        }();

        const auto pfF = juce::Time::getHighResolutionTicks();
        int fxIndex = 1;
        std::vector<te::Plugin*> fxPlugs;
        for (auto& fx : t.fx)
        {
            auto plugin = makeFaustFx (*edit, fx);
            if (auto* rt = dynamic_cast<RetunePlugin*> (plugin.get()))
            {
                int root = -1; bool minor = false;
                retuneKeyPcs (s.key, root, minor);
                rt->setContext (computeRetuneGrid (s, t.name), root, minor);
            }
            fxPlugs.push_back (plugin.get());
            track->pluginList.insertPlugin (plugin, fxIndex++, nullptr);
        }
        pfFx += pfMs (pfF);

        for (auto& sd : t.sends)
        {
            const auto it = busNum.find (sd.bus);
            if (it == busNum.end()) { errors << t.name << ": unknown send bus '" << sd.bus << "'\n"; continue; }
            auto send = edit->getPluginCache().createNewPlugin (te::AuxSendPlugin::xmlTypeName, {});
            if (auto* sp = dynamic_cast<te::AuxSendPlugin*> (send.get()))
            {
                sp->busNumber = it->second;
                sp->setGainDb ((float) sd.gainDb);
            }
            track->pluginList.insertPlugin (send, fxIndex++, nullptr);
        }

        auto* vol = track->getVolumePlugin();
        if (vol != nullptr)
        {
            vol->setVolumeDb ((float) t.gainDb);
            vol->setPan ((float) t.pan);
        }

        const auto pfA = juce::Time::getHighResolutionTicks();
        for (auto& a : t.automation)
        {
            bool isVolDb = false;
            juce::String aerr;
            if (auto* param = resolveAutoTarget (a.target, vol, sourcePlug, fxPlugs, isVolDb, aerr))
                addAutomationCurve (*edit, param, a, isVolDb);
            else
                errors << t.name << ": automation: " << aerr << "\n";
        }
        pfAutom += pfMs (pfA);

        if (! s.modulators.empty())          // #3: keep the resolution context
            modCtx[t.name] = { track, vol, sourcePlug, fxPlugs };

        const auto pfM = juce::Time::getHighResolutionTicks();
        if (! t.notes.empty())
            if (auto clip = track->insertMIDIClip ({ 0_tp, songEnd }, nullptr))
            {
                int ni = 0;
                for (auto& n : t.notes)
                    if (noteIncluded (n, ni++))          // HB5: per-note chance (seeded)
                        clip->getSequence().addNote (n.pitch,
                                                     te::BeatPosition::fromBeats (applySwing (n.start, s)),
                                                     te::BeatDuration::fromBeats (n.len),
                                                     juce::jlimit (1, 127, (int) std::lround (n.vel * 127.0)),
                                                     0, nullptr);
            }
        pfMidi += pfMs (pfM);

        const auto pfC = juce::Time::getHighResolutionTicks();
        for (auto& ac : t.audioClips)
        {
            auto f = juce::File::isAbsolutePath (ac.file) ? juce::File (ac.file)
                                                          : sotadawRoot().getChildFile (ac.file);
            if (! f.existsAsFile()) { errors << t.name << ": missing audio file " << ac.file << "\n"; continue; }
            const auto tStart = edit->tempoSequence.toTime (te::BeatPosition::fromBeats (ac.startBeat));
            double lenS = 0;
            if (ac.lengthBeats > 0)
                lenS = (edit->tempoSequence.toTime (te::BeatPosition::fromBeats (ac.startBeat + ac.lengthBeats))
                        - tStart).inSeconds();
            else
                lenS = te::AudioFile (engine, f).getLength() - ac.offsetSec;   // rest of file
            auto clip = track->insertWaveClip (f.getFileNameWithoutExtension(), f,
                            { { tStart, tStart + te::TimeDuration::fromSeconds (juce::jmax (0.1, lenS)) },
                              te::TimeDuration::fromSeconds (ac.offsetSec) }, false);
            if (clip != nullptr)
            {
                // THE RANGE IS LAW (V46 forensics): loop wavs (incl. our own loop_gen
                // renders) carry embedded beat/loop metadata, and the engine re-syncs a
                // fresh wave clip to the FILE's claimed length — a 16-beat placement of
                // a 20-beat-tagged file silently became 20 beats (and anchored fades
                // wrong). Kill the source's tempo opinions and re-pin the spec range;
                // the warp path below re-enables autoTempo with OUR numBeats.
                clip->setAutoTempo (false);
                clip->setAutoPitch (false);
                clip->setPosition ({ { tStart, tStart + te::TimeDuration::fromSeconds (juce::jmax (0.1, lenS)) },
                                     te::TimeDuration::fromSeconds (ac.offsetSec) });
                clip->setGainDB ((float) ac.gainDb);
                if (ac.fadeInBeats > 0 || ac.fadeOutBeats > 0)   // V46: clip dignity — edge fades
                {
                    const auto curve = ac.fadeCurve == "convex"  ? te::AudioFadeCurve::convex
                                     : ac.fadeCurve == "concave" ? te::AudioFadeCurve::concave
                                     : ac.fadeCurve == "s"       ? te::AudioFadeCurve::sCurve
                                                                 : te::AudioFadeCurve::linear;
                    const auto clipEnd = tStart + te::TimeDuration::fromSeconds (juce::jmax (0.1, lenS));
                    if (ac.fadeInBeats > 0)
                    {
                        clip->setFadeIn (edit->tempoSequence.toTime (edit->tempoSequence.toBeats (tStart)
                                             + te::BeatDuration::fromBeats (ac.fadeInBeats)) - tStart);
                        clip->setFadeInType (curve);
                    }
                    if (ac.fadeOutBeats > 0)
                    {
                        clip->setFadeOut (clipEnd - edit->tempoSequence.toTime (edit->tempoSequence.toBeats (clipEnd)
                                              - te::BeatDuration::fromBeats (ac.fadeOutBeats)));
                        clip->setFadeOutType (curve);
                    }
                }
                if (ac.sourceBpm > 0)   // WARP: the clip follows the song tempo (Ableton-style)
                {
                    const double fileLen = te::AudioFile (engine, f).getLength();
                   #if TRACKTION_ENABLE_TIMESTRETCH_SIGNALSMITH   // V46 warp v2: hq default, "fast" = legacy
                    clip->setTimeStretchMode (ac.stretch == "fast" ? te::TimeStretcher::soundtouchBetter
                                                                   : te::TimeStretcher::signalsmith);
                   #else
                    clip->setTimeStretchMode (te::TimeStretcher::soundtouchBetter);
                   #endif
                    clip->getLoopInfo().setNumBeats (fileLen * ac.sourceBpm / 60.0);
                    clip->setAutoTempo (true);
                }
                if (std::getenv ("SOTADAW_CLIP_DEBUG") != nullptr)
                    std::fprintf (stderr, "[clipdbg] %s file=%s pos=[%.3f,%.3f] fadeIn=%.3fs fadeOut=%.3fs\n",
                                  t.name.toRawUTF8(), ac.file.toRawUTF8(),
                                  clip->getPosition().getStart().inSeconds(),
                                  clip->getPosition().getEnd().inSeconds(),
                                  clip->getFadeIn().inSeconds(), clip->getFadeOut().inSeconds());
                // headless renders read the source directly (proxies never materialize there);
                // LIVE playback keeps proxies ON — direct file reads on the audio path stutter
                if (role == te::Edit::EditRole::forRendering)
                    clip->setUsesProxy (false);
            }
        }

        pfClips += pfMs (pfC);

        // launcher slots: loopable MIDI patterns living in this track's clip-slot column
        const auto pfSl = juce::Time::getHighResolutionTicks();
        {
            // scene-story grammar: slot.follow -> the engine's NATIVE follow actions
            auto applyFollow = [] (te::Clip& c, const juce::String& follow, double chance)
            {
                const auto fa = follow == "next" ? te::FollowAction::trackNext
                              : follow == "any"  ? te::FollowAction::trackAny
                              : follow == "stop" ? te::FollowAction::globalStop
                                                 : te::FollowAction::none;
                if (fa == te::FollowAction::none) return;
                c.followActionDurationType = te::Clip::FollowActionDurationType::loops;
                c.followActionNumLoops = 1.0;
                if (auto* acts = c.getFollowActions())
                {
                    for (auto* stale : acts->getActions())   // the container seeds a
                        acts->removeAction (*stale);         // default action — ours only
                    auto& a = acts->addAction();
                    a.action = fa;
                    a.weight = juce::jlimit (0.0, 1.0, chance);
                    if (chance < 1.0)              // the WF13 die: else play again
                    {
                        auto& again = acts->addAction();
                        again.action = te::FollowAction::globalPlayAgain;
                        again.weight = 1.0 - chance;
                    }
                }
            };
            auto clipSlots = track->getClipSlotList().getClipSlots();
            for (int sc = 0; sc < (int) t.slots.size() && sc < clipSlots.size(); ++sc)
            {
                auto& sl = t.slots[(size_t) sc];
                if (! sl.present) continue;
                const auto endT = edit->tempoSequence.toTime (te::BeatPosition::fromBeats (sl.lengthBeats));
                if (sl.audioFile.isNotEmpty())      // audio loop slot (stems->slots)
                {
                    auto af = juce::File::isAbsolutePath (sl.audioFile)
                                ? juce::File (sl.audioFile)
                                : sotadawRoot().getChildFile (sl.audioFile);
                    if (af.existsAsFile())
                        if (auto wc = te::insertWaveClip (*clipSlots[sc],
                                          sl.name.isNotEmpty() ? sl.name : t.name, af,
                                          { { 0_tp, endT },
                                            te::TimeDuration::fromSeconds (sl.offsetSec) },
                                          te::DeleteExistingClips::no))
                        {
                            // THE RANGE IS LAW: see the timeline clip note — the file's
                            // embedded beat metadata must not resize launcher cells either
                            wc->setAutoTempo (false);
                            wc->setAutoPitch (false);
                            wc->setPosition ({ { 0_tp, endT },
                                               te::TimeDuration::fromSeconds (sl.offsetSec) });
                            applyFollow (*wc, sl.follow, sl.followChance);
                            if (sl.sourceBpm > 0)   // warped loop: follows the song tempo
                            {
                                const double fileLen = te::AudioFile (engine, af).getLength();
                               #if TRACKTION_ENABLE_TIMESTRETCH_SIGNALSMITH   // V46 warp v2
                                wc->setTimeStretchMode (sl.stretch == "fast" ? te::TimeStretcher::soundtouchBetter
                                                                             : te::TimeStretcher::signalsmith);
                               #else
                                wc->setTimeStretchMode (te::TimeStretcher::soundtouchBetter);
                               #endif
                                wc->getLoopInfo().setNumBeats (fileLen * sl.sourceBpm / 60.0);
                                wc->setAutoTempo (true);
                            }
                            wc->setLoopRangeBeats ({ te::BeatPosition(),
                                                     te::BeatPosition::fromBeats (sl.lengthBeats) });
                        }
                    continue;
                }
                if (auto mc = te::insertMIDIClip (*clipSlots[sc],
                                                  sl.name.isNotEmpty() ? sl.name : t.name,
                                                  { 0_tp, endT }))
                {
                    int sni = 0;
                    for (auto& n : sl.notes)
                        if (noteIncluded (n, sni++))       // HB5: per-note chance in launcher slots too
                            mc->getSequence().addNote (n.pitch,
                                                       te::BeatPosition::fromBeats (applySwing (n.start, s)),
                                                       te::BeatDuration::fromBeats (n.len),
                                                       juce::jlimit (1, 127, (int) std::lround (n.vel * 127.0)),
                                                       0, nullptr);
                    mc->setLoopRangeBeats ({ te::BeatPosition(),
                                             te::BeatPosition::fromBeats (sl.lengthBeats) });
                    applyFollow (*mc, sl.follow, sl.followChance);
                }
            }
        }
        pfSlots += pfMs (pfSl);

        if (t.muted)
            track->setMute (true);
    }

    // bus tracks: AuxReturn -> fx chain -> volume
    const auto pfB = juce::Time::getHighResolutionTicks();
    for (auto& b : s.buses)
    {
        auto track = audioTracks[i++];
        track->setName ("bus:" + b.id);
        auto ret = edit->getPluginCache().createNewPlugin (te::AuxReturnPlugin::xmlTypeName, {});
        if (auto* rp = dynamic_cast<te::AuxReturnPlugin*> (ret.get()))
            rp->busNumber = busNum[b.id];
        track->pluginList.insertPlugin (ret, 0, nullptr);
        int fi = 1;
        for (auto& fx : b.fx)
            track->pluginList.insertPlugin (makeFaustFx (*edit, fx), fi++, nullptr);
        if (auto* vol = track->getVolumePlugin())
            vol->setVolumeDb ((float) b.gainDb);
    }
    pfBuses = pfMs (pfB);

    // ---- THE MODULATION GRAPH (#3): wire after every track exists ----
    // LFOs live on the TARGET's track; followers live on their SOURCE track
    // (a modifier eats its own track's audio — kick keys bass = follower on
    // the kick, assigned to the bass's parameter, negative depth = the duck).
    for (auto& m : s.modulators)
    {
        if (! m.target.startsWith ("tracks."))
        { errors << "modulator: v1 targets are tracks.<name>.<param>: " << m.target << "\n"; continue; }
        const auto rest = m.target.fromFirstOccurrenceOf ("tracks.", false, false);
        const auto tname = rest.upToFirstOccurrenceOf (".", false, false);
        const auto ptarget = rest.fromFirstOccurrenceOf (".", false, false);
        auto it = modCtx.find (tname);
        if (it == modCtx.end() || ptarget.isEmpty())
        { errors << "modulator: unknown target track '" << tname << "'\n"; continue; }
        bool isVolDb = false;
        juce::String merr;
        auto* param = resolveAutoTarget (ptarget, it->second.vol, it->second.source,
                                         it->second.fxPlugs, isVolDb, merr);
        if (param == nullptr)
        { errors << "modulator " << m.target << ": " << merr << "\n"; continue; }
        te::AudioTrack* home = it->second.track;
        if (m.kind == "follower")
        {
            auto sit = modCtx.find (m.source);
            if (sit == modCtx.end())
            { errors << "modulator: follower needs source=<track name>, got '" << m.source << "'\n"; continue; }
            home = sit->second.track;
        }
        auto* ml = home->getModifierList();
        if (ml == nullptr)
        { errors << "modulator: no modifier list on " << home->getName() << "\n"; continue; }
        if (m.kind == "follower")
        {
            auto mod = ml->insertModifier (juce::ValueTree (te::IDs::ENVELOPEFOLLOWER), -1, nullptr);
            if (auto* ef = dynamic_cast<te::EnvelopeFollowerModifier*> (mod.get()))
            {
                ef->attack  = (float) juce::jmax (0.3, m.attackMs);
                ef->release = (float) juce::jmax (1.0, m.releaseMs);
                // the SIGN rides the modifier's own depth (-1..1): assignment
                // values do not carry negatives (measured: a -0.9 duck ADDED
                // +10.5 dB) — depth<0 inverts the envelope = the duck.
                ef->depth   = (float) juce::jlimit (-1.0, 1.0, m.depth);
                param->addModifier (*ef, 1.0f);
                if (std::getenv ("SOTADAW_MOD_DEBUG") != nullptr)
                    std::fprintf (stderr, "[modgraph] follower %s -> %s depth=%.2f\n",
                                  m.source.toRawUTF8(), m.target.toRawUTF8(), m.depth);
            }
        }
        else
        {
            auto mod = ml->insertModifier (juce::ValueTree (te::IDs::LFO), -1, nullptr);
            if (auto* lfo = dynamic_cast<te::LFOModifier*> (mod.get()))
            {
                double hz = m.rateHz;
                if (m.sync.isNotEmpty())       // "1/4" = one LFO cycle per beat
                {
                    const double den = m.sync.fromFirstOccurrenceOf ("/", false, false).getDoubleValue();
                    if (den > 0)
                        hz = (s.bpm / 60.0) * (den / 4.0);
                }
                lfo->wave     = (float) m.shape;
                lfo->rateType = (float) te::ModifierCommon::hertz;   // default is BAR-synced
                lfo->rate     = (float) juce::jlimit (0.01, 50.0, hz);
                lfo->depth    = 1.0f;
                lfo->bipolar  = m.bipolar ? 1.0f : 0.0f;
                lfo->phase    = (float) m.phase;
                param->addModifier (*lfo, (float) m.depth);
                if (std::getenv ("SOTADAW_MOD_DEBUG") != nullptr)
                    std::fprintf (stderr, "[modgraph] lfo %.2fHz -> %s depth=%.2f\n",
                                  hz, m.target.toRawUTF8(), m.depth);
            }
        }
    }

    // song-level automation: masterGainDb | master[i].<param>
    for (auto& a : s.automation)
    {
        juce::String aerr;
        if (a.target == "masterGainDb")
        {
            if (auto* mv = edit->getMasterVolumePlugin().get())
                addAutomationCurve (*edit, mv->volParam.get(), a, true);
        }
        else if (a.target.startsWith ("master[") && a.target.contains ("]."))
        {
            const int idx = a.target.fromFirstOccurrenceOf ("master[", false, false).getIntValue();
            const auto id = a.target.fromFirstOccurrenceOf ("].", false, false);
            if (idx >= 0 && idx < (int) masterFxPlugs.size())
            {
                if (auto p = masterFxPlugs[(size_t) idx]->getAutomatableParameterByID (id))
                    addAutomationCurve (*edit, p.get(), a, false);
                else
                    errors << "song automation: param not found: " << a.target << "\n";
            }
            else errors << "song automation: master index out of range: " << a.target << "\n";
        }
        else errors << "song automation: unknown target: " << a.target << "\n";
    }

    if (std::getenv ("SOTADAW_PERF") != nullptr)
        std::printf ("PERF buildEdit phases ms: total=%.1f setup=%.1f source=%.1f fx=%.1f autom=%.1f"
                     " midi=%.1f clips=%.1f slots=%.1f buses=%.1f tracks=%d\n",
                     pfMs (pfT0), pfSetup, pfSource, pfFx, pfAutom, pfMidi, pfClips, pfSlots, pfBuses,
                     (int) s.tracks.size());
    if (errorOut != nullptr) *errorOut = errors;
    return edit;
}

// ---- serialization: Song -> JSON (the UI edits songs and must write them back) ----
inline juce::var fxListToVar (const std::vector<SongFx>& fxs)
{
    juce::Array<juce::var> out;
    for (auto& fx : fxs)
    {
        auto* o = new juce::DynamicObject();
        if (fx.type != "faustfx") o->setProperty ("type", fx.type);
        else                      o->setProperty ("id", fx.id);
        if (fx.preset.isNotEmpty()) o->setProperty ("preset", fx.preset);   // state blobs survive UI saves
        if (fx.bypass) o->setProperty ("bypass", true);
        if (! fx.params.empty())
        {
            auto* pp = new juce::DynamicObject();
            for (auto& [k, v] : fx.params) pp->setProperty (k, v);
            o->setProperty ("params", juce::var (pp));
        }
        out.add (juce::var (o));
    }
    return out;
}

inline juce::var automationToVar (const std::vector<SongAuto>& autos)
{
    juce::Array<juce::var> out;
    for (auto& a : autos)
    {
        auto* o = new juce::DynamicObject();
        o->setProperty ("target", a.target);
        juce::Array<juce::var> pts;
        for (auto& p : a.points)
        {
            auto* po = new juce::DynamicObject();
            po->setProperty ("beat", p.beat);
            po->setProperty ("v", p.v);
            if (p.curve != 0.0) po->setProperty ("curve", p.curve);
            pts.add (juce::var (po));
        }
        o->setProperty ("points", pts);
        out.add (juce::var (o));
    }
    return out;
}

inline juce::var songToVar (const Song& s)
{
    const bool v2 = ! s.buses.empty() || ! s.automation.empty()
                    || std::any_of (s.tracks.begin(), s.tracks.end(),
                                    [] (const SongTrack& t) { return ! t.automation.empty() || ! t.sends.empty(); });
    auto* root = new juce::DynamicObject();
    root->setProperty ("version", v2 ? 2 : (s.version > 0 ? s.version : 1));
    root->setProperty ("bpm", s.bpm);
    if (s.key.isNotEmpty()) root->setProperty ("key", s.key);
    root->setProperty ("lengthBars", s.lengthBars);
    root->setProperty ("masterGainDb", s.masterGainDb);
    if (s.swingAmount > 0.5)
    {
        auto* sw = new juce::DynamicObject();
        sw->setProperty ("grid", s.swingGrid);
        sw->setProperty ("amount", s.swingAmount);
        root->setProperty ("swing", juce::var (sw));
    }
    if (! s.tempoMap.empty())
    {
        juce::Array<juce::var> tm;
        for (auto& tp : s.tempoMap)
        {
            auto* o = new juce::DynamicObject();
            o->setProperty ("bar", tp.bar);
            o->setProperty ("bpm", tp.bpm);
            if (tp.curve != 1.0) o->setProperty ("curve", tp.curve);
            tm.add (juce::var (o));
        }
        root->setProperty ("tempoMap", tm);
    }
    if (! s.sections.empty())
    {
        juce::Array<juce::var> secs;
        for (auto& sec : s.sections)
        {
            auto* o = new juce::DynamicObject();
            o->setProperty ("name", sec.name);
            o->setProperty ("startBar", sec.startBar);
            secs.add (juce::var (o));
        }
        root->setProperty ("sections", secs);
    }
    if (! s.provenance.isVoid())
        root->setProperty ("provenance", s.provenance);   // the song keeps its history
    if (! s.loopMeta.isVoid())
        root->setProperty ("_loop", s.loopMeta);
    if (! s.midiMap.empty())
    {
        juce::Array<juce::var> mm;
        for (auto& b : s.midiMap)
        {
            auto* o = new juce::DynamicObject();
            o->setProperty ("cc", b.cc);
            o->setProperty ("track", b.track);
            o->setProperty ("param", b.param);
            mm.add (juce::var (o));
        }
        root->setProperty ("midiMap", mm);
    }
    if (! s.master.empty())
    {
        juce::Array<juce::var> ms;
        for (auto& m : s.master)
        {
            auto* o = new juce::DynamicObject();
            o->setProperty ("type", m.type != "faustfx" ? m.type
                            : m.id == "master_limiter" ? juce::String ("limiter") : juce::String ("faustfx"));
            if (m.type == "faustfx") o->setProperty ("id", m.id);
            if (m.preset.isNotEmpty()) o->setProperty ("preset", m.preset);
            if (m.bypass) o->setProperty ("bypass", true);
            auto* pp = new juce::DynamicObject();
            for (auto& [k, v] : m.params) pp->setProperty (k, v);
            o->setProperty ("params", juce::var (pp));
            ms.add (juce::var (o));
        }
        root->setProperty ("master", ms);
    }
    if (! s.buses.empty())
    {
        juce::Array<juce::var> bs;
        for (auto& b : s.buses)
        {
            auto* o = new juce::DynamicObject();
            o->setProperty ("id", b.id);
            o->setProperty ("gainDb", b.gainDb);
            if (! b.fx.empty()) o->setProperty ("fx", fxListToVar (b.fx));
            bs.add (juce::var (o));
        }
        root->setProperty ("buses", bs);
    }
    if (! s.automation.empty())
        root->setProperty ("automation", automationToVar (s.automation));
    juce::Array<juce::var> tracks;
    for (auto& t : s.tracks)
    {
        auto* o = new juce::DynamicObject();
        o->setProperty ("name", t.name);
        auto* src = new juce::DynamicObject();
        src->setProperty ("kind", t.source.kind);
        src->setProperty (t.source.kind == "sample" ? "kit" : t.source.kind == "vst3" ? "plugin" : "id", t.source.id);
        if (t.source.preset.isNotEmpty()) src->setProperty ("preset", t.source.preset);
        if (! t.source.params.empty())
        {
            auto* pp = new juce::DynamicObject();
            for (auto& [k, v] : t.source.params) pp->setProperty (k, v);
            src->setProperty ("params", juce::var (pp));
        }
        o->setProperty ("source", juce::var (src));
        o->setProperty ("gainDb", t.gainDb);
        o->setProperty ("pan", t.pan);
        if (t.muted) o->setProperty ("muted", true);
        if (t.locked) o->setProperty ("locked", true);   // survives UI saves — the lock is LAW
        if (t.color.isNotEmpty()) o->setProperty ("color", t.color);
        if (! t.audioClips.empty())
        {
            juce::Array<juce::var> acs;
            for (auto& ac : t.audioClips)
            {
                auto* co = new juce::DynamicObject();
                co->setProperty ("file", ac.file);
                co->setProperty ("startBeat", ac.startBeat);
                if (ac.lengthBeats > 0) co->setProperty ("lengthBeats", ac.lengthBeats);
                if (ac.offsetSec != 0) co->setProperty ("offsetSec", ac.offsetSec);
                if (ac.gainDb != 0) co->setProperty ("gainDb", ac.gainDb);
                if (ac.sourceBpm > 0) co->setProperty ("sourceBpm", ac.sourceBpm);
                if (ac.stretch.isNotEmpty()) co->setProperty ("stretch", ac.stretch);
                if (ac.fadeInBeats > 0) co->setProperty ("fadeInBeats", ac.fadeInBeats);
                if (ac.fadeOutBeats > 0) co->setProperty ("fadeOutBeats", ac.fadeOutBeats);
                if (ac.fadeCurve.isNotEmpty()) co->setProperty ("fadeCurve", ac.fadeCurve);
                if (! ac.tuning.isVoid()) co->setProperty ("tuning", ac.tuning);
                acs.add (juce::var (co));
            }
            o->setProperty ("audioClips", acs);
        }
        if (! t.fx.empty()) o->setProperty ("fx", fxListToVar (t.fx));   // was silently dropped pre-v2
        if (! t.sends.empty())
        {
            juce::Array<juce::var> sds;
            for (auto& sd : t.sends)
            {
                auto* so = new juce::DynamicObject();
                so->setProperty ("bus", sd.bus);
                so->setProperty ("gainDb", sd.gainDb);
                sds.add (juce::var (so));
            }
            o->setProperty ("sends", sds);
        }
        if (! t.automation.empty())
            o->setProperty ("automation", automationToVar (t.automation));
        juce::Array<juce::var> notes;
        for (auto& n : t.notes)
        {
            auto* no = new juce::DynamicObject();
            no->setProperty ("start", n.start);
            no->setProperty ("len", n.len);
            no->setProperty ("pitch", n.pitch);
            no->setProperty ("vel", n.vel);
            if (n.chance < 0.999) no->setProperty ("chance", n.chance);   // HB5 (omit when 1.0)
            notes.add (juce::var (no));
        }
        o->setProperty ("notes", notes);
        if (! t.slots.empty())
        {
            juce::Array<juce::var> sls;
            for (auto& sl : t.slots)
            {
                if (! sl.present) { sls.add (juce::var()); continue; }
                auto* so = new juce::DynamicObject();
                if (sl.name.isNotEmpty()) so->setProperty ("name", sl.name);
                so->setProperty ("lengthBeats", sl.lengthBeats);
                if (sl.audioFile.isNotEmpty())
                {
                    so->setProperty ("audioFile", sl.audioFile);
                    if (sl.offsetSec != 0) so->setProperty ("offsetSec", sl.offsetSec);
                    if (sl.sourceBpm > 0) so->setProperty ("sourceBpm", sl.sourceBpm);
                    if (sl.stretch.isNotEmpty()) so->setProperty ("stretch", sl.stretch);
                    if (sl.follow.isNotEmpty()) so->setProperty ("follow", sl.follow);
                    if (sl.followChance < 1.0) so->setProperty ("followChance", sl.followChance);
                }
                juce::Array<juce::var> sn;
                for (auto& n : sl.notes)
                {
                    auto* no = new juce::DynamicObject();
                    no->setProperty ("start", n.start);
                    no->setProperty ("len", n.len);
                    no->setProperty ("pitch", n.pitch);
                    no->setProperty ("vel", n.vel);
                    sn.add (juce::var (no));
                }
                so->setProperty ("notes", sn);
                sls.add (juce::var (so));
            }
            o->setProperty ("slots", sls);
        }
        if (t.grooveName.isNotEmpty())
        {
            auto* go = new juce::DynamicObject();
            go->setProperty ("name", t.grooveName);
            go->setProperty ("amount", t.grooveAmount);
            o->setProperty ("groove", juce::var (go));
        }
        tracks.add (juce::var (o));
    }
    root->setProperty ("tracks", tracks);
    if (! s.sceneNames.isEmpty())
    {
        juce::Array<juce::var> scs;
        for (auto& sc : s.sceneNames)
        {
            auto* so = new juce::DynamicObject();
            so->setProperty ("name", sc);
            scs.add (juce::var (so));
        }
        root->setProperty ("scenes", scs);
    }
    // THE UNDROPPABLE LAW: re-emit what parseSong didn't model. Modeled fields
    // always win (hasProperty guard), so set drift is harmless.
    if (auto* ex = s.extras.getDynamicObject())
        for (auto& p : ex->getProperties())
            if (! root->hasProperty (p.name))
                root->setProperty (p.name, p.value);
    return juce::var (root);
}

inline bool saveSong (const Song& s, const juce::File& f)
{
    return f.replaceWithText (juce::JSON::toString (songToVar (s)));
}

} // namespace sotadaw
