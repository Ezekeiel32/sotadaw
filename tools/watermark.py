#!/usr/bin/env python3
"""THE SOFT BINDING — wave 82 (r-31 item 046): a zero-dep audio
watermark so provenance SURVIVES what strips the C2PA manifest
(re-encode, re-upload). EU AI Act Art 50 wants machine-readable AI
marking that travels with the audio; the manifest alone dies at the
first mp3.

Design (spread-spectrum on band-energy, self-contained):
  frames of ~0.37s; carrier band 2-6kHz split in two sub-bands; each
  payload bit (PRN-spread, repeated) TILTS the sub-band energy ratio
  +-0.4dB — differential, so volume changes cancel; PRN keyed by a
  public project key (detection needs the key, not the original).
  32-bit payload = 8-bit magic 0xA5 + 24-bit id.

Survives: gain changes (differential), mp3/opus re-encode (proven in
the battery through ffmpeg 96k), moderate EQ. Dies under: heavy
time-stretch, deep lowpass <6k. Named honestly — a soft binding, not
DRM.

  embed(in_wav, out_wav, payload24)   -> writes the marked wav
  detect(wav)                          -> {found, payload, confidence}
"""
import hashlib
import os
import sys
import wave as wv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

FRAME_S = 0.37
BAND = (2000.0, 6000.0)
TILT_DB = 0.9
MAGIC = 0xA5
KEY = b"sotadaw-softbind-v1"


def _prn(nbits):
    seed = int.from_bytes(hashlib.sha256(KEY).digest()[:4], "big")
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=nbits)


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
    return x.reshape(-1, ch), sr, sw


def _write(path, x, sr, sw):
    w = wv.open(path, "wb")
    w.setnchannels(x.shape[1])
    w.setframerate(sr)
    if sw == 3:
        w.setsampwidth(3)
        v = np.clip(x * 8388607.0, -8388608, 8388607).astype(np.int32)
        b = np.zeros((v.size, 3), dtype=np.uint8)
        flat = v.reshape(-1)
        b[:, 0] = flat & 0xFF
        b[:, 1] = (flat >> 8) & 0xFF
        b[:, 2] = (flat >> 16) & 0xFF
        w.writeframes(b.tobytes())
    else:
        w.setsampwidth(2)
        w.writeframes(np.clip(x * 32767.0, -32768,
                              32767).astype("<i2").tobytes())
    w.close()


def _bits(payload24):
    word = (MAGIC << 24) | (int(payload24) & 0xFFFFFF)
    return [(word >> (31 - i)) & 1 for i in range(32)]


def _tilt_frame(spec, freqs, direction, tilt_db):
    lo, hi = BAND
    mid = (lo + hi) / 2.0
    a = (freqs >= lo) & (freqs < mid)
    b = (freqs >= mid) & (freqs < hi)
    g = 10.0 ** (tilt_db / 20.0)
    if direction > 0:
        spec[a] *= g
        spec[b] /= g
    else:
        spec[a] /= g
        spec[b] *= g
    return spec


def embed(in_wav, out_wav, payload24):
    x, sr, sw = _read(in_wav)
    n = int(sr * FRAME_S)
    bits = _bits(payload24)
    total = len(x) // n
    if total < 40:
        raise RuntimeError("audio too short for a durable binding "
                           f"({total} frames < 40)")
    prn = _prn(32)
    out = x.copy()
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    for f in range(total):
        bit = bits[f % 32]
        sign = prn[f % 32] * (1.0 if bit else -1.0)
        for c in range(x.shape[1]):
            seg = x[f * n:(f + 1) * n, c]
            spec = np.fft.rfft(seg)
            spec = _tilt_frame(spec, freqs, sign, TILT_DB)
            out[f * n:(f + 1) * n, c] = np.fft.irfft(spec, n)
    _write(out_wav, out, sr, sw)
    return {"frames": total, "reps": total // 32}


def detect(wav):
    x, sr, _ = _read(wav)
    mono = x.mean(axis=1)
    n = int(sr * FRAME_S)
    total = len(mono) // n
    if total < 32:
        return {"found": False, "why": "too short"}
    prn = _prn(32)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    lo, hi = BAND
    mid = (lo + hi) / 2.0
    a_m = (freqs >= lo) & (freqs < mid)
    b_m = (freqs >= mid) & (freqs < hi)
    ratios = np.zeros(total)
    ok = np.zeros(total, dtype=bool)
    for f in range(total):
        seg = mono[f * n:(f + 1) * n]
        spec = np.abs(np.fft.rfft(seg * np.hanning(n))) ** 2
        ea, eb = float(spec[a_m].sum()), float(spec[b_m].sum())
        if ea > 0 and eb > 0:
            ratios[f] = np.log10(ea / eb)
            ok[f] = True
    # DETREND: the content's own band ratio drifts slowly; a +-3-frame
    # moving average removes it, the +-frame-rate PRN tilt survives
    # (battery-caught: raw ratios flipped bits even on clean audio)
    k5 = 7
    pad = np.pad(ratios, k5 // 2, mode="edge")
    trend = np.convolve(pad, np.ones(k5) / k5, mode="valid")
    det = ratios - trend
    acc = np.zeros(32)
    cnt = np.zeros(32)
    for f in range(total):
        if not ok[f]:
            continue
        k = f % 32
        acc[k] += det[f] * prn[k]
        cnt[k] += 1
    cnt = np.maximum(cnt, 1)
    m = acc / cnt
    bits = [1 if v > 0 else 0 for v in m]
    conf = float(np.mean(np.abs(m)) / (np.std(m) + 1e-12))
    word = 0
    for b in bits:
        word = (word << 1) | b
    magic = (word >> 24) & 0xFF
    if magic == MAGIC:
        return {"found": True, "payload": word & 0xFFFFFF,
                "confidence": round(conf, 2)}
    inv = 0                                   # polarity-flipped chain
    for b in bits:
        inv = (inv << 1) | (1 - b)
    if (inv >> 24) & 0xFF == MAGIC:
        return {"found": True, "payload": inv & 0xFFFFFF,
                "confidence": round(conf, 2), "inverted": True}
    return {"found": False, "confidence": round(conf, 2)}


if __name__ == "__main__":
    import argparse
    import json as _j
    ap = argparse.ArgumentParser(description="THE SOFT BINDING (w82)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("embed")
    e.add_argument("in_wav")
    e.add_argument("out_wav")
    e.add_argument("--payload", type=lambda s: int(s, 0), default=0x50DA)
    d = sub.add_parser("detect")
    d.add_argument("wav")
    a = ap.parse_args()
    if a.cmd == "embed":
        print(_j.dumps(embed(a.in_wav, a.out_wav, a.payload)))
    else:
        print(_j.dumps(detect(a.wav)))
