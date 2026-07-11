#!/usr/bin/env python3
"""sing_battery.py — THE VOICE guarded: does DiffSinger sing the RIGHT NOTES?

For each of the 4 voice timbres, render sing_test's lyrics over its melody and
verify the vocal's f0 CONTOUR tracks the melody — the real singing-quality
metric (mumble hits no pitch; singing hits the written notes). Per melody
note's time window, extract f0 (autocorrelation) and check it matches the note
pitch mod octave within ~1.2 semitones. Runs CPU (CUDA_VISIBLE_DEVICES='').
"""
import json, os, subprocess, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python")
sys.path.insert(0, os.path.join(ROOT, "tools"))

VOICES = ["standard", "hunter", "lilith", "phantom"]


def load_wav(p):
    import wave
    with wave.open(p) as w:
        sr, n, sw = w.getframerate(), w.getnframes(), w.getsampwidth()
        raw = w.readframes(n)
    if sw == 3:
        a = np.zeros(len(raw) // 3, dtype=np.int32)
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        a = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        a = np.where(a & 0x800000, a - 0x1000000, a).astype(np.float32) / 8388608.0
    else:
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if w.getnchannels() == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return sr, a


def f0_at(x, sr, t0, t1):
    i0, i1 = int(t0 * sr), int(t1 * sr)
    w = x[i0:i1]
    if len(w) < sr // 100 or np.abs(w).max() < 0.02:
        return None
    w = w - w.mean()
    ac = np.correlate(w, w, "full")[len(w) - 1:]
    lo, hi = int(sr / 700), int(sr / 110)     # 110..700 Hz search
    if hi >= len(ac):
        return None
    lag = ac[lo:hi].argmax() + lo
    return sr / lag


def check(voice, song="sing_test"):
    tmp = f"_singbat_{voice}"
    src = os.path.join(ROOT, "songs", f"{tmp}.json")
    import shutil
    shutil.copy(os.path.join(ROOT, "songs", f"{song}.json"), src)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="")
    r = subprocess.run([PY, f"{ROOT}/tools/sing.py", "render", tmp, "melody", voice],
                       capture_output=True, text=True, env=env, timeout=240)
    wav = os.path.join(ROOT, "songs", f"{tmp}_vocal.wav")
    if not os.path.exists(wav):
        return voice, "RENDER FAIL", 0, 0
    s = json.load(open(src))
    bpm = float(s.get("bpm", 120)); spb = 60.0 / bpm
    mel = next((t for t in s["tracks"] if t["name"] == "melody"), None)
    sr, x = load_wav(wav)
    hits = tot = 0
    for n in mel["notes"]:
        t0 = n["start"] * spb + 0.08          # skip the consonant onset
        t1 = (n["start"] + n["len"]) * spb - 0.03
        if t1 - t0 < 0.08:
            continue
        f0 = f0_at(x, sr, t0, t1)
        if f0 is None:
            continue
        tot += 1
        target = 440.0 * 2 ** ((n["pitch"] - 69) / 12)
        # octave-fold both to compare pitch class distance in semitones
        cents = 1200 * np.log2(f0 / target)
        semi_off = abs(((cents + 600) % 1200) - 600) / 100.0
        hits += semi_off <= 1.2
    for f in (src, wav):
        if os.path.exists(f):
            os.remove(f)
    rate = hits / max(1, tot)
    return voice, ("OK" if rate >= 0.6 else "OFF-PITCH"), hits, tot


if __name__ == "__main__":
    bad = 0
    for v in VOICES:
        voice, verdict, hits, tot = check(v)
        bad += verdict != "OK"
        print(f"  {voice:9} {verdict:10} f0 tracks melody {hits}/{tot} notes")
    print(f"sing battery: {len(VOICES) - bad}/{len(VOICES)} voices sing on-pitch")
    sys.exit(1 if bad else 0)
