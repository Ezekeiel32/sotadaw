#!/usr/bin/env python3
"""FX_TRANSIENT battery — through the REAL m1 JIT lane. Percussive hits
(sharp onset + exponential tail): attack +9 must lift the ONSETS and leave the
tails, sustain -9 must cut the TAILS and leave the onsets, 0/0 must null
against dry, and nothing clips. SKIP-green without m1.
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
    print("SKIP transient battery — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="trans_")
sr = 44100
t = np.arange(4 * sr) / sr
tin = t % 1.0                                       # a hit every second
x = 0.25 * np.sin(2 * np.pi * 330 * t) * np.exp(-tin / 0.12)
src = os.path.join(tmp, "hits.wav")
with wave.open(src, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def render(fx, tag):
    j = os.path.join(tmp, f"{tag}.json")
    o = os.path.join(tmp, f"{tag}.wav")
    json.dump({"bpm": 120, "lengthBars": 2, "masterGainDb": 0,
               "tracks": [{"name": "hits", "gainDb": 0, "fx": fx,
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


def win_db(y, fr, a, b):
    """mean RMS dB over [hit+a, hit+b] across the hits at 1s, 2s, 3s."""
    segs = [y[int((h + a) * fr):int((h + b) * fr)] for h in (1.0, 2.0, 3.0)]
    seg = np.concatenate(segs)
    return 20 * np.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-12)


dry, fr = render([], "dry")
atk, _ = render([{"id": "fx_transient", "params": {"attack": 9, "sustain": 0}}], "atk")
sus, _ = render([{"id": "fx_transient", "params": {"attack": 0, "sustain": -9}}], "sus")
nul, _ = render([{"id": "fx_transient", "params": {"attack": 0, "sustain": 0}}], "nul")
n = min(len(dry), len(atk), len(sus), len(nul))
dry, atk, sus, nul = dry[:n], atk[:n], sus[:n], nul[:n]
ok(n > fr, "JIT lane: fx_transient (not AOT-baked) rendered through real m1")

on_lift = win_db(atk, fr, 0.001, 0.025) - win_db(dry, fr, 0.001, 0.025)
ok(on_lift > 3, f"attack +9: onsets lift {on_lift:.1f} dB (>3)")
tail_hold = abs(win_db(atk, fr, 0.20, 0.40) - win_db(dry, fr, 0.20, 0.40))
ok(tail_hold < 1.5, f"attack +9: tails move only {tail_hold:.2f} dB (<1.5)")

tail_cut = win_db(dry, fr, 0.20, 0.40) - win_db(sus, fr, 0.20, 0.40)
ok(tail_cut > 3, f"sustain -9: tails cut {tail_cut:.1f} dB (>3)")
on_hold = abs(win_db(sus, fr, 0.001, 0.025) - win_db(dry, fr, 0.001, 0.025))
ok(on_hold < 2.5, f"sustain -9: onsets move only {on_hold:.2f} dB (<2.5)")

tail = slice(int(0.25 * fr), n)
null = 20 * np.log10(np.abs(nul[tail] - dry[tail]).max() + 1e-12)
ok(null < -60, f"0/0 ~= bypass (max diff {null:.0f} dBFS — unity by construction)")
ok(int(np.sum(np.abs(atk) >= 0.999)) == 0, "0 clipped samples with attack +9")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} transient battery")
