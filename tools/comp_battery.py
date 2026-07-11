#!/usr/bin/env python3
"""FX_COMP battery — through the REAL m1 JIT lane. A loud/quiet alternating
tone: the loud passages must come DOWN hard (real N:1 GR — the whole point vs
the dead {"type":"comp"} friendly-param wiring), the quiet passages must stay,
makeup must lift, ratio 1 must null against dry, and nothing clips.
SKIP-green without m1.
"""
import json, os, shutil, subprocess, sys, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


if not os.path.exists(M1):
    print("SKIP comp battery — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="comp_")
sr = 44100
t = np.arange(4 * sr) / sr
loud = ((t < 1.0) | ((t >= 2.0) & (t < 3.0)))
x = np.sin(2 * np.pi * 330 * t) * np.where(loud, 0.5, 0.05)
src = os.path.join(tmp, "take.wav")
with wave.open(src, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def render(fx, tag):
    j = os.path.join(tmp, f"{tag}.json")
    o = os.path.join(tmp, f"{tag}.wav")
    json.dump({"bpm": 120, "lengthBars": 2, "masterGainDb": 0,
               "tracks": [{"name": "take", "gainDb": 0, "fx": fx,
                           "source": {"kind": "audio"},
                           "audioClips": [{"file": src, "startBeat": 0,
                                           "lengthBeats": 8, "offsetSec": 0}]}]},
              open(j, "w"), indent=1)
    r = subprocess.run([M1, "render", j, o], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"render {tag}: {(r.stdout + r.stderr)[-300:]}"
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


P = {"thresh": -25, "ratio": 4, "attack": 5, "release": 100}
dry, fr = render([], "dry")
wet, _ = render([{"id": "fx_comp", "params": P}], "wet")
n = min(len(dry), len(wet))
dry, wet = dry[:n], wet[:n]
loud_w = slice(int(0.3 * fr), int(0.9 * fr))       # well past the 5ms attack
quiet_w = slice(int(1.5 * fr), int(1.9 * fr))      # well past the 100ms release
ok(n > fr, "JIT lane: fx_comp (not AOT-baked) rendered through real m1")
gr = rms_db(dry[loud_w]) - rms_db(wet[loud_w])
ok(gr > 6, f"loud passage gain-reduced {gr:.1f} dB (>6 — REAL N:1, not the dead built-in's 0.4)")
qshift = abs(rms_db(dry[quiet_w]) - rms_db(wet[quiet_w]))
ok(qshift < 1.5, f"quiet passage under threshold moves only {qshift:.2f} dB (<1.5)")

mk, _ = render([{"id": "fx_comp", "params": {**P, "makeup": 6}}], "mk")
lift = rms_db(mk[:n][loud_w]) - rms_db(wet[loud_w])
ok(5.0 < lift < 7.0, f"makeup 6 lifts the compressed signal {lift:.2f} dB (~6)")

uni, _ = render([{"id": "fx_comp", "params": {"thresh": -25, "ratio": 1}}], "uni")
tail = slice(int(0.25 * fr), n)                    # skip makeup-smoo settle
null = 20 * np.log10(np.abs(uni[:n][tail] - dry[tail]).max() + 1e-12)
ok(null < -60, f"ratio=1 ~= bypass (max diff {null:.0f} dBFS — gain computer honest)")
ok(int(np.sum(np.abs(wet) >= 0.999)) == 0, "0 clipped samples through the compressor")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} comp battery")
