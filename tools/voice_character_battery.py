#!/usr/bin/env python3
"""VOICE CHARACTER BATTERY — wave 62 (items 210/212/213). Parse checks
pure; two JIT render proofs (drift wobbles, evolution never repeats)."""
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import wave as wavmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import voice_character as VCH  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def read_wav(path):
    w = wavmod.open(path, "rb")
    sr, sw, ch, n = (w.getframerate(), w.getsampwidth(), w.getnchannels(),
                     w.getnframes())
    raw = w.readframes(n)
    w.close()
    a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
         | (a[:, 2].astype(np.int32) << 16))
    x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) \
        / 8388608.0
    return x.reshape(-1, ch).mean(axis=1), sr


def render(source_id, secs=12, pitch=57):
    tmp = tempfile.mkdtemp(prefix="vch_")
    sj, wv = os.path.join(tmp, "s.json"), os.path.join(tmp, "s.wav")
    beats = secs * 2
    json.dump({"version": 2, "bpm": 120, "lengthBars": beats // 4 + 1,
               "masterGainDb": 0.0, "master": [],
               "tracks": [{"name": "v", "source": {"id": source_id},
                           "gainDb": 0.0,
                           "notes": [{"start": 0, "len": beats,
                                      "pitch": pitch, "vel": 110}]}]},
              open(sj, "w"))
    r = subprocess.run([M1, "render", sj, wv], capture_output=True,
                       text=True, timeout=600)
    if r.returncode != 0:
        return None, None
    return read_wav(wv)


def f0_track(x, sr, f_lo, f_hi, win_s=0.25):
    n = int(sr * win_s)
    out = []
    for i in range(0, len(x) - n, n):
        seg = x[i:i + n] * np.hanning(n)
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        band = (freqs > f_lo) & (freqs < f_hi)
        if not band.any() or spec[band].max() < 1e-6:
            continue
        bi = np.argmax(spec[band])
        fs, ss = freqs[band], spec[band]
        if 0 < bi < len(ss) - 1:            # parabolic interp = cent-true
            d = 0.5 * (ss[bi - 1] - ss[bi + 1]) / \
                (ss[bi - 1] - 2 * ss[bi] + ss[bi + 1] + 1e-12)
            out.append(fs[bi] + d * (fs[1] - fs[0]))
        else:
            out.append(fs[bi])
    return out


# ------------------------------------------------ 212 the analog pass
tmp = tempfile.mkdtemp(prefix="vch_fix_")
plain = os.path.join(tmp, "fixture.dsp")
open(plain, "w").write(
    'import("stdfaust.lib");\n'
    'freq = hslider("freq", 220, 20, 2000, 0.001);\n'
    'gain = hslider("gain", 0.5, 0, 1, 0.01);\n'
    'gate = button("gate");\n'
    'env = en.adsr(0.01, 0.1, 0.9, 0.2, gate);\n'
    'process = os.sawtooth(freq)*env*gain*0.5 <: _,_;\n')
out = VCH.analogize(plain)
check("analogize: emits the _analog twin with the drift line",
      out and out.endswith("_analog.dsp") and
      "no.lfnoise(0.37)" in open(out).read() and
      "freq_raw" in open(out).read(), str(out))
check("analogize: idempotent-safe (the twin is never re-wrapped)",
      VCH.analogize(out) is None)
check("court_character: the plain fixture is dead-stiff, the twin "
      "is lively",
      VCH.court_character(plain)["advisories"] and
      not VCH.court_character(out)["advisories"])

# the render proof: a SINGLE-SAW fixture pair (a 7-saw voice bin-hops
# the f0 probe — the fixture isolates the drift). JIT resolves
# instruments/ only, so the pair lives there for the render.
fx_base = os.path.join(VCH.INSTR, "_w62fix.dsp")
open(fx_base, "w").write(open(plain).read())
ana = VCH.analogize(fx_base, os.path.join(VCH.INSTR,
                                          "_w62fix_analog.dsp"),
                    cents=5.0)
check("analogize: wraps the render fixture", ana is not None)
x0, sr0 = render("_w62fix")
x1, sr1 = render("_w62fix_analog")
check("render: both twins sound",
      x0 is not None and x1 is not None and
      float(np.abs(x1).max()) > 0.01, 
      f"base={x0 is not None} analog_peak={float(np.abs(x1).max()) if x1 is not None else 0:.3f}")
if x1 is not None and x0 is not None:
    A3 = 220.0
    t0 = f0_track(x0[sr0:], sr0, A3 * 0.97, A3 * 1.03)
    t1 = f0_track(x1[sr1:], sr1, A3 * 0.97, A3 * 1.03)
    spread0 = 1200 * math.log2(max(t0) / min(t0)) if t0 else 99
    spread1 = 1200 * math.log2(max(t1) / min(t1)) if len(t1) > 3 else 0
    check("proof: the analog twin DRIFTS (>=2 cents span) while the "
          "base holds (<1)",
          spread1 >= 2.0 and spread0 < 1.0,
          f"base {spread0:.2f}c analog {spread1:.2f}c")
os.remove(fx_base)

# ------------------------------------------------ 213 the evolution
xe, sre = render("pad_evolve", secs=16)
check("pad_evolve renders via JIT", xe is not None)
if xe is not None:
    n = int(sre * 0.5)
    cens = []
    for i in range(0, len(xe) - n, n):
        seg = xe[i:i + n] * np.hanning(n)
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(n, 1.0 / sre)
        s = spec.sum()
        if s > 1e-6:
            cens.append(float((spec * freqs).sum() / s))
    cens = cens[2:]
    span = (max(cens) - min(cens)) if cens else 0
    check("proof: the cutoff journey MOVES (centroid span > 250Hz)",
          span > 250, f"span {span:.0f}Hz")
    c = np.array(cens) - np.mean(cens)
    ac = np.correlate(c, c, "full")[len(c) - 1:]
    ac = ac / (ac[0] + 1e-12)
    lag_floor = 4                       # ignore trivial short lags
    peak = float(ac[lag_floor:].max()) if len(ac) > lag_floor else 1.0
    check("proof: motion never re-aligns (incommensurate LFOs: "
          "autocorr peak < 0.8 past lag 2s)", peak < 0.8,
          f"peak {peak:.2f}")

# ------------------------------------------------ 210 attack classes
song = {"tracks": [
    {"name": "pluck_lead", "source": {"id": "x", "params": {"attack": 0.4}},
     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 90}]},
    {"name": "pad_bed", "source": {"id": "x", "params": {"attack": 0.002}},
     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 90}]},
    {"name": "pad_ok", "source": {"id": "x", "params": {"attack": 0.9}},
     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 90}]}]}
v = VCH.court_attack_class(song)
kinds = {(a["track"]) for a in v["advisories"]}
check("attack court: a 400ms 'pluck' and a 2ms 'pad' both flag; the "
      "slow pad passes",
      kinds == {"pluck_lead", "pad_bed"}, str(v))
check("attack court: zone default read from the voice source "
      "(supersaw_jp attack 4ms fits lead)",
      not VCH.court_attack_class({"tracks": [
          {"name": "lead_main", "source": {"id": "supersaw_jp"},
           "notes": [{"start": 0, "len": 1, "pitch": 60,
                      "vel": 90}]}]})["advisories"])

os.remove(ana)                          # the twins were proof artifacts
print()
if FAILS:
    print(f"voice_character_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("voice_character_battery: ALL GREEN")
