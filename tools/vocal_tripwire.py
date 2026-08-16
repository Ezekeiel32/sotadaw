#!/usr/bin/env python3
"""THE VOCAL TRIPWIRE — wave 91 (r-11 item 241): the labeled-corpus
degradation gate. A court that scores mangled audio the same as clean
audio is DEAD — this battery plants two physical degradations on a
real sung take (fable_pop_vocal_demo, 190 known words) and demands
the measured WER RESPOND:

  clean           the baseline (must sit under the red line — the
                  corpus take was accepted-grade)
  lowpass 1.8k    consonants die first (the r-11 75% law) -> WER rises
  noise -14dB     masking -> WER rises further

Whisper runs three times (~1-2 min) — a --full suite leg by the house
pattern. Fail-open when the corpus pair is missing on this box.
"""
import json
import os
import sys
import tempfile
import wave as wv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG = os.path.join(ROOT, "songs", "fable_pop_vocal_demo.json")
WAV = os.path.join(ROOT, "songs", "fable_pop_vocal_demo_vocal.wav")


def _read(path):
    w = wv.open(path, "rb")
    sr, sw, ch, n = (w.getframerate(), w.getsampwidth(), w.getnchannels(),
                     w.getnframes())
    raw = w.readframes(n)
    w.close()
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000,
                     x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1), sr


def _write(path, x, sr):
    w = wv.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(np.clip(x, -1, 1 - 1e-6).astype(np.float64)
                  .__mul__(32767).astype("<i2").tobytes())
    w.close()


def degrade_lowpass(x, sr, cutoff=1800.0):
    S = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    S[f > cutoff] *= np.exp(-(f[f > cutoff] - cutoff) / 400.0)
    return np.fft.irfft(S, len(x)).real


def degrade_noise(x, sr, snr_db=14.0):
    rng = np.random.RandomState(7)
    n = rng.randn(len(x))
    sig = float(np.sqrt((x ** 2).mean()))
    n = n / float(np.sqrt((n ** 2).mean())) * sig * 10 ** (-snr_db / 20.0)
    return x + n


def wer_of(wav):
    import vocal_court as VC
    v = VC.court_vocal("fable_pop_vocal_demo", wav=wav, lang="en")
    return float(v.get("wer", 1.0)), v.get("verdict")


def main():
    if not (os.path.exists(SONG) and os.path.exists(WAV)):
        print("[skip] corpus pair missing on this box — tripwire vacuous")
        return 0
    x, sr = _read(WAV)
    # NEVER truncate: the court compares against ALL staged words —
    # a 60s cut scored 0.916 'clean' purely from deletions (tripwire
    # lesson #1)
    tmp = tempfile.mkdtemp(prefix="vtrip_")
    clean_p = os.path.join(tmp, "clean.wav")
    lp_p = os.path.join(tmp, "lp.wav")
    nz_p = os.path.join(tmp, "nz.wav")
    _write(clean_p, x, sr)
    _write(lp_p, degrade_lowpass(x, sr), sr)
    _write(nz_p, degrade_noise(degrade_lowpass(x, sr), sr), sr)
    w_clean, v_clean = wer_of(clean_p)
    w_lp, _ = wer_of(lp_p)
    w_nz, _ = wer_of(nz_p)
    print(f"clean WER {w_clean:.3f} [{v_clean}]  lowpass {w_lp:.3f}  "
          f"lowpass+noise {w_nz:.3f}")
    # THE TRIPWIRE LAW: this gate proves RESPONSE, not absolute quality
    # (quality is the vocal court's own verdict elsewhere). Clean must
    # leave detection HEADROOM and the ladder must rise monotonically.
    # (Measured baseline on this synthesized demo stem: 0.600 — real
    # commercial stems run ~0.25; the gap is the voice rail's known
    # distance, not the tripwire's business.)
    fails = []
    if not (w_clean < 0.75):
        fails.append("clean baseline unusable (whisper sees nothing)")
    if not (w_lp >= w_clean):
        fails.append("lowpass did not raise WER — the court is numb")
    if not (w_nz >= w_lp and w_nz >= w_clean + 0.15):
        fails.append("stacked degradation did not raise WER by the "
                     "0.15 headroom — the tripwire is dead")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"vocal_tripwire: {len(fails)} RED")
        return 1
    print("vocal_tripwire: ALL GREEN — the court RESPONDS to physics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
