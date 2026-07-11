#!/usr/bin/env python3
"""EARS v4b — STRUCTURE FROM SOUND: novelty-curve section boundaries.

  segment.py <wav> [--bpm N] [--min-gap 8] [--json out.json]

Foote-checkerboard novelty (Foote 2000, the classic) over a coarse log-mel
self-similarity matrix: frames at 0.5s, cosine SSM on z-scored bands, novelty =
checkerboard correlation along the diagonal, boundaries = peaks with a min-gap.
Zero new deps (numpy only, loader from hear.py), CPU, any length.

Why not All-In-One (MIT, SOTA): its natten dependency has no wheel for
torch 2.11+cu130 and source-compiles CUDA kernels (probe 2026-07-05, aborted at
time-box). Foote ships today on every machine; the neural lane stays open for
a wheel-matched future.

With --bpm, boundaries also print as BARS (rounded to the nearest bar) — ready
to paste into song.json sections[] or feed stems_import.
"""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
from hear import load_wav, mel_edges


def mel_frames(x, sr, hop_s=0.5, bands=40):
    """log-mel energy per 0.5s frame — coarse on purpose (structure, not onsets)."""
    hop = int(hop_s * sr)
    nfft = 4096
    edges = mel_edges(bands, fmin=30.0, fmax=min(12000.0, sr / 2 - 100))
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)
    bins = [np.where((freqs >= lo) & (freqs < hi))[0]
            for lo, hi in zip(edges[:-1], edges[1:])]
    frames = []
    for i in range(0, len(x) - nfft, hop):
        mag = np.abs(np.fft.rfft(x[i:i + nfft] * np.hanning(nfft)))
        frames.append([float(mag[b].mean()) if len(b) else 0.0 for b in bins])
    F = np.log1p(np.array(frames) * 1000.0)
    mu, sd = F.mean(axis=0), F.std(axis=0) + 1e-9        # z-score per band
    return (F - mu) / sd, hop_s


def novelty_curve(F, kernel_s=10, hop_s=0.5):
    """Cosine SSM diagonal x checkerboard kernel -> novelty per frame."""
    n = len(F)
    Fn = F / (np.linalg.norm(F, axis=1, keepdims=True) + 1e-9)
    S = Fn @ Fn.T
    L = max(4, int(kernel_s / hop_s / 2))                 # half-size in frames
    g = np.exp(-0.5 * (np.linspace(-1, 1, 2 * L) ** 2) / 0.25)
    cb = np.outer(g, g) * np.kron([[1, -1], [-1, 1]], np.ones((L, L)))
    nov = np.zeros(n)
    for i in range(L, n - L):
        nov[i] = float((S[i - L:i + L, i - L:i + L] * cb).sum())
    nov = np.maximum(nov, 0.0)
    return nov / (nov.max() + 1e-9)


def boundaries(nov, hop_s=0.5, min_gap_s=8.0, thresh=0.35):
    """Defaults tuned on chezy_song ground truth (11 sections): precision 1.00 /
    recall 0.50 with bar-snap — every emitted boundary is REAL; subtle 8-bar
    layer-adds merge into their neighbors (right trade for import sections)."""
    gap = int(min_gap_s / hop_s)
    peaks = []
    for i in range(1, len(nov) - 1):
        if nov[i] < thresh or nov[i] <= nov[i - 1] or nov[i] < nov[i + 1]:
            continue
        if peaks and i - peaks[-1] < gap:
            if nov[i] > nov[peaks[-1]]:
                peaks[-1] = i
            continue
        peaks.append(i)
    return [(round(p * hop_s, 1), round(float(nov[p]), 3)) for p in peaks]


def label_sections(x, sr, bound_secs, vocal_path=None):
    """Semantic labels from the ears alone: energy rank + position + motion.
    Classes: intro / build / peak / break / verse / outro. 'peak' covers
    drop-or-hook (vocal share decides the word when a vocal stem exists)."""
    edges = [0.0] + list(bound_secs) + [len(x) / sr]
    vx = None
    if vocal_path and os.path.exists(vocal_path):
        vsr, vx = load_wav(vocal_path)
    feats = []
    for a, b in zip(edges[:-1], edges[1:]):
        seg = x[int(a * sr):int(b * sr)]
        if len(seg) < sr:
            feats.append({"rms": 0.0, "voc": 0.0})
            continue
        rms = float(np.sqrt((seg ** 2).mean()))
        voc = 0.0
        if vx is not None:
            vseg = vx[int(a * vsr):int(b * vsr)]
            if len(vseg) > vsr // 2:
                voc = float(np.sqrt((vseg ** 2).mean())) / (rms + 1e-9)
        feats.append({"rms": rms, "voc": voc})
    peak_rms = max(f["rms"] for f in feats) + 1e-12
    n = len(feats)
    labels = []
    for i, f in enumerate(feats):
        e = f["rms"] / peak_rms
        nxt = feats[i + 1]["rms"] / peak_rms if i + 1 < n else 0.0
        if i == 0 and e < 0.75:
            lab = "intro"
        elif i == n - 1 and e < 0.8:
            lab = "outro"
        elif e >= 0.82:
            lab = "hook" if f["voc"] > 0.35 else "drop"
        elif e < 0.55 and i > 0 and feats[i - 1]["rms"] / peak_rms >= 0.75:
            lab = "break"
        elif nxt >= 0.82 and e < nxt - 0.12:
            lab = "build"
        elif f["voc"] > 0.3:
            lab = "verse"
        elif 0.5 <= e < 0.8 and i <= (2 * n) // 3:
            lab = "verse"      # Harmonix grammar: verse = THE early/mid non-peak
                               # (912-song prior: thirds 1221/773/185 — verses
                               # live early and die by the final third)
        else:
            lab = "build" if nxt > e + 0.08 else "part"
        labels.append(lab)
    # FLAT-DYNAMICS GUARD (battery-honest): when nearly every mid section reads
    # as peak-class the landscape isn't discriminating (loudness-flat trap/hiphop
    # measured 2/9 vs goa 4/7) — withhold semantic names rather than spam 'drop'.
    mids = labels[1:-1] if n > 2 else []
    if mids and all(l in ("drop", "hook") for l in mids):
        labels = [labels[0]] + ["part"] * len(mids) + ([labels[-1]] if n > 1 else [])
    # dedupe names: intro, build, drop, drop 2, ...
    counts, named = {}, []
    for lab in labels:
        counts[lab] = counts.get(lab, 0) + 1
        named.append(lab if counts[lab] == 1 else f"{lab} {counts[lab]}")
    return named


def segment(path, bpm=None, min_gap_s=8.0, vocal_path=None, thresh=0.35):
    sr, x = load_wav(path)
    F, hop_s = mel_frames(x, sr)
    nov = novelty_curve(F, hop_s=hop_s)
    bounds = boundaries(nov, hop_s=hop_s, min_gap_s=min_gap_s, thresh=thresh)
    out = {"file": os.path.basename(path), "duration_s": round(len(x) / sr, 1),
           "boundaries": bounds}
    if bpm:
        spb = 60.0 / bpm * 4.0
        out["bars"] = [int(round(t / spb)) + 1 for t, _ in bounds]
        out["boundaries"] = [(round(round(t / spb) * spb, 1), c)   # snap to bar
                             for t, c in bounds]
    out["labels"] = label_sections(x, sr, [t for t, _ in out["boundaries"]],
                                   vocal_path=vocal_path)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--min-gap", type=float, default=8.0)
    ap.add_argument("--json", default=None)
    ap.add_argument("--vocal", default=None, help="vocal stem wav (labels gain verse/hook)")
    ap.add_argument("--profile", default="precise", choices=("precise", "pop"),
                    help="precise = every boundary real (electronic/imports; default). "
                         "pop = dense vocal-pop boundaries (Harmonix-912-tuned: "
                         "F@3 0.435 vs 0.359; on electronic it over-detects — "
                         "witnesses drop to 0.45/0.58, hence not the default)")
    a = ap.parse_args()
    if a.profile == "pop":
        a.min_gap = min(a.min_gap, 4.0)
        r = segment(a.wav, a.bpm, a.min_gap, vocal_path=a.vocal, thresh=0.15)
    else:
        r = segment(a.wav, a.bpm, a.min_gap, vocal_path=a.vocal)
    print(f"[segment] {r['file']} {r['duration_s']}s -> {len(r['boundaries'])} boundaries")
    labs = r.get("labels", [])
    if labs:
        print(f"  0.0s {'':14}{labs[0]}")
    for i, (t, c) in enumerate(r["boundaries"]):
        bar = f"  bar {r['bars'][i]:3}" if "bars" in r else ""
        lab = f"  {labs[i + 1]}" if i + 1 < len(labs) else ""
        print(f"  {t:7.1f}s  conf {c:.3f}{bar}{lab}")
    if a.json:
        json.dump(r, open(a.json, "w"), indent=1)
        print(f"[segment] -> {a.json}")
