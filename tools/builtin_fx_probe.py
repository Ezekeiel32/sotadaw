#!/usr/bin/env python3
"""builtin_fx_probe.py — empirical truth for the Tracktion built-ins the JSON
schema exposes ({"type":"eq"} / {"type":"comp"}). CLAUDE.md law: built-ins can
silently no-op; PROBE, never presume.

Current truth (2026-07-10): eq ALIVE; comp DEAD — its native ratio is 1/N
clamped to [0.05, 1.0] (tracktion_Compressor.cpp:196) so SongLoader's friendly
"ratio": 4 lands as 1:1 = zero GR. THE FIX (SongLoader.h comp block): convert
threshold -> juce::Decibels::decibelsToGain(v), ratio -> (v > 0.01f ? 1.0f/v
: 1.0f); attack/release/outputDb are already native. After the fix + rebuild,
this probe flips to COMP ALIVE (~14 dB GR here).

Exit: 0 = both alive (fix landed) · 2 = comp still dead (known, fix pending)
      1 = eq dead OR comp WRONG (real regression — investigate)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

if not os.path.exists(M1):
    print("SKIP builtin fx probe — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="builtin_")
sr = 44100
t = np.arange(4 * sr) / sr
loud = ((t < 1.0) | ((t >= 2.0) & (t < 3.0)))
dyn = 0.5 * np.sin(2 * np.pi * 330 * t) * loud + 0.05 * np.sin(2 * np.pi * 330 * t) * (~loud)
noise = 0.25 * np.random.default_rng(3).standard_normal(len(t))
for name, sig in (("dyn", dyn), ("noise", noise)):
    with wave.open(os.path.join(tmp, name + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(sig, -1, 1) * 32767).astype(np.int16).tobytes())


def render(src, fx, tag):
    j = os.path.join(tmp, tag + ".json"); o = os.path.join(tmp, tag + ".wav")
    json.dump({"bpm": 120, "lengthBars": 2, "masterGainDb": 0,
               "tracks": [{"name": "probe", "gainDb": 0, "fx": fx,
                           "source": {"kind": "audio"},
                           "audioClips": [{"file": os.path.join(tmp, src + ".wav"),
                                           "startBeat": 0, "lengthBeats": 8, "offsetSec": 0}]}]},
              open(j, "w"))
    r = subprocess.run([M1, "render", j, o], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (r.stdout + r.stderr)[-400:]
    with wave.open(o) as w:
        sw, ch, fr = w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        y = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        y = ((y ^ 0x800000) - 0x800000).astype(np.float64) / 8388608.0
    else:
        y = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return y.reshape(-1, ch).mean(axis=1), fr


def rms_db(seg):
    return 20 * np.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-12)


def band_db(y, fr, lo, hi):
    Y = np.abs(np.fft.rfft(y)); f = np.fft.rfftfreq(len(y), 1 / fr)
    m = (f >= lo) & (f < hi)
    return 10 * np.log10(float((Y[m] ** 2).sum()) + 1e-12)


dry, fr = render("dyn", [], "dyn_dry")
cmp_, _ = render("dyn", [{"type": "comp", "params": {"threshold": -25, "ratio": 4,
                                                     "attack": 5, "release": 100}}], "dyn_comp")
n = min(len(dry), len(cmp_)); dry, cmp_ = dry[:n], cmp_[:n]
gr_loud = rms_db(dry[int(0.3 * fr):int(0.9 * fr)]) - rms_db(cmp_[int(0.3 * fr):int(0.9 * fr)])
gr_quiet = rms_db(dry[int(1.5 * fr):int(1.9 * fr)]) - rms_db(cmp_[int(1.5 * fr):int(1.9 * fr)])

ndry, _ = render("noise", [], "n_dry")
neq, _ = render("noise", [{"type": "eq", "params": {"hiFreq": 4000, "hiGain": -12}}], "n_eq")
n2 = min(len(ndry), len(neq))
hf_drop = band_db(ndry[:n2], fr, 8000, 16000) - band_db(neq[:n2], fr, 8000, 16000)
shutil.rmtree(tmp, ignore_errors=True)

eq_alive = hf_drop > 6
comp_alive = gr_loud > 6 and abs(gr_quiet) < 2.0
comp_dead = gr_loud < 1.5 and abs(gr_quiet) < 1.5   # the known clamp signature
print(f"eq: hi-shelf -12 -> 8-16k drop {hf_drop:.1f} dB -> {'ALIVE' if eq_alive else 'DEAD'}")
print(f"comp: 19dB-over at 4:1 -> loud GR {gr_loud:.2f} dB, quiet {gr_quiet:.2f} dB -> "
      + ("ALIVE (fix landed)" if comp_alive else
         "DEAD as documented (SongLoader fix pending — use fx_comp)" if comp_dead else
         "WRONG (neither alive nor the known clamp — investigate)"))
sys.exit(0 if (eq_alive and comp_alive) else 2 if (eq_alive and comp_dead) else 1)
