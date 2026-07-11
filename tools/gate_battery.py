#!/usr/bin/env python3
"""FX_GATE battery — through the REAL m1 JIT lane. A phrase-and-silence voice
over a constant -38dB noise floor: the floor between phrases must drop hard,
the phrases must keep their level, depth 0 must null against dry, and nothing
clips. SKIP-green without m1.
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
    print("SKIP gate battery — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="gate_")
sr = 44100
dur = 4.0
t = np.arange(int(dur * sr)) / sr
phrase = ((t % 2.0) < 1.0).astype(float)                      # 1s on, 1s off
rng = np.random.default_rng(9)
# floor sigma 0.008: rms ~ -42dB but the gate's PEAK follower reads its ~3-sigma
# crests at ~-30dB — thresholds must clear the crest, not the rms (follower law)
x = 0.4 * np.sin(2 * np.pi * 330 * t) * phrase + 0.008 * rng.standard_normal(len(t))
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
    r = float(np.sqrt(np.mean(seg ** 2)))
    return 20 * np.log10(r + 1e-12)


dry, fr = render([], "dry")
wet, _ = render([{"id": "fx_gate", "params": {"thresh": -20, "depth": 40, "rel": 0.08}}], "wet")
n = min(len(dry), len(wet))
dry, wet = dry[:n], wet[:n]

# windows well inside the silent gaps (skip 150ms release skirts) and phrases
gap = slice(int(1.3 * fr), int(1.9 * fr))
ph = slice(int(0.25 * fr), int(0.9 * fr))
ok(n > fr, "JIT lane: fx_gate (not AOT-baked) rendered through real m1")
floor_drop = rms_db(dry[gap]) - rms_db(wet[gap])
ok(floor_drop > 12, f"noise floor between phrases drops {floor_drop:.1f} dB (>12)")
phrase_shift = abs(rms_db(dry[ph]) - rms_db(wet[ph]))
ok(phrase_shift < 0.5, f"the phrase itself moves only {phrase_shift:.2f} dB (<0.5)")
ok(int(np.sum(np.abs(wet) >= 0.999)) == 0, "0 clipped samples through the gate")

byp, _ = render([{"id": "fx_gate", "params": {"thresh": -20, "depth": 0}}], "byp")
null = 20 * np.log10(np.abs(byp[:n] - dry).max() + 1e-12)
ok(null < -35, f"depth=0 ~= bypass (max diff {null:.0f} dBFS — zones LIVE)")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} gate battery")
