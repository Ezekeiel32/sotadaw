#!/usr/bin/env python3
"""DOCTOR C5 battery — the harmony-clash law is conservative and correct.

A planted b9-class fight flags; consonant writing, a single blue note,
low-confidence votes, and drum lanes never do.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from doctor import diagnose

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


def base_song(lead_pitches, conf=0.9, lead_name="lead", chord="C", lens=None):
    """4 bars of C major pad + a lead placing lead_pitches on beats 1/3."""
    song = {"key": "C major", "bpm": 120, "lengthBars": 4,
            "chords": [{"bar": b + 1, "chord": chord, "conf": conf} for b in range(4)],
            "sections": [{"name": "a", "startBar": 0}, {"name": "b", "startBar": 2}],
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [{"name": "keys", "notes": [], "fx": []},
                       {"name": "bass", "notes": [], "fx": []},
                       {"name": lead_name, "notes": [], "fx": []}]}
    for b in range(4):
        for p in (60, 64, 67):
            song["tracks"][0]["notes"].append({"start": b * 4.0, "len": 3.9, "pitch": p, "vel": 0.8})
        song["tracks"][1]["notes"].append({"start": b * 4.0, "len": 3.5, "pitch": 36, "vel": 0.9})
    for i, p in enumerate(lead_pitches):
        ln = (lens[i] if lens else 1.0)
        song["tracks"][2]["notes"].append({"start": (i // 2) * 4.0 + (i % 2) * 2.0,
                                           "len": ln, "pitch": p, "vel": 0.85})
    return song


def c5(issues):
    return [i for i in issues if i[0] == "C5"]


# 8 strong-beat notes, 4 of them Db (b9 against C) — a pattern, must flag
clashy = base_song([61, 60, 61, 64, 61, 67, 61, 60])
hits = c5(diagnose(clashy))
ok(len(hits) == 1 and "lead" in hits[0][1] and "suggest_chords" in hits[0][2],
   "planted b9 pattern (4/8 strong beats on Db over C) flags with the fix line")

clean = base_song([60, 64, 67, 72, 64, 60, 67, 64])
ok(not c5(diagnose(clean)), "consonant chord-tone lead stays silent")

blue = base_song([60, 64, 61, 67, 64, 60, 72, 64])
ok(not c5(diagnose(blue)), "a single blue note is never a pattern (1/8 < gates)")

shaky = base_song([61, 60, 61, 64, 61, 67, 61, 60], conf=0.3)
ok(not c5(diagnose(shaky)), "low-confidence chord votes never ground a clash claim")

drums = base_song([61, 60, 61, 64, 61, 67, 61, 60], lead_name="perc_top")
ok(not c5(diagnose(drums)), "drum-named lanes are exempt (pitches are drum-map slots)")

short = base_song([61, 60, 61, 64, 61, 67, 61, 60], lens=[0.25] * 8)
ok(not c5(diagnose(short)), "short passing hits (<0.5 beats) never count as sustained clashes")

scale = base_song([62, 60, 65, 64, 62, 67, 65, 60])
ok(not c5(diagnose(scale)), "in-scale non-chord tones (D, F over C) are taste, not clashes")

print(f"PASS {N}/{N} doctor C5 battery")
