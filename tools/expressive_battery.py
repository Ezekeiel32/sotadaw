#!/usr/bin/env python3
"""EXPRESSIVE battery — verifies both metrics discriminate correctly + humanize
is musically safe + microtiming survives the render. Honest expectations: the
continuous score is sensitive to subtle humanize; NOMML is a coarse
performance-vs-score classifier. Exit 1 on any failure."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from expressive import expressiveness, nomml_level, humanize

FAIL = []
def check(n, c, d=""):
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))
    (None if c else FAIL.append(n))

mech = [{"start": i * 0.25, "len": 0.2, "pitch": 42, "vel": 0.8} for i in range(16)]

# --- continuous expressiveness score ---
check("expr: mechanical ~0", expressiveness(mech) < 1.0, f"{expressiveness(mech)}")
prev = -1
mono = True
for amt in (0.0, 0.4, 0.7, 1.0):
    e = expressiveness(humanize(mech, amt, 1))
    mono = mono and e >= prev
    prev = e
check("expr: rises monotonically with humanize amount", mono, "0->0.4->0.7->1.0")

# --- humanize safety ---
h = humanize(mech, 0.7, 1)
check("humanize: no note reorder", all(h[i]["start"] <= h[i + 1]["start"] + 1e-9 for i in range(len(h) - 1)))
check("humanize: velocities in (0,1]", all(0 < n["vel"] <= 1 for n in h))
check("humanize: deterministic per seed", h == humanize(mech, 0.7, 1))
check("humanize: seed varies", h != humanize(mech, 0.7, 9))
check("humanize: timing bounded < 16th", max(abs(h[i]["start"] - mech[i]["start"]) for i in range(len(mech))) < 0.25)

# --- NOMML classifier (coarse, performance-vs-score) ---
lm, cm = nomml_level(mech)
check("NOMML: dead grid -> mechanical", cm == "mechanical", f"level {lm}")
perf = [{"start": i * 0.25 + ((-1) ** i) * 0.05, "len": 0.2, "pitch": 42,
         "vel": 0.5 + 0.4 * (i % 4 == 0)} for i in range(16)]
lp, cp = nomml_level(perf)
check("NOMML: real off-grid performance -> expressive", cp == "expressive", f"level {lp}")
check("NOMML: discriminates perf > mechanical", lp > lm, f"{lp} > {lm}")
lt, _ = nomml_level([{"start": round(i / 3.0, 4), "len": 0.2, "pitch": 42, "vel": 0.8} for i in range(12)])
check("NOMML: triplets align (not max-level noise)", lt < 7, f"triplet level {lt}")

# --- microtiming survives the render: ROBUST single-note test (unambiguous onset).
# Render one on-grid note (start 1.0) and one off-grid (start 1.3 = +0.15s at 120bpm)
# SEPARATELY; the first-energy-sample gap must be ~0.15s, proving the engine plays
# the off-grid start exactly (not quantized to 1.0 or 1.25). Robust vs detector noise.
import json
import numpy as np, soundfile as sf
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
def onset_s(start_beat):
    s = {"version": 2, "bpm": 120, "lengthBars": 1, "masterGainDb": 0,
         "tracks": [{"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -3,
                     "notes": [{"start": start_beat, "len": 0.2, "pitch": 42, "vel": 1.0}]}]}
    tj = os.path.join(ROOT, "songs", "_exp_1n.json"); tw = os.path.join(ROOT, "songs", "_exp_1n.wav")
    json.dump(s, open(tj, "w"), indent=1)
    r = subprocess.run([M1, "render", tj, tw], capture_output=True, text=True, timeout=300)
    ok = "ok=1" in (r.stdout + r.stderr) and os.path.exists(tw)
    t = None
    if ok:
        x = np.abs(sf.read(tw, always_2d=True)[0].mean(axis=1)); sr = sf.info(tw).samplerate
        hits = np.where(x > x.max() * 0.1)[0]
        t = hits[0] / sr if len(hits) else None
    for f in (tj, tw):
        os.path.exists(f) and os.remove(f)
    return t
t_on, t_off = onset_s(1.0), onset_s(1.3)     # 0.3 beat = 0.15s apart at 120bpm
if t_on is not None and t_off is not None:
    gap = (t_off - t_on) * 1000
    check("microtiming SURVIVES render (off-grid note lands ~150ms late)", 130 < gap < 170, f"{round(gap,1)}ms (expect ~150)")
else:
    check("microtiming survives render", False, "render failed")

print(f"\nVERDICT: {len(FAIL)} fail" + ("" if not FAIL else " — " + ", ".join(FAIL)))
sys.exit(1 if FAIL else 0)
