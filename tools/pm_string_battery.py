#!/usr/bin/env python3
"""pm_string battery — the first physical model's zones govern real physics.

Proof surface (5 JIT renders through the real binary):
  Z1 tuning: the waveguide tracks trigger pitch exactly (f0 == 220 for A3)
  Z2 headroom law: 0 clipped at vel 1.0 solo
  Z3 damp = TONE: dark (0.05) centroid < 2.6kHz, bright (0.95) > 4kHz,
     bright > 1.8x dark (the excitation pre-damp lesson: the raw burst's
     click once drowned the loop filter — centroid ~10kHz whatever damp said)
  Z4 sustain = TIME: staccato's attack->tail drop exceeds ring's by >= 12 dB
Run: python3 tools/pm_string_battery.py
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def render(tdir, name, params):
    doc = {"version": 2, "bpm": 100, "key": "A minor", "lengthBars": 2,
           "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
           "tracks": [{"name": "s", "source": {"kind": "faust", "id": "pm_string",
                                               "params": params},
                       "gainDb": 0,
                       "notes": [{"start": 0, "len": 1.6, "pitch": 57, "vel": 1.0},
                                 {"start": 2, "len": 1.6, "pitch": 69, "vel": 1.0}]}]}
    j, w = os.path.join(tdir, name + ".json"), os.path.join(tdir, name + ".wav")
    json.dump(doc, open(j, "w"))
    subprocess.run([M1, "render", j, w], capture_output=True, timeout=180)
    a = json.loads(subprocess.run([PY, os.path.join(ROOT, "tools", "analyze2.py"), w],
                                  capture_output=True, text=True, timeout=120).stdout)
    return a, w


def tail_drop_db(wav):
    sr, x = wavfile.read(wav)
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= (np.abs(x).max() + 1e-12)
    att = np.sqrt(np.mean(x[int(0.05 * sr):int(0.25 * sr)] ** 2))
    tail = np.sqrt(np.mean(x[int(0.90 * sr):int(1.15 * sr)] ** 2))
    return 20.0 * np.log10((att + 1e-12) / (tail + 1e-12))


tdir = tempfile.mkdtemp(prefix="pmbat_")
base, _ = render(tdir, "base", {})
check("Z1 waveguide tracks trigger pitch", base.get("f0_hz") == 220.0,
      str(base.get("f0_hz")))
check("Z2 headroom law at vel 1.0", base.get("clipped_samples") == 0
      and base.get("peak_dbfs", 0) < -3.0,
      f"peak {base.get('peak_dbfs')}")
dark, _ = render(tdir, "dark", {"damp": 0.05})
bright, _ = render(tdir, "bright", {"damp": 0.95})
dc, bc = dark["spectral_centroid_hz"], bright["spectral_centroid_hz"]
check("Z3 damp governs tone", dc < 2600 and bc > 4000 and bc > 1.8 * dc,
      f"dark {dc:.0f} / bright {bc:.0f}")
_, ws = render(tdir, "stac", {"sustain": 0.0})
_, wr = render(tdir, "ring", {"sustain": 1.0})
ds, dr = tail_drop_db(ws), tail_drop_db(wr)
check("Z4 sustain governs time", ds - dr >= 12.0,
      f"stac drop {ds:.1f}dB vs ring {dr:.1f}dB")

print(f"pm_string battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
