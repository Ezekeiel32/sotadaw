#!/usr/bin/env python3
"""restore_audio.py — THE REPAIR RAIL: QC + fix real-world recordings before
they become tracks (the import lane assumed clean studio stems; phones, room
mics and old bounces carry hum, noise floor and DC that no fx should have to
fight downstream — fix at the SOURCE, per the mix law).

  restore_audio.py in.wav [-o out.wav] [--report-only]
                   [--denoise-db auto|0|N] [--hum auto|50|60|off] [--dc auto|on|off]

QC report: peak/rms, DC offset, noise floor (10th-pct frame RMS), mains hum
(50/60 Hz + harmonics vs local PSD neighborhood), hard-clip regions (report
only — declipping is deliberately NOT attempted). Fixes, each honest + bounded:
  dc      20 Hz zero-phase highpass (also kills subsonic thumps)
  hum     narrow zero-phase IIR notch comb at base*k (k=1..8, Q 35)
  denoise STFT spectral gate: noise profile = median spectrum of the quietest
          10% frames; soft mask (fully open 8 dB above profile) floored at
          -reduce_db, smoothed in time+freq against musical noise
Auto policy applies ONLY what the QC flags — a clean file passes through as a
byte-copy with applied=[]. Deterministic. Machine line: RESTORE_JSON {...}.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
import scipy.ndimage as ndi
import scipy.signal as sig
import soundfile as sf

FRAME_S = 0.046          # ~46 ms QC frames
CLIP_AT = 0.9995
HUM_MIN_DB = 10.0        # harmonic peak must clear its PSD neighborhood by this
FLOOR_NOISY_DB = -60.0   # auto-denoise engages above this floor
DC_MIN = 5e-4


def _mono(y):
    return y if y.ndim == 1 else y.mean(axis=1)


def qc(y, sr):
    m = _mono(y)
    n = max(1, int(FRAME_S * sr))
    nfr = len(m) // n
    fr = m[: nfr * n].reshape(nfr, n) if nfr else m.reshape(1, -1)
    frms = np.sqrt((fr ** 2).mean(axis=1))
    floor = float(np.percentile(frms, 10)) if nfr >= 4 else float(frms.min())
    clip = np.abs(m) >= CLIP_AT
    edges = np.diff(clip.astype(int))
    starts = np.flatnonzero(edges == 1)
    regions = 0
    for s in starts:
        e = s + 1
        while e < len(m) and clip[e]:
            e += 1
        if e - s >= 3:
            regions += 1
    base, strength, harms = detect_hum(m, sr)
    return {
        "sr": int(sr), "dur_s": round(len(m) / sr, 2),
        "peak_db": round(20 * np.log10(float(np.abs(m).max()) + 1e-12), 2),
        "rms_db": round(20 * np.log10(float(np.sqrt((m ** 2).mean())) + 1e-12), 2),
        "dc": round(float(m.mean()), 6),
        "noise_floor_db": round(20 * np.log10(floor + 1e-12), 2),
        "hum": ({"base": base, "strength_db": round(strength, 1), "harmonics": harms}
                if base else None),
        "clip_regions": int(regions),
    }


def detect_hum(m, sr):
    """(base|None, strength_db, harmonics_found) via Welch PSD neighborhoods."""
    nper = min(len(m), 32768)
    if nper < 8192:
        return None, 0.0, 0
    f, p = sig.welch(m, fs=sr, nperseg=nper)
    df = f[1] - f[0]
    best = (None, 0.0, 0)
    for base in (50.0, 60.0):
        scores, found = [], 0
        for k in range(1, 5):
            fc = base * k
            if fc > sr / 2 - 50:
                break
            peak_m = (f >= fc - 1.5) & (f <= fc + 1.5)
            hood = (f >= fc - 12) & (f <= fc + 12) & ~((f >= fc - 3) & (f <= fc + 3))
            if not peak_m.any() or not hood.any():
                continue
            s = 10 * np.log10(p[peak_m].max() + 1e-24) - 10 * np.log10(np.median(p[hood]) + 1e-24)
            scores.append(s)
            if s > HUM_MIN_DB:
                found += 1
        if found >= 2:
            avg = float(np.mean(sorted(scores, reverse=True)[:found]))
            if avg > best[1]:
                best = (base, avg, found)
    return best


def fix_dc(y, sr):
    sos = sig.butter(4, 20.0, "highpass", fs=sr, output="sos")
    return sig.sosfiltfilt(sos, y, axis=0).astype(y.dtype, copy=False)


def fix_hum(y, sr, base, nharm=8, q=35.0):
    out = y.astype(np.float64, copy=True)
    for k in range(1, nharm + 1):
        fc = base * k
        if fc >= sr / 2 - 50:
            break
        b, a = sig.iirnotch(fc, q, fs=sr)
        out = sig.filtfilt(b, a, out, axis=0)
    return out


def denoise(y, sr, reduce_db=10.0):
    """per-channel STFT spectral gate; profile from the quietest 10% frames."""
    def one(m):
        nper, nov = 2048, 1536
        _, _, Z = sig.stft(m, fs=sr, nperseg=nper, noverlap=nov, padded=True)
        mag = np.abs(Z)
        frame = np.sqrt((mag ** 2).mean(axis=0))
        k = max(4, int(0.10 * mag.shape[1]))
        prof = np.median(mag[:, np.argsort(frame)[:k]], axis=1)
        floor = 10 ** (-reduce_db / 20.0)
        over = mag / (prof[:, None] * 2.5 + 1e-12)      # 8 dB over profile = open
        gain = floor + (1.0 - floor) * np.clip(over - 1.0, 0.0, 1.0)
        gain = ndi.uniform_filter(gain, size=(3, 5))
        _, out = sig.istft(Z * gain, fs=sr, nperseg=nper, noverlap=nov)
        out = out[: len(m)]
        return np.pad(out, (0, len(m) - len(out))) if len(out) < len(m) else out

    if y.ndim == 1:
        return one(y)
    return np.stack([one(y[:, c]) for c in range(y.shape[1])], axis=1)


def restore(y, sr, denoise_db="auto", hum="auto", dc="auto"):
    before = qc(y, sr)
    out = y.astype(np.float64, copy=True)
    applied = []
    if dc == "on" or (dc == "auto" and abs(before["dc"]) > DC_MIN):
        out = fix_dc(out, sr)
        applied.append("dc")
    hb = None
    if hum in ("50", "60"):
        hb = float(hum)
    elif hum == "auto" and before["hum"]:
        hb = before["hum"]["base"]
    if hb:
        out = fix_hum(out, sr, hb)
        applied.append(f"hum{int(hb)}")
    rd = None
    if denoise_db == "auto":
        rd = 10.0 if before["noise_floor_db"] > FLOOR_NOISY_DB else None
    elif float(denoise_db) > 0:
        rd = float(denoise_db)
    if rd:
        out = denoise(out, sr, rd)
        applied.append(f"denoise{rd:g}")
    return out, applied, before


def main(argv=None):
    ap = argparse.ArgumentParser(description="QC + repair a recording (report is free)")
    ap.add_argument("inp")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--denoise-db", default="auto", help="auto | 0 (off) | N dB of reduction")
    ap.add_argument("--hum", default="auto", choices=["auto", "50", "60", "off"])
    ap.add_argument("--dc", default="auto", choices=["auto", "on", "off"])
    a = ap.parse_args(argv)

    y, sr = sf.read(a.inp, always_2d=False)
    info = sf.info(a.inp)
    if a.report_only:
        print("RESTORE_JSON " + json.dumps({"qc": qc(y, sr), "applied": [], "out": None}))
        return 0

    out, applied, before = restore(y, sr, a.denoise_db, a.hum, a.dc)
    dst = a.out or os.path.splitext(a.inp)[0] + "_restored.wav"
    if not applied:
        shutil.copyfile(a.inp, dst)             # clean file = byte-honest passthrough
        after = before
    else:
        peak = float(np.abs(out).max())
        if peak > 0.999:                        # never CREATE clipping while repairing
            out = out * (0.999 / peak)
            applied.append("trim_peak")
        subtype = "PCM_24" if "24" in (info.subtype or "") else \
                  ("FLOAT" if "FLOAT" in (info.subtype or "").upper() else "PCM_16")
        sf.write(dst, out, sr, subtype=subtype)
        after = qc(out, sr)
    print("RESTORE_JSON " + json.dumps(
        {"qc_before": before, "applied": applied, "qc_after": after, "out": dst}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
