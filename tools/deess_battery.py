#!/usr/bin/env python3
"""FX_DEESS battery — through the REAL m1 JIT lane (fx_deess is not AOT-baked,
so this also proves the new-fx-without-rebuild path). A synthetic voice (300Hz
body + hard 8kHz ess bursts) renders with and without the de-esser: the ess
band must duck hard IN the bursts, the body must stay within a fraction of a
dB, nothing clips, and zones must be live (amount 0 ~= bypass). SKIP-green
without m1.
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
    print("SKIP deess battery — m1 not built")
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="deess_")
sr = 44100
dur = 4.0
t = np.arange(int(dur * sr)) / sr
body = 0.30 * np.sin(2 * np.pi * 300 * t)
rng = np.random.default_rng(5)
ess = rng.standard_normal(len(t))
ess -= np.convolve(ess, np.ones(9) / 9, "same")            # crude highpass ~5k+
burst = ((t % 1.0) > 0.5) & ((t % 1.0) < 0.8)              # 300ms ess each second
x = body + 0.28 * ess * burst
src = os.path.join(tmp, "voice.wav")
with wave.open(src, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def song(fx):
    return {"bpm": 120, "lengthBars": 2, "masterGainDb": 0,
            "tracks": [{"name": "voice", "gainDb": 0, "fx": fx,
                        "source": {"kind": "audio"},
                        "audioClips": [{"file": src, "startBeat": 0,
                                        "lengthBeats": 8, "offsetSec": 0}]}]}


def render(fx, tag):
    j = os.path.join(tmp, f"{tag}.json")
    o = os.path.join(tmp, f"{tag}.wav")
    json.dump(song(fx), open(j, "w"), indent=1)
    r = subprocess.run([M1, "render", j, o], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0 and os.path.exists(o), f"render {tag}: {(r.stdout + r.stderr)[-300:]}"
    with wave.open(o) as w:
        sw, ch, fr = w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if sw == 3:                                             # m1 renders 24-bit
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        y = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        y = (y ^ 0x800000) - 0x800000
        y = y.astype(np.float64) / 8388608.0
    else:
        y = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    y = y.reshape(-1, ch).mean(axis=1)
    return y, fr


def band_db(y, fr, lo, hi, mask=None):
    Y = np.abs(np.fft.rfft(y if mask is None else y * mask))
    f = np.fft.rfftfreq(len(y), 1 / fr)
    m = (f >= lo) & (f < hi)
    e = float((Y[m] ** 2).sum())
    return 10 * np.log10(e + 1e-12)


dry, fr = render([], "dry")
wet, _ = render([{"id": "fx_deess", "params": {"freq": 5000, "thresh": -34, "amount": 14}}], "wet")
n = min(len(dry), len(wet))
dry, wet = dry[:n], wet[:n]
tt = np.arange(n) / fr
bm = (((tt % 1.0) > 0.52) & ((tt % 1.0) < 0.78)).astype(float)   # inside bursts

ok(len(wet) > sr, "JIT lane: an fx NOT in the AOT registry rendered through real m1")
duck = band_db(dry, fr, 6000, 16000, bm) - band_db(wet, fr, 6000, 16000, bm)
ok(duck > 6.0, f"ess band ducks {duck:.1f} dB inside the bursts (>6)")
body_shift = abs(band_db(dry, fr, 150, 600) - band_db(wet, fr, 150, 600))
ok(body_shift < 0.7, f"the voice's body moves only {body_shift:.2f} dB (<0.7)")
ok(int(np.sum(np.abs(wet) >= 0.999)) == 0, "0 clipped samples through the de-esser")

byp, _ = render([{"id": "fx_deess", "params": {"freq": 5000, "thresh": -34, "amount": 0}}], "byp")
byp = byp[:n]
null = 20 * np.log10(np.abs(byp - dry).max() + 1e-12)
ok(null < -35, f"amount=0 ~= bypass (max diff {null:.0f} dBFS — zones are LIVE + split reconstructs)")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} deess battery")
