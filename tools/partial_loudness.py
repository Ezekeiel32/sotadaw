#!/usr/bin/env python3
"""PARTIAL LOUDNESS — wave 81 (r-6 item 189): the Moore-Glasberg
two-signal model as the human-facing masking meter (the Neutron-class
court). For a target stem against the rest of the mix:

  ERB-banded excitation ->  N'_solo    = C * E_t^0.2
                            N'_partial = C * ((E_t+E_m)^0.2 - E_m^0.2)
  MUR = sum(N'_partial) / sum(N'_solo)       (masked-to-unmasked ratio)

MUR ~ 1.0 = the stem reads as loud in the mix as solo; the
listening-test red line sits at 10% (MUR < 0.10 = the stem is
functionally inaudible). Per-band loss names WHERE the collision
lives. Documented approximations vs the full DAFx-2004 port: uniform-
cam FFT banding instead of gammatones, a fixed outer/middle-ear
high-pass approximation, no temporal integration (steady-state RMS
windows) — the frequency-selective masking CORE is exact in form.

  mur(target, masker, sr)      arrays -> {mur, red, band_loss}
  stem_murs(stems_dir)         every stem vs the sum of the others
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

N_BANDS = 40
EXP = 0.2
RED_LINE = 0.10


def _cam(f):
    return 21.4 * np.log10(1.0 + 0.00437 * f)


def _band_edges(sr, n=N_BANDS):
    lo, hi = _cam(30.0), _cam(min(18000.0, sr / 2 * 0.95))
    cams = np.linspace(lo, hi, n + 1)
    return (10.0 ** (cams / 21.4) - 1.0) / 0.00437


def _outer_middle_ear_db(f):
    """Fixed approximation of the outer+middle-ear transfer: high-pass
    below ~500Hz (-12dB/oct-ish), gentle presence lift 2-5k, rolloff
    past 10k."""
    f = np.maximum(f, 1.0)
    low = -12.0 * np.maximum(np.log2(500.0 / f), 0.0)
    pres = 3.0 * np.exp(-0.5 * ((np.log2(f / 3000.0)) / 0.8) ** 2)
    high = -8.0 * np.maximum(np.log2(f / 10000.0), 0.0)
    return low + pres + high


def excitation(x, sr, n=N_BANDS):
    """Per-ERB-band excitation (power) with the ear weighting."""
    if len(x) < sr // 10:
        return np.zeros(n)
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
    w = 10.0 ** (_outer_middle_ear_db(freqs) / 10.0)
    spec = spec * w
    edges = _band_edges(sr, n)
    E = np.zeros(n)
    for i in range(n):
        m = (freqs >= edges[i]) & (freqs < edges[i + 1])
        E[i] = float(spec[m].sum())
    return E          # RAW power — mur() owns the joint scale; a
                      # per-signal normalize here erased the masker's
                      # absolute level (battery-caught)


def mur(target, masker, sr):
    """The two-signal partial-loudness ratio + per-band loss."""
    Et = excitation(np.asarray(target, dtype=np.float64), sr)
    Em = excitation(np.asarray(masker, dtype=np.float64), sr)
    # joint normalization: excitations must share a scale
    scale = max(Et.max(), Em.max(), 1e-30)
    Et, Em = Et / scale, Em / scale
    solo = np.power(np.maximum(Et, 0), EXP)
    part = np.power(np.maximum(Et + Em, 0), EXP) - \
        np.power(np.maximum(Em, 0), EXP)
    part = np.maximum(part, 0.0)
    s_sum = float(solo.sum())
    if s_sum <= 0:
        return {"mur": None, "red": False, "band_loss": []}
    m = float(part.sum() / s_sum)
    edges = _band_edges(sr)
    loss = []
    for i in range(N_BANDS):
        if solo[i] > 0.01 * solo.max():
            l = 1.0 - (part[i] / max(solo[i], 1e-30))
            if l > 0.6:
                loss.append({"band_hz": [round(float(edges[i])),
                                         round(float(edges[i + 1]))],
                             "loss": round(float(l), 2)})
    loss.sort(key=lambda d: -d["loss"])
    return {"mur": round(m, 3), "red": m < RED_LINE,
            "band_loss": loss[:6]}


def _read(path):
    import wave as wv
    w = wv.open(path, "rb")
    sr, sw, ch, nn = (w.getframerate(), w.getsampwidth(),
                      w.getnchannels(), w.getnframes())
    raw = w.readframes(nn)
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


def stem_murs(stems_dir):
    """Every stem vs the sum of the others — the collision table."""
    wavs = sorted(f for f in os.listdir(stems_dir)
                  if f.lower().endswith(".wav"))
    if len(wavs) < 2:
        return {}
    data = {}
    sr = None
    for f in wavs:
        x, sr = _read(os.path.join(stems_dir, f))
        data[f] = x
    n = min(len(x) for x in data.values())
    out = {}
    for f, x in data.items():
        rest = np.zeros(n)
        for g, y in data.items():
            if g != f:
                rest += y[:n]
        out[f] = mur(x[:n], rest, sr)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="PARTIAL LOUDNESS (w81)")
    ap.add_argument("stems_dir")
    a = ap.parse_args()
    table = stem_murs(a.stems_dir)
    for f, v in table.items():
        tag = "RED" if v.get("red") else "ok "
        print(f"  [{tag}] {f:30} MUR {v.get('mur')}")
    print(json.dumps(table, indent=1))
