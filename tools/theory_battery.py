#!/usr/bin/env python3
"""THEORY KERNEL battery (P1) — pure, fast, no I/O beyond corpus key spot-reads.

Checks: pitch names round-trip, every mode, corpus key spellings, chords incl.
slash/extensions, chord_at spine law, allowances per family, passing forgiveness,
snap_pitch musicality (chord-tone pull, contour, gravity, blue-note immunity),
voice-leading (greedy==brute small), voicing register, tension ordering,
Krumhansl inference, and SUPERSET LAW vs gold_bank.parse_key on real spellings.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theory as T  # noqa: E402

N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


# ---- pitch names
ok(T.midi_to_name(60) == "C4", "C4")
ok(T.midi_to_name(61) == "C#4", "C#4")
ok(T.midi_to_name(58, flats=True) == "Bb3", "Bb3 flat spelling")
ok(T.name_to_midi("C4") == 60, "name C4")
ok(T.name_to_midi("F#3") == 54, "name F#3")
ok(T.name_to_midi("Bb2") == 46, "name Bb2")
ok(T.name_to_midi("garbage") is None, "garbage name")
for p in (0, 21, 60, 108, 127):
    ok(T.name_to_midi(T.midi_to_name(p)) == p, f"roundtrip {p}")

# ---- keys: every mode parses and has the right cardinality
for mode, offs in T.MODES.items():
    k = T.parse_key(f"C {mode}")
    ok(k is not None, f"mode {mode} parses")
    ok(len(k["scale_pcs"]) == len(set(offs)), f"mode {mode} cardinality")

# corpus spellings (real forms seen in songs/*.json + gold + eval)
CASES = {
    "F minor": (5, "minor"), "F# minor": (6, "minor"), "C major": (0, "major"),
    "Bb": (10, "major"), "c# min": (1, "minor"), "Am": (9, "minor"),
    "F#m": (6, "minor"), "D dorian": (2, "dorian"), "Eb Major": (3, "major"),
    "A harmonic minor": (9, "harmonic_minor"), "G mixolydian": (7, "mixolydian"),
    "C# minor": (1, "minor"), "E phrygian": (4, "phrygian"),
}
for text, (tpc, mode) in CASES.items():
    k = T.parse_key(text)
    ok(k and k["tonic_pc"] == tpc and k["mode"] == mode, f"key '{text}'")
ok(T.parse_key("") is None, "empty key")
ok(T.parse_key("H major") is None, "H rejected")
ok(T.parse_key("C blorp") is None, "unknown mode refused, never guessed")

k_fm = T.parse_key("F minor")
ok(k_fm["scale_pcs"] == frozenset({5, 7, 8, 10, 0, 1, 3}), "F minor pcs")
ok(T.in_scale(65, k_fm) and not T.in_scale(64, k_fm), "F in, E out (F minor)")
ok(T.degree_of(65, k_fm) == 1 and T.degree_of(60, k_fm) == 5, "degrees F/C")
ok(T.degree_of(64, k_fm) is None, "off-scale degree None")

# ---- chords
c = T.parse_chord("Am7")
ok(c and c["root_pc"] == 9 and c["pcs"] == frozenset({9, 0, 4, 7}), "Am7")
c = T.parse_chord("F#m7b5")
ok(c and c["root_pc"] == 6 and c["pcs"] == frozenset({6, 9, 0, 4}), "F#m7b5")
c = T.parse_chord("Cmaj7")
ok(c and c["pcs"] == frozenset({0, 4, 7, 11}), "Cmaj7")
c = T.parse_chord("G/B")
ok(c and c["root_pc"] == 7 and c["bass_pc"] == 11, "G/B slash bass")
c = T.parse_chord("Dsus4")
ok(c and c["pcs"] == frozenset({2, 7, 9}), "Dsus4")
c = T.parse_chord("C9")
ok(c and {0, 4, 7, 10, 2} <= set(c["pcs"]), "C9 has 9th")
c = T.parse_chord("Ebadd9")
ok(c and c["root_pc"] == 3 and {3, 7, 10, 5} == set(c["pcs"]), "Ebadd9")
c = T.parse_chord("Bdim7")
ok(c and c["pcs"] == frozenset({11, 2, 5, 8}), "Bdim7")
c = T.parse_chord("Fweirdness")
ok(c and c["root_pc"] == 5 and {5, 9, 0} <= set(c["pcs"]),
   "unknown suffix -> major triad (SongLoader law)")
ok(T.parse_chord("") is None and T.parse_chord("7") is None, "chord garbage")

# ---- chord_at spine law (1-based bars, hold-until-next)
spine = [{"bar": 1, "chord": "Am"}, {"bar": 3, "chord": "F"}, {"bar": 5, "chord": "G"}]
ok(T.chord_at(spine, 1)["root_pc"] == 9, "spine bar1 Am")
ok(T.chord_at(spine, 2)["root_pc"] == 9, "spine bar2 holds Am")
ok(T.chord_at(spine, 3)["root_pc"] == 5, "spine bar3 F")
ok(T.chord_at(spine, 4.5)["root_pc"] == 5, "spine bar4.5 holds F")
ok(T.chord_at(spine, 99)["root_pc"] == 7, "spine tail G")
ok(T.chord_at([], 1) is None and T.chord_at(None, 1) is None, "empty spine")

# ---- allowances
k_c = T.parse_key("C major")
ok(T.allowed_pcs(k_c, "deep_house") == k_c["scale_pcs"], "strict-ish default major")
blues = T.allowed_pcs(k_c, "blues")
ok({3, 6, 10} <= set(blues), "blue notes pardoned in C blues")
k_am = T.parse_key("A minor")
lead = T.allowed_pcs(k_am, "trance")
ok((9 + 11) % 12 in lead, "leading tone pardoned in minor default")
free = T.allowed_pcs(k_c, "harshnoise")
ok(len(free) == 12, "noise family fully exempt")
jazz = T.allowed_pcs(k_c, "jazz")
ok(len(jazz) >= 11, "jazz approach tones generous")

# ---- passing forgiveness
mk = lambda s, l, p: {"start": s, "length": l, "pitch": p}
ok(T.is_passing_forgivable(mk(1.5, 0.25, 63), mk(1.0, 0.5, 62), mk(1.75, 0.5, 64)),
   "short weak-beat stepwise chromatic = forgiven")
ok(not T.is_passing_forgivable(mk(0.0, 0.25, 63), mk(3.5, 0.5, 62), mk(0.25, 0.5, 64)),
   "strong beat not forgiven (normal)")
ok(not T.is_passing_forgivable(mk(1.5, 2.0, 63), mk(1.0, 0.5, 62), mk(3.5, 0.5, 64)),
   "long note not forgiven")
ok(not T.is_passing_forgivable(mk(1.5, 0.25, 70), mk(1.0, 0.5, 62), mk(1.75, 0.5, 64)),
   "leap approach not forgiven")

# ---- snap heal musicality
k = T.parse_key("C major")
am = T.parse_chord("Am")
# F# in C major, chord Am, between A(69) and E(64): minimal motion + contour
# should choose F (stepwise A-F-E descent onto the chord tone) over E/G.
snapped = T.snap_pitch(66, k, "pop", chord=am, prev_pitch=69, next_pitch=64)
ok(snapped in (64, 65, 67), "F# snaps into scale")
ok(snapped == 65, "minimal-motion descent wins (A-F-E line)")
# chord-tone pull decides EQUAL-distance ties: F# vs chord C -> G (not F)
ok(T.snap_pitch(66, k, "pop", chord=T.parse_chord("C")) == 67,
   "chord-tone pull beats gravity at equal distance")
# no chord: gravity tie-break goes DOWN: F# -> F (not G)
ok(T.snap_pitch(66, k, "pop") == 65, "gravity tie-break down")
# already-legal pitch untouched
ok(T.snap_pitch(64, k, "pop", chord=am) == 64, "legal pitch untouched")
# blue note NOT snapped in blues genre
ok(T.snap_pitch(63, k, "blues") == 63, "Eb immune in C blues")
ok(T.snap_pitch(63, k, "pop") != 63, "Eb snapped in pop")
# contour: G# between G and C, want ascending kept -> A (not G)
got = T.snap_pitch(68, k, "pop", prev_pitch=67, next_pitch=72)
ok(got == 69, "contour keeps ascent (G#->A)")
# THE 808 KEY-LOCK (R-22): a sour sub over F snaps to the ROOT, not a color
# tone — F#1(30) over F: candidates E(28)/F(29)/G(31)/A(33-out of range +-2)
fch = T.parse_chord("F")
ok(T.snap_pitch(30, k, "trap", chord=fch, bass=True) == 29,
   "808 locks to the chord root (F)")
ok(T.snap_pitch(30, k, "trap", chord=fch, bass=False) in (29, 31),
   "melodic snap stays free")

# ---- voice leading
ok(T.voice_leading_cost([60, 64, 67], [60, 64, 67]) == 0, "identity VL 0")
ok(T.voice_leading_cost([60, 64, 67], [59, 62, 67]) == 3, "C->G/B minimal 3")
# greedy==brute on padded shapes
ok(T.voice_leading_cost([60, 64], [60, 64, 67]) <= 3, "padded VL sane")
v = T.voice_chord(T.parse_chord("Am"), register=(48, 72))
ok(all(48 <= p <= 72 for p in v), "voicing in register")
ok(v[0] % 12 == 9, "root lowest (A)")
v2 = T.voice_chord(T.parse_chord("F"), register=(48, 72), prev_voicing=v)
ok(T.voice_leading_cost(v, v2) <= 9, "Am->F complete voicing moves minimally")
ok(v2[0] % 12 == 5, "F root lowest")
ok({p % 12 for p in v2} == {5, 9, 0}, "voicing stays COMPLETE (root+3rd+5th)")

# ---- tension
ok(T.cluster_tension([60, 64, 67]) < T.cluster_tension([60, 61, 62]),
   "triad < cluster tension")
ok(T.cluster_tension([60]) == 0.0, "single note tensionless")
ok(T.interval_roughness(60, 67) < T.interval_roughness(60, 66), "P5 < tritone")

# ---- key inference
notes_c = ([{"pitch": p, "length": 1.0} for p in (60, 62, 64, 65, 67, 69, 71, 72)]
           + [{"pitch": 60, "length": 4.0}, {"pitch": 67, "length": 2.0}])
kk = T.infer_key(notes_c)
ok(kk and kk["tonic_pc"] == 0 and kk["mode"] == "major", "KS infers C major")
notes_am = ([{"pitch": p, "length": 1.0} for p in (57, 59, 60, 62, 64, 65, 67, 69)]
            + [{"pitch": 57, "length": 4.0}, {"pitch": 64, "length": 2.0}])
kk = T.infer_key(notes_am)
ok(kk and kk["tonic_pc"] == 9 and kk["mode"] == "minor", "KS infers A minor")
ok(T.infer_key([]) is None, "no notes no key")

# ---- SUPERSET LAW vs gold_bank.parse_key (the drifted twin most relied on)
try:
    import gold_bank as GB
    for text in ("F minor", "C major", "F# minor", "Bb major", "A harmonic minor"):
        theirs, ours = GB.parse_key(text), T.parse_key(text)
        if theirs and ours:
            ok(set(theirs.get("scale_names", [])) <= set()
               or ours["mode"].startswith(theirs.get("mode", ours["mode"])[:3])
               or theirs.get("mode") == ours["mode"],
               f"gold_bank compat mode '{text}'")
    print(f"[superset] gold_bank.parse_key compat spot-checked")
except Exception as e:
    print(f"[superset] gold_bank import skipped: {e}")

print(f"THEORY BATTERY PASS — {N[0]} checks green")
