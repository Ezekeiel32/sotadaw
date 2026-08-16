// THE SCORE ENGRAVING KERNEL (SCORE tab, 2026-08-02) — song.json -> engraved
// notation model. Pure layout/spelling logic, no painting: ScorePage.h draws it
// (Bravura/SMuFL), m1 `score-probe` prints its census for tools/score_battery.py.
//
// The laws implemented here are real engraving law, not approximations:
//  - DISPLAY QUANTIZE: per-staff, per-beat grid election (16th default, 32nd when
//    the material demands, triplet grid when a beat's onsets fit 1/3 better than
//    1/4) — display-only; song data is never touched.
//  - RHYTHM SPELLING: metric-tree splitting. A duration renders as ONE value only
//    where convention allows (beat-group spans, syncopation whitelist); otherwise
//    it splits at the strongest metric boundary inside it and TIES — recursively.
//    Rests split stricter (no syncopated rests, no dotted rests in simple meter).
//  - THE WORLD GRID: meterMap num/den per bar; compound (x/8, num%3==0) groups in
//    dotted quarters; 7/8-style bars group 3+2+2.
//  - PITCH SPELLING: key signature from song.key (letter+mode -> fifths), scale
//    degrees spelled through the signature, chromatics by practice (b3/b6/b7 flat
//    in major, raised 6/7 in minor, #4 lydian) — accidental STATE is per measure
//    per letter+octave, exactly like a reader tracks it.
//  - DRUMS: Weinberg standard drumset mapping (kick 1st space, snare 3rd space,
//    hats/cymbals x-heads above), hands = voice 0 stems up, feet = voice 1 stems
//    down, all drum tracks MERGED onto one staff (per-head writeback survives).
//  - BEAMS: per metric beat-group; pure-8th runs merge to half-bar pairs in 4/4.
//  - SPACING: Gourlay column widths (a + b*log2(dt)), columns aligned score-wide.
#pragma once
#include "SongLoader.h"
#include <cmath>
#include <map>
#include <set>
#include <vector>

namespace score
{
using sotadaw::Song;
using sotadaw::SongNote;
using sotadaw::SongTrack;

//============================================================== identity + roles
enum class Clef { Treble, Bass, Percussion };
enum class HeadShape { Normal, X, CircleX };
enum class DrumRole { Kick, Snare, Clap, HatClosed, HatOpen, HatPedal, Ride,
                      Crash, TomHigh, TomMid, TomFloor, Aux, None };

struct SrcRef { int track = -1, note = -1; };

// staff steps are DIATONIC: 0 = bottom line, +1 per line/space. Lines at 0,2,4,6,8.
inline int drumStep (DrumRole r)
{
    switch (r)
    {
        case DrumRole::Kick:      return 1;   // 1st space
        case DrumRole::TomFloor:  return 3;   // 2nd space
        case DrumRole::Snare:     return 5;   // 3rd space
        case DrumRole::Clap:      return 5;   // snare space, x head
        case DrumRole::TomMid:    return 6;   // 4th line
        case DrumRole::TomHigh:   return 7;   // 4th space
        case DrumRole::Ride:      return 8;   // top line, x head
        case DrumRole::HatClosed: return 9;   // above top line, x head
        case DrumRole::HatOpen:   return 9;   // same spot, circle-x head
        case DrumRole::Crash:     return 11;  // 1st ledger above, x head
        case DrumRole::HatPedal:  return -1;  // below staff, x head
        default:                  return 9;   // aux percussion rides high
    }
}
inline HeadShape drumShape (DrumRole r)
{
    switch (r)
    {
        case DrumRole::Kick: case DrumRole::Snare:
        case DrumRole::TomHigh: case DrumRole::TomMid: case DrumRole::TomFloor:
            return HeadShape::Normal;
        case DrumRole::HatOpen: return HeadShape::CircleX;
        default:                return HeadShape::X;
    }
}
inline bool drumIsFoot (DrumRole r) { return r == DrumRole::Kick || r == DrumRole::HatPedal; }

// name/instrument classification. Melodic words VETO first (formant_vox is a
// voice, chip_bass is a bass — "808" alone never decides).
inline DrumRole roleForTrack (const SongTrack& t)
{
    const auto hay = (t.name + " " + t.source.id + " " + t.source.preset).toLowerCase();
    auto has = [&hay] (const char* w) { return hay.contains (w); };
    if (has ("vox") || has ("vocal") || has ("voice") || has ("choir") || has ("lead")
        || has ("bass") || has ("pad") || has ("key") || has ("pluck") || has ("chord")
        || has ("arp") || has ("piano") || has ("organ") || has ("guitar") || has ("string")
        || has ("brass") || has ("flute") || has ("bell") || has ("sax") || has ("synth")
        || has ("melody") || has ("sketch"))
        return DrumRole::None;
    if (has ("kick") || has ("bd_") || hay == "bd")            return DrumRole::Kick;
    if (has ("snare") || has ("rim"))                          return DrumRole::Snare;
    if (has ("clap"))                                          return DrumRole::Clap;
    if (has ("openhat") || has ("open_hat") || has ("ohat"))   return DrumRole::HatOpen;
    if (has ("hat") || has ("hh"))                             return DrumRole::HatClosed;
    if (has ("ride"))                                          return DrumRole::Ride;
    if (has ("crash") || has ("cym") || has ("china") || has ("splash")) return DrumRole::Crash;
    if (has ("floor"))                                         return DrumRole::TomFloor;
    if (has ("tom"))                                           return DrumRole::TomMid;
    if (has ("shaker") || has ("tamb") || has ("guira") || has ("cabasa")
        || has ("maraca") || has ("noise"))                    return DrumRole::Aux;
    if (has ("conga") || has ("bongo") || has ("darbuka") || has ("dhol")
        || has ("tabla") || has ("djembe") || has ("timbale") || has ("block")
        || has ("cowbell") || has ("perc") || has ("drum"))    return DrumRole::TomMid;
    return DrumRole::None;
}

//============================================================== key + spelling
struct KeySig
{
    int fifths = 0;            // -7..7
    bool minor = false;
    int tonicLetter = 0;       // 0=C..6=B
    juce::String label;
};

inline int naturalPc (int letter) { static const int p[7] = { 0, 2, 4, 5, 7, 9, 11 }; return p[letter]; }

inline KeySig parseKey (const juce::String& key)
{
    KeySig k;
    auto s = key.trim();
    if (s.isEmpty()) { k.label = "C"; return k; }
    const auto c0 = (char) juce::CharacterFunctions::toUpperCase (s[0]);
    static const int letterOf[7] = { 5, 6, 0, 1, 2, 3, 4 };   // A..G -> C-based index
    if (c0 < 'A' || c0 > 'G') { k.label = "C"; return k; }
    k.tonicLetter = letterOf[c0 - 'A'];
    int alter = 0, i = 1;
    while (i < s.length() && (s[i] == '#' || s[i] == 'b'))
        { alter += (s[i] == '#' ? 1 : -1); ++i; }
    const auto rest = s.substring (i).trim().toLowerCase();
    k.minor = rest.startsWith ("min") || rest == "m" || rest.startsWith ("m ")
              || rest.startsWith ("aeol") || rest.startsWith ("dor");   // modal ~ minor signature
    static const int baseFifths[7] = { 0, 2, 4, -1, 1, 3, 5 };          // C D E F G A B
    k.fifths = baseFifths[k.tonicLetter] + 7 * alter - (k.minor ? 3 : 0);
    k.fifths = juce::jlimit (-7, 7, k.fifths);
    k.label = s;
    return k;
}

// key-signature alteration for a letter (0=C..6=B): sharps F C G D A E B, flats B E A D G C F
inline int keyAlter (const KeySig& k, int letter)
{
    static const int sharpOrder[7] = { 3, 0, 4, 1, 5, 2, 6 };
    for (int i = 0; i < juce::jmin (7,  k.fifths); ++i) if (sharpOrder[i] == letter)     return 1;
    for (int i = 0; i < juce::jmin (7, -k.fifths); ++i) if (sharpOrder[6 - i] == letter) return -1;
    return 0;
}

struct Spelled { int letter = 0; int alter = 0; int octave = 4; int absStep = 0; };

// spell a MIDI pitch through the key: scale degrees ride the signature, chromatics
// by common practice (see table rationale in the header comment)
inline Spelled spellPitch (int pitch, const KeySig& k)
{
    const int pc = ((pitch % 12) + 12) % 12;
    // tonic pc through its own signature alter (Gb major's G wears the flat)
    const int tonicPc = (naturalPc (k.tonicLetter) + keyAlter (k, k.tonicLetter) + 12) % 12;
    int off = ((pc - tonicPc) + 12) % 12;
    // (scale-letter offset from tonic, alteration relative to the key signature)
    static const int majT[12][2] = { {0,0},{0,1},{1,0},{2,-1},{2,0},{3,0},{3,1},{4,0},{5,-1},{5,0},{6,-1},{6,0} };
    static const int minT[12][2] = { {0,0},{1,-1},{1,0},{2,0},{2,1},{3,0},{3,1},{4,0},{5,0},{5,1},{6,0},{6,1} };
    int lo = (k.minor ? minT : majT)[off][0], ra = (k.minor ? minT : majT)[off][1];
    if (! k.minor && off == 1 && k.fifths < 0) { lo = 1; ra = -1; }   // flat keys: b2 not #1
    Spelled sp;
    sp.letter = (k.tonicLetter + lo) % 7;
    sp.alter  = juce::jlimit (-2, 2, keyAlter (k, sp.letter) + ra);
    const int base = naturalPc (sp.letter) + sp.alter;
    sp.octave = (int) std::lround ((pitch - base) / 12.0);
    sp.absStep = sp.octave * 7 + sp.letter;
    return sp;
}

//============================================================== the model
struct Head
{
    int step = 0;              // staff step (0 = bottom line)
    int alter = 0;             // spelled alteration (vs natural)
    int shownAcc = -9;         // -9 = no accidental drawn, else -2..2 (0 = natural sign)
    HeadShape shape = HeadShape::Normal;
    bool otherSide = false;    // 2nds cluster: this head sits across the stem
    bool ghostAdd = false;     // proposal diff paint
    bool ghostRemove = false;
    float vel = 0.8f;
    SrcRef src;                // writeback: song.tracks[track].notes[note]
};

struct Element
{
    double start = 0, dur = 0.25;   // measure-local, display-quantized quarter-beats
    bool isRest = false;
    int denom = 4;                  // 1 2 4 8 16 32
    int dots = 0;
    bool triplet = false;
    bool tieFrom = false, tieTo = false;
    int voice = 0;
    bool stemUp = true;
    int beamGroup = -1;             // Measure::beams index
    int col = 0;                    // column index in Measure::colBeats
    int artic = 0;                  // 1 = staccato (absorb law), 2 = accent (vel spike)
    std::vector<Head> heads;        // sorted ascending step; empty = rest
    bool wholeMeasureRest = false;
};

struct Measure
{
    double startBeat = 0, beats = 4;
    int num = 4, den = 4;
    bool showMeter = false;
    std::vector<double> groups;         // beat-group sizes (quarter-beats)
    std::vector<Element> v[2];
    struct Beam { int voice = 0; std::vector<int> idx; };
    std::vector<Beam> beams;
    std::vector<double> colBeats;       // score-wide aligned columns (measure-local)
};

struct GhostStrike { int measure = 0; double start = 0; int step = 0; };   // removed-note overlay

struct Staff
{
    juce::String name;
    int trackIdx = -1;                  // -1 = merged drums
    std::vector<int> mergedTracks;
    Clef clef = Clef::Treble;
    bool isDrums = false;
    std::vector<Measure> measures;
    std::vector<GhostStrike> strikes;
    int loStep = 0, hiStep = 8;         // vertical extent across the whole part
    bool hidden = false;
    struct Dyn  { double beat = 0; int level = 3; };       // 0..5 = pp p mp mf f ff (global beats)
    struct Hair { double a = 0, b = 0; bool cresc = true; };
    std::vector<Dyn> dyns;              // derived from velocities (melodic staves)
    std::vector<Hair> hairs;
};

struct ChordMark   { int measure = 0; juce::String label; };
struct SectionMark { int measure = 0; juce::String name; };
struct TempoMark   { int measure = 0; double bpm = 120; };
struct LyricSyl    { double beat = 0; juce::String text; };

struct Model
{
    std::vector<Staff> staves;
    int numMeasures = 0;
    KeySig key;
    std::vector<ChordMark> chords;
    std::vector<SectionMark> sections;
    std::vector<TempoMark> tempos;
    std::vector<LyricSyl> lyrics;       // shown under the sung staff when present
    int lyricStaff = -1;
    bool swung = false;
    double quant = 0.25;
};

//============================================================== rhythm spelling
struct NoteVal { int denom; int dots; };
inline bool durToVal (double d, bool triplet, NoteVal& out)
{
    struct Row { double d; int den, dots; };
    static const Row straight[] = { {4,1,0},{3,2,1},{2,2,0},{1.5,4,1},{1,4,0},{0.75,8,1},
                                    {0.5,8,0},{0.375,16,1},{0.25,16,0},{0.125,32,0} };
    static const Row trip[]     = { {1.0/3,8,0},{2.0/3,4,0},{1.0/6,16,0} };
    if (triplet)
        { for (auto& r : trip) if (std::abs (d - r.d) < 1e-6) { out = { r.den, r.dots }; return true; } }
    for (auto& r : straight) if (std::abs (d - r.d) < 1e-6) { out = { r.den, r.dots }; return true; }
    return false;
}

// beat-group pattern for a meter, in quarter-beats
inline std::vector<double> groupsFor (int num, int den)
{
    std::vector<double> g;
    if (den == 8 && num % 3 == 0)      { for (int i = 0; i < num / 3; ++i) g.push_back (1.5); }
    else if (den == 8)                 { g.push_back (1.5); for (int i = 3; i + 1 < num; i += 2) g.push_back (1.0);
                                         if ((num - 3) % 2 == 1) g.push_back (0.5); }
    else                               { const double b = 4.0 / den; for (int i = 0; i < num; ++i) g.push_back (b); }
    if (g.empty()) g.push_back (4.0);
    return g;
}

namespace detail
{
    inline bool nearMult (double v, double grid) { return std::abs (v / grid - std::round (v / grid)) < 1e-6; }

    struct MeasureCtx
    {
        double beats; int num, den;
        std::vector<double> bounds;      // cumulative group boundaries incl. 0 and beats
        bool tripletBeat (double t) const { return tripFlags && ! tripFlags->empty()
                                                   && (*tripFlags)[juce::jlimit (0, (int) tripFlags->size() - 1, (int) std::floor (t + 1e-6))]; }
        const std::vector<char>* tripFlags = nullptr;
        double halfBar() const { return (num == 4 && den == 4) ? 2.0 : -1.0; }
    };

    inline int boundaryRank (const MeasureCtx& m, double x)
    {
        if (m.halfBar() > 0 && std::abs (x - m.halfBar()) < 1e-6) return 5;   // outranks beats
        for (auto b : m.bounds) if (std::abs (x - b) < 1e-6) return 4;
        if (nearMult (x, 0.5))   return 3;
        if (nearMult (x, 0.25))  return 2;
        if (nearMult (x, 0.125)) return 1;
        if (nearMult (x, 1.0 / 3.0) || nearMult (x, 1.0 / 6.0)) return 2;
        return 0;
    }

    // may [t, t+d) render as ONE notated value?
    inline bool canSingleNote (const MeasureCtx& m, double t, double d)
    {
        if (m.tripletBeat (t))
        {
            const double b0 = std::floor (t + 1e-6);
            if (t + d > b0 + 1.0 + 1e-6) return false;             // triplets never cross their beat
            NoteVal v;
            return durToVal (d, true, v) && nearMult (t - b0, d >= 0.5 ? 1.0 / 3.0 : 1.0 / 6.0);
        }
        NoteVal v;
        if (! durToVal (d, false, v)) return false;
        // exact span of consecutive beat-groups from a group start
        double acc = 0;
        for (size_t i = 0; i + 1 < m.bounds.size(); ++i)
            if (std::abs (t - m.bounds[i]) < 1e-6)
            {
                acc = 0;
                for (size_t j = i; j + 1 < m.bounds.size(); ++j)
                {
                    acc += m.bounds[j + 1] - m.bounds[j];
                    if (std::abs (d - acc) < 1e-6) return true;
                }
            }
        if (m.den == 4)
        {   // syncopation whitelist (editor practice, see header)
            if (std::abs (d - 3.0) < 1e-6)  return nearMult (t, 1.0) && t + d <= m.beats + 1e-6;
            if (std::abs (d - 2.0) < 1e-6)  return nearMult (t, 1.0) && t + d <= m.beats + 1e-6;
            if (std::abs (d - 1.5) < 1e-6)  return nearMult (t, 0.5) && t + d <= m.beats + 1e-6;
            if (std::abs (d - 1.0) < 1e-6)  return nearMult (t, 0.25) && t + d <= m.beats + 1e-6;
        }
        // inside ONE group, on the value's own grid (dotted values ride base/2)
        for (size_t i = 0; i + 1 < m.bounds.size(); ++i)
            if (t >= m.bounds[i] - 1e-6 && t + d <= m.bounds[i + 1] + 1e-6)
            {
                const double base = 4.0 / (double) v.denom;
                const double grid = v.dots ? base / 2.0 : juce::jmin (base, 0.25);
                return nearMult (t - m.bounds[i], grid);
            }
        return false;
    }

    inline bool canSingleRest (const MeasureCtx& m, double t, double d)
    {
        if (std::abs (t) < 1e-6 && std::abs (d - m.beats) < 1e-6) return true;   // whole-measure
        if (m.tripletBeat (t))
        {
            const double b0 = std::floor (t + 1e-6);
            if (t + d > b0 + 1.0 + 1e-6) return false;
            NoteVal v;
            return durToVal (d, true, v) && nearMult (t - b0, 1.0 / 6.0);
        }
        NoteVal v;
        if (! durToVal (d, false, v)) return false;
        if (m.den == 4 && v.dots > 0) return false;                 // no dotted rests, simple meter
        if (m.num == 4 && m.den == 4 && std::abs (d - 2.0) < 1e-6)  // half rest at 1 or 3 only
            return std::abs (t) < 1e-6 || std::abs (t - 2.0) < 1e-6;
        for (size_t i = 0; i + 1 < m.bounds.size(); ++i)            // else: inside one group, on-grid
            if (t >= m.bounds[i] - 1e-6 && t + d <= m.bounds[i + 1] + 1e-6)
            {
                const double base = 4.0 / (double) v.denom;
                return nearMult (t - m.bounds[i], v.dots ? base / 2.0 : base);
            }
        return false;
    }

    inline double splitPoint (const MeasureCtx& m, double t0, double t1)
    {
        const double grid = m.tripletBeat (t0) ? 1.0 / 6.0 : 0.125;
        double best = -1; int bestRank = -1;
        for (double x = std::floor (t0 / grid + 1.0 + 1e-9) * grid; x < t1 - 1e-6; x += grid)
        {
            if (x <= t0 + 1e-6) continue;
            const int r = boundaryRank (m, x);
            if (r > bestRank) { bestRank = r; best = x; }           // ties keep the FIRST
        }
        return best > 0 ? best : (t0 + t1) * 0.5;
    }

    template <typename Emit>
    inline void spellSpan (const MeasureCtx& m, double t0, double t1, bool isRest, int depth, Emit&& emit)
    {
        if (t1 - t0 < 1e-6) return;
        if (depth > 24) { emit (t0, t1 - t0, true); return; }       // safety: emit unlabeled
        const bool ok = isRest ? canSingleRest (m, t0, t1 - t0) : canSingleNote (m, t0, t1 - t0);
        if (ok) { emit (t0, t1 - t0, false); return; }
        const double x = splitPoint (m, t0, t1);
        if (x <= t0 + 1e-9 || x >= t1 - 1e-9) { emit (t0, t1 - t0, true); return; }
        spellSpan (m, t0, x, isRest, depth + 1, emit);
        spellSpan (m, x, t1, isRest, depth + 1, emit);
    }
} // namespace detail

//============================================================== build options
struct Options
{
    double quant = 0.0;          // 0 = AUTO; else 0.5 / 0.25 / 0.125 display grid
    bool mergeDrums = true;
    const Song* proposal = nullptr;                       // ghost overlay source
    const std::map<int, std::set<juce::String>>* addedKeys = nullptr;    // track -> noteKey set
    const std::map<int, std::vector<SongNote>>* removedNotes = nullptr;  // track -> struck notes
};

inline juce::String ghostNoteKey (const SongNote& n)
{
    return juce::String ((int) std::lround (n.start * 1000)) + ":" + juce::String (n.pitch)
         + ":" + juce::String ((int) std::lround (n.len * 1000))
         + ":" + juce::String ((int) std::lround (n.vel * 100));
}

//============================================================== the builder
inline Model buildModel (const Song& song, const Options& opt)
{
    Model mo;
    mo.key = parseKey (song.key);
    mo.swung = song.swingAmount > 0.515;
    const Song& src = opt.proposal != nullptr ? *opt.proposal : song;

    // ---- measures of the world (meterMap-aware)
    double lastEnd = 0;
    for (auto& t : src.tracks) for (auto& n : t.notes) lastEnd = juce::jmax (lastEnd, n.start + n.len);
    int numBars = (int) std::ceil (juce::jmax (song.lengthBars, 1.0));
    while (src.barStartBeat (numBars) < lastEnd - 1e-6) ++numBars;
    numBars = juce::jmin (numBars, 512);
    mo.numMeasures = numBars;

    struct BarInfo { double start, beats; int num, den; bool show; };
    std::vector<BarInfo> bars;
    int cn = 4, cd = 4;
    for (int b = 0; b < numBars; ++b)
    {
        int nn = 4, nd = 4;
        for (auto& mp : src.meterMap) if (mp.bar <= b + 1e-9) { nn = mp.num; nd = mp.den; }
        BarInfo bi { src.barStartBeat (b), src.beatsInBar (b), nn, nd, b == 0 || nn != cn || nd != cd };
        cn = nn; cd = nd;
        bars.push_back (bi);
    }

    // ---- staff plan: melodic tracks in song order, merged DRUMS staff last
    std::vector<int> drumTracks;
    for (int ti = 0; ti < (int) src.tracks.size(); ++ti)
    {
        auto& t = src.tracks[(size_t) ti];
        if (t.source.kind == "audio" || t.notes.empty()) continue;
        if (roleForTrack (t) != DrumRole::None && opt.mergeDrums) { drumTracks.push_back (ti); continue; }
        Staff st;
        st.name = t.name;
        st.trackIdx = ti;
        if (roleForTrack (t) != DrumRole::None)
        { st.isDrums = true; st.clef = Clef::Percussion; st.mergedTracks = { ti }; }
        else
        {   // clef by register: median below G3 -> bass
            std::vector<int> ps; ps.reserve (t.notes.size());
            for (auto& n : t.notes) ps.push_back (n.pitch);
            std::nth_element (ps.begin(), ps.begin() + (long) ps.size() / 2, ps.end());
            st.clef = ps[ps.size() / 2] < 55 ? Clef::Bass : Clef::Treble;
        }
        mo.staves.push_back (std::move (st));
    }
    if (! drumTracks.empty())
    {
        Staff st;
        st.name = "DRUMS";
        st.isDrums = true;
        st.clef = Clef::Percussion;
        st.mergedTracks = drumTracks;
        mo.staves.push_back (std::move (st));
    }

    // ---- per staff: quantize -> voices -> measures -> spelling -> beams
    for (auto& st : mo.staves)
    {
        struct QN { double qs, qe; int pitch; float vel; SrcRef src; DrumRole role; bool gAdd = false; };
        std::vector<QN> qs;
        const auto& tracks = st.mergedTracks.empty() ? std::vector<int> { st.trackIdx } : st.mergedTracks;

        // triplet flags per whole-song beat (per staff): elected from raw onsets
        const int nGlobalBeats = (int) std::ceil (bars.back().start + bars.back().beats) + 1;
        std::vector<char> tripFlag ((size_t) nGlobalBeats, 0);
        if (opt.quant <= 0.0)
        {
            std::vector<std::vector<double>> perBeat ((size_t) nGlobalBeats);
            for (int ti : tracks)
                for (auto& n : src.tracks[(size_t) ti].notes)
                {
                    const int b = (int) std::floor (n.start + 1e-6);
                    if (b >= 0 && b < nGlobalBeats) perBeat[(size_t) b].push_back (n.start - b);
                }
            for (int b = 0; b < nGlobalBeats; ++b)
            {
                auto& v = perBeat[(size_t) b];
                if (v.size() < 2) continue;
                double e16 = 0, e12 = 0;
                for (double f : v)
                {
                    e16 += std::abs (f - std::round (f * 4.0) / 4.0);
                    e12 += std::abs (f - std::round (f * 3.0) / 3.0);
                }
                if (e12 * 1.15 < e16 - 1e-9) tripFlag[(size_t) b] = 1;
            }
        }
        auto snap = [&tripFlag, &opt] (double t, bool isDur, double anchor) -> double
        {
            const int b = (int) std::floor ((isDur ? anchor : t) + 1e-6);
            const bool trip = b >= 0 && b < (int) tripFlag.size() && tripFlag[(size_t) b];
            const double g = opt.quant > 0.0 ? opt.quant : (trip ? 1.0 / 3.0 : 0.25);
            return std::round (t / g) * g;
        };

        for (int ti : tracks)
        {
            auto& t = src.tracks[(size_t) ti];
            const auto role = st.isDrums ? roleForTrack (t) : DrumRole::None;
            const auto* added = opt.addedKeys != nullptr && opt.addedKeys->count (ti)
                                  ? &opt.addedKeys->at (ti) : nullptr;
            for (int ni = 0; ni < (int) t.notes.size(); ++ni)
            {
                auto& n = t.notes[(size_t) ni];
                QN q;
                q.qs = juce::jmax (0.0, snap (n.start, false, 0));
                const double grid = opt.quant > 0.0 ? opt.quant
                                   : (tripFlag[(size_t) juce::jlimit (0, (int) tripFlag.size() - 1,
                                       (int) std::floor (q.qs + 1e-6))] ? 1.0 / 3.0 : 0.25);
                // the END snaps on ITS OWN beat's grid (mixed straight/triplet seams
                // otherwise mint 1/12-beat fragments no notation can spell)
                q.qe = st.isDrums ? q.qs + grid
                                  : juce::jmax (q.qs + grid, snap (n.start + n.len, false, 0));
                q.pitch = n.pitch;
                q.vel = (float) n.vel;
                q.src = { ti, ni };
                q.role = role == DrumRole::None && st.isDrums ? DrumRole::Aux : role;
                q.gAdd = added != nullptr && added->count (ghostNoteKey (n)) > 0;
                qs.push_back (q);
            }
        }
        std::sort (qs.begin(), qs.end(), [] (const QN& a, const QN& b)
                   { return a.qs < b.qs || (a.qs == b.qs && a.pitch < b.pitch); });

        // voice assignment. drums: hands/feet. melodic: overlap -> voice 1
        struct VN { double qs, qe; std::vector<QN> members; };
        std::vector<VN> voiceNotes[2];
        auto sameStart = [] (double a, double b) { return std::abs (a - b) < 1e-6; };
        for (auto& q : qs)
        {
            const int want = st.isDrums ? (drumIsFoot (q.role) ? 1 : 0) : 0;
            auto& primary = voiceNotes[want];
            if (! primary.empty() && sameStart (primary.back().qs, q.qs))
            { primary.back().members.push_back (q); primary.back().qe = juce::jmax (primary.back().qe, q.qe); continue; }
            if (! st.isDrums && ! primary.empty() && primary.back().qe > q.qs + 1e-6)
            {
                auto& second = voiceNotes[1];
                if (! second.empty() && sameStart (second.back().qs, q.qs))
                { second.back().members.push_back (q); second.back().qe = juce::jmax (second.back().qe, q.qe); continue; }
                if (second.empty() || second.back().qe <= q.qs + 1e-6)
                { second.push_back ({ q.qs, q.qe, { q } }); continue; }
                primary.back().qe = q.qs;                    // both busy: truncate display
                primary.push_back ({ q.qs, q.qe, { q } });
                continue;
            }
            primary.push_back ({ q.qs, q.qe, { q } });
        }
        for (int v = 0; v < 2; ++v)                          // monophony per voice (display)
            for (size_t i = 0; i + 1 < voiceNotes[v].size(); ++i)
                voiceNotes[v][i].qe = juce::jmin (voiceNotes[v][i].qe, voiceNotes[v][i + 1].qs);

        // measures
        st.measures.resize ((size_t) numBars);
        for (int b = 0; b < numBars; ++b)
        {
            auto& M = st.measures[(size_t) b];
            M.startBeat = bars[(size_t) b].start;
            M.beats = bars[(size_t) b].beats;
            M.num = bars[(size_t) b].num; M.den = bars[(size_t) b].den;
            M.showMeter = bars[(size_t) b].show;
            M.groups = groupsFor (M.num, M.den);
        }

        auto barIndexAt = [&bars] (double beat) -> int
        {
            int lo = 0;
            for (int i = 0; i < (int) bars.size(); ++i)
                if (bars[(size_t) i].start <= beat + 1e-6) lo = i; else break;
            return lo;
        };

        for (int v = 0; v < 2; ++v)
        {
            for (auto& vn : voiceNotes[v])
            {
                double t = vn.qs;
                bool first = true;
                while (t < vn.qe - 1e-6)
                {
                    const int bi = juce::jmin (barIndexAt (t), numBars - 1);
                    auto& M = st.measures[(size_t) bi];
                    const double mEnd = M.startBeat + M.beats;
                    const double segEnd = juce::jmin (vn.qe, mEnd);
                    detail::MeasureCtx ctx { M.beats, M.num, M.den, {}, nullptr };
                    ctx.bounds.push_back (0);
                    for (double gsz : M.groups) ctx.bounds.push_back (ctx.bounds.back() + gsz);
                    std::vector<char> localTrip ((size_t) std::ceil (M.beats) + 1, 0);
                    for (int lb = 0; lb < (int) localTrip.size(); ++lb)
                    {
                        const int gb = (int) std::floor (M.startBeat + lb + 1e-6);
                        if (gb >= 0 && gb < (int) tripFlag.size()) localTrip[(size_t) lb] = tripFlag[(size_t) gb];
                    }
                    ctx.tripFlags = &localTrip;
                    const bool lastSeg = segEnd >= vn.qe - 1e-6;
                    std::vector<std::pair<double, double>> pieces;
                    detail::spellSpan (ctx, t - M.startBeat, segEnd - M.startBeat, false, 0,
                        [&pieces] (double s, double d, bool) { pieces.push_back ({ s, d }); });
                    for (size_t p = 0; p < pieces.size(); ++p)
                    {
                        Element e;
                        e.start = pieces[p].first; e.dur = pieces[p].second;
                        e.voice = v;
                        const int gBeat = (int) std::floor (M.startBeat + e.start + 1e-6);
                        e.triplet = gBeat >= 0 && gBeat < (int) tripFlag.size() && tripFlag[(size_t) gBeat]
                                    && std::abs (e.dur - 1.0) > 1e-6 && e.dur < 1.0 - 1e-6;
                        NoteVal nv { 4, 0 };
                        durToVal (e.dur, e.triplet, nv);
                        e.denom = nv.denom; e.dots = nv.dots;
                        e.tieTo = ! (first && p == 0);
                        e.tieFrom = ! (lastSeg && p + 1 == pieces.size());
                        for (auto& m2 : vn.members)
                        {
                            Head h;
                            if (st.isDrums)
                            { h.step = drumStep (m2.role); h.shape = drumShape (m2.role); h.alter = 0; }
                            else
                            {
                                const auto sp = spellPitch (m2.pitch, mo.key);
                                h.step = sp.absStep - (st.clef == Clef::Bass ? 18 : 30);
                                h.alter = sp.alter;
                            }
                            h.vel = m2.vel; h.src = m2.src; h.ghostAdd = m2.gAdd;
                            e.heads.push_back (h);
                        }
                        std::sort (e.heads.begin(), e.heads.end(),
                                   [] (const Head& a, const Head& b) { return a.step < b.step; });
                        e.heads.erase (std::unique (e.heads.begin(), e.heads.end(),
                                   [] (const Head& a, const Head& b) { return a.step == b.step && a.shape == b.shape; }),
                                   e.heads.end());
                        M.v[v].push_back (std::move (e));
                    }
                    t = segEnd;
                    first = false;
                }
            }
            // THE ABSORB LAW (melodic v0): a lone short note in its beat displays as
            // the beat's value — plain when the raw length nearly fills it, staccato
            // when it is genuinely short. Real MIDI is full of 0.2-beat dust that
            // literal spelling peppers with rests; an engraver writes the beat and
            // dots it. Clean half-beat figures (8th + 8th rest) keep their literal
            // spelling — the dot fires only when the shown value would be under HALF
            // the absorbed span.
            if (v == 0 && ! st.isDrums)
                for (int b = 0; b < numBars; ++b)
                {
                    auto& M = st.measures[(size_t) b];
                    auto& vec = M.v[0];
                    std::sort (vec.begin(), vec.end(), [] (const Element& a, const Element& b2)
                               { return a.start < b2.start; });
                    std::vector<double> bounds { 0.0 };
                    for (double gsz : M.groups) bounds.push_back (bounds.back() + gsz);
                    for (size_t i = 0; i < vec.size(); ++i)
                    {
                        auto& e = vec[i];
                        if (e.isRest || e.tieFrom || e.tieTo || e.triplet || e.heads.empty()) continue;
                        const int gBeat = (int) std::floor (M.startBeat + e.start + 1e-6);
                        if (gBeat >= 0 && gBeat < (int) tripFlag.size() && tripFlag[(size_t) gBeat]) continue;
                        double nextBound = M.beats;
                        for (double bd : bounds) if (bd > e.start + 1e-6) { nextBound = bd; break; }
                        double gapEnd = nextBound;
                        if (i + 1 < vec.size()) gapEnd = juce::jmin (gapEnd, vec[i + 1].start);
                        const double newDur = gapEnd - e.start;
                        if (newDur <= e.dur + 1e-6) continue;
                        NoteVal nv;
                        if (! durToVal (newDur, false, nv)) continue;   // the value gate
                        double srcLen = 0;
                        for (auto& h : e.heads)
                            if (h.src.track >= 0 && h.src.track < (int) src.tracks.size()
                                && h.src.note >= 0
                                && h.src.note < (int) src.tracks[(size_t) h.src.track].notes.size())
                                srcLen = juce::jmax (srcLen,
                                    src.tracks[(size_t) h.src.track].notes[(size_t) h.src.note].len);
                        const bool nearlyFull = srcLen >= 0.72 * newDur;
                        const bool genuineShort = e.dur < 0.5 * newDur - 1e-6;
                        if (! nearlyFull && ! genuineShort) continue;
                        e.dur = newDur; e.denom = nv.denom; e.dots = nv.dots;
                        if (! nearlyFull) e.artic |= 1;
                    }
                }
            // rest fill per measure
            for (int b = 0; b < numBars; ++b)
            {
                auto& M = st.measures[(size_t) b];
                auto& vec = M.v[v];
                std::sort (vec.begin(), vec.end(), [] (const Element& a, const Element& b) { return a.start < b.start; });
                if (v == 1 && vec.empty()) continue;         // silent second voice shows nothing
                std::vector<std::pair<double, double>> gaps;
                double cur = 0;
                for (auto& e : vec) { if (e.start > cur + 1e-6) gaps.push_back ({ cur, e.start }); cur = juce::jmax (cur, e.start + e.dur); }
                if (M.beats > cur + 1e-6) gaps.push_back ({ cur, M.beats });
                if (v == 1 || (st.isDrums && v == 1)) { if (! gaps.empty()) { gaps.erase (gaps.begin()); if (! gaps.empty()) gaps.pop_back(); } }
                detail::MeasureCtx ctx { M.beats, M.num, M.den, {}, nullptr };
                ctx.bounds.push_back (0);
                for (double gsz : M.groups) ctx.bounds.push_back (ctx.bounds.back() + gsz);
                std::vector<char> localTrip ((size_t) std::ceil (M.beats) + 1, 0);
                for (int lb = 0; lb < (int) localTrip.size(); ++lb)
                {
                    const int gb = (int) std::floor (M.startBeat + lb + 1e-6);
                    if (gb >= 0 && gb < (int) tripFlag.size()) localTrip[(size_t) lb] = tripFlag[(size_t) gb];
                }
                ctx.tripFlags = &localTrip;
                for (auto& g : gaps)
                    detail::spellSpan (ctx, g.first, g.second, true, 0, [&] (double s, double d, bool)
                    {
                        Element e;
                        e.start = s; e.dur = d; e.isRest = true; e.voice = v;
                        const int gBeat = (int) std::floor (M.startBeat + s + 1e-6);
                        e.triplet = gBeat >= 0 && gBeat < (int) tripFlag.size() && tripFlag[(size_t) gBeat]
                                    && d < 1.0 - 1e-6;
                        NoteVal nv { 4, 0 };
                        durToVal (d, e.triplet, nv);
                        e.denom = nv.denom; e.dots = nv.dots;
                        e.wholeMeasureRest = v == 0 && std::abs (s) < 1e-6 && std::abs (d - M.beats) < 1e-6;
                        if (e.wholeMeasureRest) { e.denom = 1; e.dots = 0; }
                        vec.push_back (std::move (e));
                    });
                std::sort (vec.begin(), vec.end(), [] (const Element& a, const Element& b)
                           { return a.start < b.start || (a.start == b.start && a.voice < b.voice); });
            }
        }

        // accidental state per measure (letter+octave), voices interleaved by time
        if (! st.isDrums)
            for (auto& M : st.measures)
            {
                std::map<int, int> state;   // absStep -> current alter
                std::vector<Element*> all;
                for (int v = 0; v < 2; ++v) for (auto& e : M.v[v]) all.push_back (&e);
                std::sort (all.begin(), all.end(), [] (const Element* a, const Element* b) { return a->start < b->start; });
                for (auto* e : all)
                    for (auto& h : e->heads)
                    {
                        const int abs = h.step + (st.clef == Clef::Bass ? 18 : 30);
                        const int letter = ((abs % 7) + 7) % 7;
                        const int base = keyAlter (mo.key, letter);
                        const int cur = state.count (abs) ? state[abs] : base;
                        if (e->tieTo) { state[abs] = h.alter; continue; }   // tied-in: no re-sign
                        if (h.alter != cur) { h.shownAcc = h.alter; state[abs] = h.alter; }
                    }
            }

        // 2nds cluster: adjacent steps alternate across the stem
        for (auto& M : st.measures)
            for (int v = 0; v < 2; ++v)
                for (auto& e : M.v[v])
                    for (size_t i = 1; i < e.heads.size(); ++i)
                        if (e.heads[i].step - e.heads[i - 1].step == 1 && ! e.heads[i - 1].otherSide)
                            e.heads[i].otherSide = true;

        // stems + beams per beat-group (pure-8th neighbours merge to half-bar in 4/4)
        for (auto& M : st.measures)
        {
            const bool twoVoices = ! M.v[0].empty() && ! M.v[1].empty();
            for (int v = 0; v < 2; ++v)
            {
                std::vector<double> bounds { 0.0 };
                for (double gsz : M.groups) bounds.push_back (bounds.back() + gsz);
                std::vector<std::vector<int>> groups;
                std::vector<int> cur;
                double curBoundEnd = bounds.size() > 1 ? bounds[1] : M.beats;
                size_t gi = 0;
                auto flush = [&groups, &cur] { if (cur.size() > 1) groups.push_back (cur); cur.clear(); };
                for (int i = 0; i < (int) M.v[v].size(); ++i)
                {
                    auto& e = M.v[v][(size_t) i];
                    while (e.start >= curBoundEnd - 1e-6 && gi + 2 < bounds.size())
                    { flush(); ++gi; curBoundEnd = bounds[gi + 1]; }
                    if (e.isRest || e.denom < 8) { flush(); continue; }
                    if (! cur.empty() && M.v[v][(size_t) cur.back()].triplet != e.triplet) flush();
                    cur.push_back (i);
                }
                flush();
                // merge neighbouring all-8th beat groups at odd->even beat pairs (4/4 look)
                if (M.num == 4 && M.den == 4)
                    for (size_t a = 0; a + 1 < groups.size(); ++a)
                    {
                        auto pure8 = [&M, v] (const std::vector<int>& g)
                        { for (int i : g) if (M.v[v][(size_t) i].denom != 8 || M.v[v][(size_t) i].triplet) return false; return true; };
                        const auto& A = groups[a]; const auto& B = groups[a + 1];
                        const double aStart = M.v[v][(size_t) A.front()].start;
                        const double bEnd = M.v[v][(size_t) B.back()].start + M.v[v][(size_t) B.back()].dur;
                        if (pure8 (A) && pure8 (B)
                            && ((aStart >= -1e-6 && bEnd <= 2.0 + 1e-6) || (aStart >= 2.0 - 1e-6 && bEnd <= 4.0 + 1e-6)))
                        {
                            groups[a].insert (groups[a].end(), B.begin(), B.end());
                            groups.erase (groups.begin() + (long) a + 1);
                            --a;
                        }
                    }
                for (auto& g : groups)
                {
                    Measure::Beam bm; bm.voice = v; bm.idx = g;
                    for (int i : g) M.v[v][(size_t) i].beamGroup = (int) M.beams.size();
                    M.beams.push_back (bm);
                }
                // stem directions
                for (auto& e : M.v[v])
                {
                    if (e.isRest || e.heads.empty()) continue;
                    if (st.isDrums)      e.stemUp = v == 0;
                    else if (twoVoices)  e.stemUp = v == 0;
                    else
                    {
                        int far = e.heads.front().step;
                        for (auto& h : e.heads) if (std::abs (h.step - 4) > std::abs (far - 4)) far = h.step;
                        e.stemUp = far < 4;
                    }
                }
                // beam group: one direction (majority of farthest heads)
                for (auto& bm : M.beams)
                {
                    if (bm.voice != v) continue;
                    if (st.isDrums || twoVoices) continue;
                    int up = 0, dn = 0;
                    for (int i : bm.idx) (M.v[v][(size_t) i].stemUp ? up : dn)++;
                    const bool u = up >= dn;
                    for (int i : bm.idx) M.v[v][(size_t) i].stemUp = u;
                }
            }
        }

        // columns (per staff for now; score-wide union happens in the layout pass)
        for (auto& M : st.measures)
        {
            std::set<long> cs;
            for (int v = 0; v < 2; ++v) for (auto& e : M.v[v]) cs.insert (std::lround (e.start * 5040));
            if (cs.empty()) cs.insert (0);
            M.colBeats.clear();
            for (long c : cs) M.colBeats.push_back ((double) c / 5040.0);
        }

        // vertical extent
        st.loStep = 0; st.hiStep = 8;
        for (auto& M : st.measures)
            for (int v = 0; v < 2; ++v)
                for (auto& e : M.v[v])
                    for (auto& h : e.heads)
                    { st.loStep = juce::jmin (st.loStep, h.step - 2); st.hiStep = juce::jmax (st.hiStep, h.step + 2); }

        // THE MARKS PASS: velocities become engraved dynamics + articulation.
        // Accents on real spikes (any staff); dynamic letters at phrase starts and
        // hairpins on sustained trends (melodic staves — kit dynamics live in the
        // heads' velocity shading). Conservative thresholds: a mark must EARN print.
        {
            struct Ev { double gs, ge; float vel; Element* el; };
            std::vector<Ev> evs;
            for (auto& M : st.measures)
                for (int v = 0; v < 2; ++v)
                    for (auto& e : M.v[v])
                        if (! e.isRest && ! e.heads.empty() && ! e.tieTo)
                        {
                            float mv = 0;
                            for (auto& h : e.heads) mv = juce::jmax (mv, h.vel);
                            evs.push_back ({ M.startBeat + e.start, M.startBeat + e.start + e.dur, mv, &e });
                        }
            std::sort (evs.begin(), evs.end(), [] (const Ev& a, const Ev& b) { return a.gs < b.gs; });
            std::vector<float> ring;
            for (auto& ev : evs)
            {
                if (ring.size() >= 6)
                {
                    float mean = 0;
                    for (float r2 : ring) mean += r2;
                    mean /= (float) ring.size();
                    if (ev.vel >= mean * 1.3f && ev.vel >= 0.85f) ev.el->artic |= 2;
                }
                ring.push_back (ev.vel);
                if (ring.size() > 8) ring.erase (ring.begin());
            }
            if (! st.isDrums && evs.size() >= 3)
            {
                auto level = [] (float v2)
                { return v2 < 0.30f ? 0 : v2 < 0.45f ? 1 : v2 < 0.58f ? 2 : v2 < 0.72f ? 3 : v2 < 0.86f ? 4 : 5; };
                int lastLevel = -1;
                size_t i = 0;
                while (i < evs.size())
                {
                    size_t j = i;                        // phrase = notes within 2-beat gaps
                    while (j + 1 < evs.size() && evs[j + 1].gs - evs[j].ge < 2.0) ++j;
                    float pv = 0; int pn = 0;
                    for (size_t k = i; k <= juce::jmin (i + 2, j); ++k) { pv += evs[k].vel; ++pn; }
                    const int lv = level (pv / (float) juce::jmax (1, pn));
                    if (lv != lastLevel) { st.dyns.push_back ({ evs[i].gs, lv }); lastLevel = lv; }
                    auto trend = [&] (bool up)           // monotonic-ish runs -> hairpins
                    {
                        int emitted = 0;
                        size_t r0 = i;
                        for (size_t k = i; k <= j && emitted < 2; ++k)
                        {
                            const bool keeps = k == r0
                                || (up ? evs[k].vel >= evs[k - 1].vel - 0.03f
                                       : evs[k].vel <= evs[k - 1].vel + 0.03f);
                            if (keeps && k != j) continue;
                            const size_t rEnd = keeps ? k : k - 1;
                            const float dv = evs[rEnd].vel - evs[r0].vel;
                            const double span = evs[rEnd].gs - evs[r0].gs;
                            if ((up ? dv >= 0.18f : dv <= -0.18f) && span >= 2.0)
                            {
                                st.hairs.push_back ({ evs[r0].gs, evs[rEnd].gs, up });
                                const int lv2 = level (evs[rEnd].vel);
                                if (lv2 != lastLevel)
                                { st.dyns.push_back ({ evs[rEnd].gs + 0.001, lv2 }); lastLevel = lv2; }
                                ++emitted;
                            }
                            r0 = k;
                        }
                    };
                    trend (true);
                    trend (false);
                    i = j + 1;
                }
            }
        }

        // removed-note strikes (proposal overlay)
        if (opt.removedNotes != nullptr)
            for (int ti : tracks)
                if (opt.removedNotes->count (ti))
                    for (auto& n : opt.removedNotes->at (ti))
                    {
                        GhostStrike gsk;
                        gsk.measure = barIndexAt (n.start);
                        gsk.start = n.start - bars[(size_t) juce::jlimit (0, numBars - 1, gsk.measure)].start;
                        if (st.isDrums)
                            gsk.step = drumStep (roleForTrack (src.tracks[(size_t) ti]));
                        else
                            gsk.step = spellPitch (n.pitch, mo.key).absStep - (st.clef == Clef::Bass ? 18 : 30);
                        st.strikes.push_back (gsk);
                    }
    }

    // ---- song furniture
    for (auto& c : src.chords)
    {
        const int m = juce::jlimit (0, juce::jmax (0, numBars - 1), (int) std::lround (c.bar) - 1);
        if (c.label.isNotEmpty()) mo.chords.push_back ({ m, c.label });
    }
    for (auto& s : src.sections)
        mo.sections.push_back ({ juce::jlimit (0, juce::jmax (0, numBars - 1), (int) s.startBar), s.name });
    mo.tempos.push_back ({ 0, song.bpm });
    for (auto& tp : src.tempoMap)
        if (tp.bar > 1e-9)
            mo.tempos.push_back ({ juce::jlimit (0, numBars - 1, (int) tp.bar), tp.bpm });

    // lyrics ride the sung staff when the song carries them ({beat,text} tolerant walk)
    if (auto* obj = src.extras.getDynamicObject())
    {
        auto grab = [&mo] (const juce::var& arr)
        {
            if (auto* a = arr.getArray())
                for (auto& it : *a)
                    if (auto* o = it.getDynamicObject())
                        if (o->hasProperty ("beat") && o->hasProperty ("text"))
                            mo.lyrics.push_back ({ (double) o->getProperty ("beat"),
                                                   o->getProperty ("text").toString() });
        };
        const auto ly = obj->getProperty ("lyrics");
        grab (ly);
        if (auto* a = ly.getArray())
            for (auto& sec : *a)
                if (auto* o = sec.getDynamicObject())
                    grab (o->getProperty ("words"));
        if (! mo.lyrics.empty())
            for (int si = 0; si < (int) mo.staves.size(); ++si)
            {
                const auto nm = mo.staves[(size_t) si].name.toLowerCase();
                if (nm.contains ("vocal") || nm.contains ("vox") || nm.contains ("voice") || nm.contains ("sing"))
                { mo.lyricStaff = si; break; }
            }
    }

    mo.quant = opt.quant > 0.0 ? opt.quant : 0.25;
    return mo;
}

//============================================================== proof: the census
// machine-checkable invariants for tools/score_battery.py (via m1 score-probe)
inline juce::var census (const Model& mo)
{
    auto* root = new juce::DynamicObject();
    juce::StringArray violations;
    int elements = 0, rests = 0, ties = 0, beams = 0, accidentals = 0, triplets = 0, ghosts = 0;
    int notes = 0, dynamics = 0, hairpins = 0, artics = 0;
    juce::Array<juce::var> staves;
    for (auto& st : mo.staves)
    {
        dynamics += (int) st.dyns.size();
        hairpins += (int) st.hairs.size();
        auto* so = new juce::DynamicObject();
        so->setProperty ("name", st.name);
        so->setProperty ("clef", st.clef == Clef::Treble ? "treble" : st.clef == Clef::Bass ? "bass" : "perc");
        so->setProperty ("drums", st.isDrums);
        so->setProperty ("measures", (int) st.measures.size());
        int mi = 0;
        for (auto& M : st.measures)
        {
            for (int v = 0; v < 2; ++v)
            {
                double sum = 0, cursor = -1;
                for (auto& e : M.v[v])
                {
                    ++elements;
                    if (e.isRest) ++rests; else ++notes;
                    if (e.tieFrom) ++ties;
                    if (e.triplet) ++triplets;
                    if (e.artic != 0) ++artics;
                    NoteVal nv;
                    if (! e.wholeMeasureRest && ! durToVal (e.dur, e.triplet, nv))
                        violations.add (st.name + " m" + juce::String (mi) + " v" + juce::String (v)
                                        + ": unspellable dur " + juce::String (e.dur, 4));
                    if (e.start < cursor - 1e-6)
                        violations.add (st.name + " m" + juce::String (mi) + " v" + juce::String (v) + ": overlap at "
                                        + juce::String (e.start, 3));
                    cursor = e.start + e.dur;
                    sum += e.dur;
                    for (auto& h : e.heads)
                    {
                        if (h.shownAcc != -9) ++accidentals;
                        if (h.ghostAdd) ++ghosts;
                    }
                    if (e.start + e.dur > M.beats + 1e-5)
                        violations.add (st.name + " m" + juce::String (mi) + ": element spills the bar");
                }
                if (v == 0 && ! M.v[0].empty() && std::abs (sum - M.beats) > 1e-5)
                    violations.add (st.name + " m" + juce::String (mi) + " v0: fills "
                                    + juce::String (sum, 4) + " of " + juce::String (M.beats, 2));
            }
            beams += (int) M.beams.size();
            for (auto& bm : M.beams)
                for (int i : bm.idx)
                    if (M.v[bm.voice][(size_t) i].isRest || M.v[bm.voice][(size_t) i].denom < 8)
                        violations.add (st.name + " m" + juce::String (mi) + ": beam over rest/long value");
            ++mi;
        }
        staves.add (juce::var (so));
    }
    root->setProperty ("staves", staves);
    root->setProperty ("numMeasures", mo.numMeasures);
    root->setProperty ("key", mo.key.label);
    root->setProperty ("fifths", mo.key.fifths);
    root->setProperty ("minor", mo.key.minor);
    root->setProperty ("elements", elements);
    root->setProperty ("rests", rests);
    root->setProperty ("ties", ties);
    root->setProperty ("beams", beams);
    root->setProperty ("accidentals", accidentals);
    root->setProperty ("triplets", triplets);
    root->setProperty ("ghostAdds", ghosts);
    root->setProperty ("notes", notes);
    root->setProperty ("dynamics", dynamics);
    root->setProperty ("hairpins", hairpins);
    root->setProperty ("artics", artics);
    root->setProperty ("chords", (int) mo.chords.size());
    root->setProperty ("sections", (int) mo.sections.size());
    root->setProperty ("lyrics", (int) mo.lyrics.size());
    juce::Array<juce::var> viol;
    for (auto& v : violations) viol.add (v);
    root->setProperty ("violations", viol);
    return juce::var (root);
}

} // namespace score
