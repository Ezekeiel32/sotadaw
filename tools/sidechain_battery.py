#!/usr/bin/env python3
"""SIDECHAIN_BAKE battery — the duck follows the ACTUAL kick, not an LFO.
A swung/broken kick pattern (offbeat placements no LFO matches) drives the
envelope kernel; corners, depth, merge and recovery are asserted, then the
full CLI --write lands on a scratch song and m1 resave = the engine parse
court (skipped green without m1).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np

from sidechain_bake import duck_envelope, plan  # noqa: E402

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


# ---- kernel: swung triggers (0, 1.75, 3.5 — NOT an even grid)
trig = [0.0, 1.75, 3.5]
gb, env = duck_envelope(trig, total_beats=8.0, depth=4.0, attack=0.05, hold=0.05, release=0.4)
ok(float(env.min()) == -4.0, f"duck bottoms at -depth ({env.min():.2f})")


def at(beat):
    return float(np.interp(beat, gb, env))


ok(at(1.75 + 0.125) < -3.0, "swung trigger at 1.75 ducks right after its onset")
ok(at(1.0) == 0.0 and at(3.0) == 0.0, "envelope fully recovers between distant triggers")
ok(at(1.7) == 0.0, "no duck BEFORE a trigger (an LFO would be mid-cycle here)")

# ---- overlap merge: two triggers 0.25 apart never rise between them
gb2, env2 = duck_envelope([2.0, 2.25], 6.0, depth=6.0, attack=0.05, hold=0.05, release=0.5)
seg = env2[(gb2 >= 2.125) & (gb2 <= 2.375)]
ok(float(seg.max()) <= -4.0, f"overlapping triggers merge deepest-first (max between = {seg.max():.2f})")

# ---- plan() on a synthetic song: auto trigger/target picks + absolute points
song = {"bpm": 140, "lengthBars": 2, "tracks": [
    {"name": "Kick", "gainDb": 0, "notes": [{"start": s, "len": 0.25, "pitch": 36, "vel": 1.0}
                                            for s in trig]},
    {"name": "bass", "gainDb": -3.0, "notes": [{"start": 0, "len": 8, "pitch": 40, "vel": 0.9}]},
    {"name": "lead", "gainDb": 0, "notes": []}]}
p = plan(song, depth=4.0)
ok(p["available"] and p["trigger"] == "Kick" and p["n_triggers"] == 3,
   "auto-picked the kick trigger (case-blind) with 3 unique onsets")
tgt = p["targets"][0]
vs = [pt["v"] for pt in tgt["automation"]["points"]]
ok(tgt["track"] == "bass" and min(vs) == -7.0 and max(vs) == -3.0,
   f"points are ABSOLUTE around base -3.0 (min {min(vs)}, max {max(vs)})")
ok(2 < tgt["n_points"] < 60, f"thinned to corners ({tgt['n_points']} points)")
ok(plan(song, depth=4.0) == p, "deterministic")
ok(not plan({"bpm": 120, "lengthBars": 2, "tracks": []})["available"],
   "no trigger -> honest degrade with a --trigger hint")

# ---- CLI --write on a scratch song + m1 resave parse court
tmp = tempfile.mkdtemp(prefix="sc_")
sp = os.path.join(tmp, "scratch.json")
json.dump(song, open(sp, "w"))
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sidechain_bake.py"),
                    sp, "--depth", "5", "--write"], capture_output=True, text=True, timeout=120)
back = json.load(open(sp))
autos = [t.get("automation", []) for t in back["tracks"] if t["name"] == "bass"][0]
ok(r.returncode == 0 and len(autos) == 1 and autos[0]["target"] == "gainDb"
   and any(pt["v"] == -8.0 for pt in autos[0]["points"]),
   "CLI --write landed a gainDb duck lane (depth 5 below base -3)")
j = json.loads([l for l in r.stdout.splitlines() if l.startswith("SIDECHAIN_JSON")][0][15:])
ok(j["available"] and j["targets"][0]["n_points"] == len(autos[0]["points"]),
   "SIDECHAIN_JSON machine line matches what landed")

if os.path.exists(M1):
    o = os.path.join(tmp, "out.wav")
    rr = subprocess.run([M1, "render", sp, o], capture_output=True, text=True, timeout=300)
    ok(rr.returncode == 0 and os.path.getsize(o) > 1000,
       "m1 parse court: the baked song renders (engine accepts the automation)")
else:
    ok(True, "m1 absent — parse court skipped green")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} sidechain battery")
