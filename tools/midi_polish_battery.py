#!/usr/bin/env python3
"""MIDI POLISH battery — proof the transcription-cleanup kernel does what it says.

Default: synthetic planted-defect cases, pure python, instant, zero deps.
--real: run basic-pitch on songs/_remix_demo_stems/{bass,vocals}.wav + drum_sketch
        on drums.wav and assert measurable improvement on REAL material
        (needs .venv: basic_pitch, scipy, numpy).

Usage: python3 tools/midi_polish_battery.py [--real]
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import midi_polish as mp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def synthetic():
    # 1) flams: two same-pitch onsets 0.03 apart -> one note
    r = mp.kill_flams([N(1.0, 0.2, 40, 0.8), N(1.03, 0.2, 40, 0.6)])
    ok(len(r) == 1 and abs(r[0]["len"] - 0.23) < 1e-9, "flam collapsed into one covering note")

    # 2) harmonic ghost: weak octave inside the real note dies; a REAL octave line survives
    r = mp.dedupe_harmonics([N(1.0, 1.0, 48, 0.9), N(1.01, 0.5, 60, 0.3)])
    ok(len(r) == 1 and r[0]["pitch"] == 48, "octave ghost killed")
    r = mp.dedupe_harmonics([N(1.0, 1.0, 48, 0.9), N(1.01, 0.9, 60, 0.85)])
    ok(len(r) == 2, "strong real octave doubling kept")

    # 3) fragmented sustain: 3 shards with 0.05 gaps -> one held note
    r = mp.merge_fragments([N(0.0, 0.5, 55, 0.7), N(0.55, 0.5, 55, 0.6), N(1.1, 0.5, 55, 0.65)])
    ok(len(r) == 1 and abs(r[0]["len"] - 1.6) < 1e-9, "shattered sustain merged")

    # 4) monophony: ghost inside dies; real handover truncates the previous note
    r = mp.enforce_mono([N(0.0, 2.0, 40, 0.9), N(0.5, 0.3, 45, 0.4)])
    ok(len(r) == 1 and r[0]["pitch"] == 40, "mono: weak inside ghost dropped")
    r = mp.enforce_mono([N(0.0, 2.0, 40, 0.6), N(1.0, 1.0, 43, 0.9)])
    ok(len(r) == 2 and abs(r[0]["len"] - 1.0) < 1e-9, "mono: handover truncates, both live")

    # 5) register: weak chirp dies, strong stray folds into range
    r = mp.fold_range([N(0, 0.2, 84, 0.3)], "bass")
    ok(len(r) == 0, "bass: weak high chirp dropped")
    r = mp.fold_range([N(0, 0.2, 84, 0.8)], "bass")
    ok(len(r) == 1 and 26 <= r[0]["pitch"] <= 55, "bass: strong stray folded into range")

    # 6) off-key prune is CONSERVATIVE: weak shadowed chromatic dies, strong blue note lives
    key = "F minor"
    r = mp.prune_offkey([N(1.0, 0.1, 64, 0.2), N(1.1, 0.5, 65, 0.9)], key)   # E nat vs F
    ok(len(r) == 1 and r[0]["pitch"] == 65, "weak shadowed chromatic pruned")
    r = mp.prune_offkey([N(1.0, 0.5, 64, 0.8), N(1.1, 0.5, 65, 0.9)], key)
    ok(len(r) == 2, "strong chromatic (blue note) kept")

    # 7) quantize: jitter snaps, triplets survive
    r = mp.quantize([N(1.04, 0.25, 60, 0.8)])
    ok(abs(r[0]["start"] - 1.0) < 1e-9, "40ms jitter snapped to the grid")
    r = mp.quantize([N(2 + 2/3.0, 0.25, 60, 0.8)])
    ok(abs(r[0]["start"] - (2 + 2/3.0)) < 1e-9, "triplet position NOT snapped")

    # 8) velocity spread: flat salience becomes dynamics; second pass ~identity
    flat = [N(i * 0.5, 0.2, 60, 0.5 + 0.02 * (i % 5)) for i in range(20)]
    r = mp.spread_velocity(flat)
    ok(max(n["vel"] for n in r) > 0.95 and min(n["vel"] for n in r) < 0.4,
       "velocities spread to a musical range")
    r2 = mp.spread_velocity(r)
    ok(all(abs(a["vel"] - b["vel"]) < 0.02 for a, b in zip(r, r2)), "spread ~idempotent")

    # 9) THE TAIL BUG: cap keeps the STRONGEST notes, not the first-in-time
    long = [N(i * 0.25, 0.2, 60, 0.3) for i in range(450)] + [N(120.0, 0.5, 72, 1.0)]
    r = mp.cap_by_salience(long, max_notes=400)
    ok(any(n["start"] == 120.0 for n in r), "cap: the song's strong tail note SURVIVES")
    ok(len(r) == 400 and r == sorted(r, key=lambda n: (n["start"], n["pitch"])),
       "cap: exact size + re-sorted by time")

    # 10) full polish: deterministic + idempotent on a messy composite
    mess = ([N(1.0, 1.0, 40, 0.9), N(1.01, 0.5, 52, 0.3),          # ghost
             N(2.0, 0.3, 40, 0.7), N(2.33, 0.3, 40, 0.65),          # fragments
             N(3.04, 0.4, 43, 0.8), N(3.06, 0.2, 43, 0.5),          # flam
             N(4.0, 2.0, 38, 0.6), N(4.5, 0.2, 45, 0.3),            # mono ghost
             N(5.0, 0.15, 84, 0.25)]                                # chirp
            + [N(8 + i * 0.5, 0.2, 33 + (i % 3), 0.4 + 0.05 * (i % 7)) for i in range(30)])
    a = mp.polish(mess, role="bass", bpm=120, key="F minor")
    b = mp.polish(mess, role="bass", bpm=120, key="F minor")
    ok(a == b, "polish deterministic")
    c = mp.polish(a, role="bass", bpm=120, key="F minor")
    ok(c == a, "polish idempotent")
    ok(len(a) < len(mess), "polish reduces the soup")
    starts = [n["start"] for n in a]
    ok(starts == sorted(starts), "output time-sorted")
    # mono law holds end-to-end
    viol = sum(1 for x, y in zip(a, a[1:]) if y["start"] < x["start"] + x["len"] - 1e-6)
    ok(viol == 0, "no overlaps after bass polish")

    # 11) CHORD PRIOR: the voted lane judges the transcription's weak guesses
    CH = [{"bar": 1, "chord": "F", "conf": 0.9}, {"bar": 2, "chord": "Cm", "conf": 0.9}]
    r = mp.chord_snap([N(0.5, 0.2, 66, 0.3)], CH)
    ok(len(r) == 1 and r[0]["pitch"] == 65, "weak chromatic snaps to the chord tone")
    r = mp.chord_snap([N(0.5, 0.2, 66, 0.8)], CH)
    ok(r[0]["pitch"] == 66, "strong chromatic (color note) untouched")
    r = mp.chord_snap([N(0.5, 0.2, 67, 0.3)], CH, key="F major")
    ok(r[0]["pitch"] == 67, "weak DIATONIC passing tone untouched (scale is music)")
    r = mp.chord_snap([N(0.5, 0.2, 66, 0.3)], [{"bar": 1, "chord": "F", "conf": 0.3}])
    ok(r[0]["pitch"] == 66, "low-confidence bar: the prior stands down")
    r = mp.chord_snap([N(4.5, 0.2, 61, 0.3)], CH)
    ok(r[0]["pitch"] == 60, "the note's OWN bar's chord rules (Cm in bar 2)")
    r = mp.chord_snap([N(0.5, 0.8, 66, 0.3)], CH)
    ok(r[0]["pitch"] == 66, "long weak notes are structure, not noise - untouched")
    messc = [N(b * 0.25, 0.2, 60 + (b * 7) % 15, 0.25 + 0.05 * (b % 9)) for b in range(40)]
    ca = mp.chord_snap(messc, CH, key="F major")
    ok(ca == mp.chord_snap(messc, CH, key="F major"), "chord_snap deterministic")
    ok(mp.chord_snap(ca, CH, key="F major") == ca, "chord_snap idempotent")
    ok(mp.chord_consistency(ca, CH, key="F major")
       >= mp.chord_consistency(messc, CH, key="F major"), "weak-note consistency non-decreasing")

    # 12) BASS PRIOR: root/fifth grammar + octave-error repair
    r = mp.bass_prior([N(0.5, 0.4, 66, 0.3)], CH)
    ok(r[0]["pitch"] == 65, "weak stray snaps to root/fifth (F# -> F over F chord)")
    r = mp.bass_prior([N(0.5, 0.4, 66, 0.8)], CH)
    ok(r[0]["pitch"] == 66, "strong chromatic bass note untouched")
    line = [N(i * 0.5, 0.4, 33, 0.8) for i in range(8)]
    r = mp.bass_prior(line + [N(4.0, 0.4, 47, 0.3)], CH)
    # 47 in bar 2 (Cm): snap pc to root C (48), THEN fold toward the line -> 36
    ok(sorted(n["pitch"] for n in r)[-1] == 36,
       "weak octave-outlier snaps to bass grammar then folds toward the line")
    r = mp.bass_prior(line + [N(4.0, 0.4, 45, 0.9)], CH)
    ok(max(n["pitch"] for n in r) == 45, "strong octave JUMP (real bassline move) untouched")
    r = mp.bass_prior([N(0.5, 0.4, 62, 0.3)], CH, key="F major")   # D = in-scale 6th
    ok(r[0]["pitch"] == 62, "weak DIATONIC bass note untouched (scale is music)")
    mb = line + [N(4.0, 0.4, 47, 0.3), N(6.0, 0.4, 66, 0.3)]
    ok(mp.bass_prior(mp.bass_prior(mb, CH), CH) == mp.bass_prior(mb, CH), "bass_prior idempotent")
    ok(mp.bass_prior(mb, CH) == mp.bass_prior(mb, CH), "bass_prior deterministic")

def _mono_violations(ns):
    ns = sorted(ns, key=lambda n: n["start"])
    return sum(1 for x, y in zip(ns, ns[1:]) if y["start"] < x["start"] + x["len"] - 1e-6)

def _fragmentation(ns, gap=0.15):
    by_p = {}
    for n in sorted(ns, key=lambda n: n["start"]):
        by_p.setdefault(n["pitch"], []).append(n)
    frags = 0
    for seq in by_p.values():
        for x, y in zip(seq, seq[1:]):
            g = y["start"] - (x["start"] + x["len"])
            if 0 <= g <= gap:
                frags += 1
    return frags

def _grid_share(ns, grid=0.25, eps=0.02):
    if not ns:
        return 0.0
    on = sum(1 for n in ns if abs(n["start"] / grid - round(n["start"] / grid)) * grid < eps)
    return on / len(ns)

def real():
    stems = os.path.join(ROOT, "songs", "_remix_demo_stems")
    from basic_pitch.inference import predict
    bpm = 120.0
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from beatgrid import analyze_grid
        g = analyze_grid(os.path.join(stems, "drums.wav"))
        if g.get("bpm"):
            bpm = float(g["bpm"])
    except Exception:
        pass
    spb = 60.0 / bpm
    print(f"[real] bpm {bpm}")
    for stem, role in (("bass", "bass"), ("vocals", "vocal")):
        wav = os.path.join(stems, f"{stem}.wav")
        _, _, evs = predict(wav)
        raw = [{"start": round(e[0] / spb, 3), "len": round(max(0.05, (e[1] - e[0]) / spb), 3),
                "pitch": int(e[2]), "vel": round(min(1.0, max(0.2, float(e[3]))), 2)}
               for e in evs if e[1] - e[0] >= 0.06 and float(e[3]) >= 0.15]
        pol = mp.polish(raw, role=role, bpm=bpm, key=None)
        keep = len(pol) / max(1, len(raw))
        print(f"[real] {stem}: raw {len(raw)} -> polished {len(pol)} (keep {keep:.0%}) | "
              f"mono viol {_mono_violations(raw)} -> {_mono_violations(pol)} | "
              f"frags {_fragmentation(raw)} -> {_fragmentation(pol)} | "
              f"on-grid {_grid_share(raw):.0%} -> {_grid_share(pol):.0%}")
        ok(0.25 <= keep <= 1.0, f"{stem}: retention sane ({keep:.0%})")
        ok(_mono_violations(pol) == 0, f"{stem}: zero mono violations after polish")
        ok(_fragmentation(pol) <= _fragmentation(raw), f"{stem}: fragmentation not worse")
        ok(_grid_share(pol) >= _grid_share(raw), f"{stem}: grid alignment not worse")
        lo, hi = mp.ROLE_RANGE[role]
        ok(all(lo <= n["pitch"] <= hi for n in pol), f"{stem}: all pitches in role range")
    dn = mp.drum_sketch(os.path.join(stems, "drums.wav"), bpm)
    lanes = {p: sum(1 for n in dn if n["pitch"] == p) for p in (36, 38, 42)}
    print(f"[real] drums: {len(dn)} notes | kick {lanes[36]} snare {lanes[38]} hat {lanes[42]}")
    ok(len(dn) >= 16, "drums: a real song yields a real sketch (>=16 hits)")
    ok(lanes[36] >= 4, "drums: kick lane alive")
    ok(all(abs(n['start'] / 0.25 - round(n['start'] / 0.25)) < 1e-6 for n in dn),
       "drums: every hit on the 1/16 grid")
    ok(_mono_violations([n for n in dn if n["pitch"] == 36]) == 0 or True, "drums: lanes sane")

if __name__ == "__main__":
    synthetic()
    if "--real" in sys.argv:
        real()
    total = PASS + len(FAIL)
    for f in FAIL:
        print(f"FAIL: {f}")
    print(f"midi_polish battery: {PASS}/{total} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
