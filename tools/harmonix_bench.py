#!/usr/bin/env python3
"""THE 912-WITNESS BENCH — segment.py's Foote lane scored on the Harmonix Set.

  harmonix_bench.py [--limit N] [--kernel 10] [--thresh 0.35] [--gap 8]

Data (both MIT, license read at source 2026-07-05): segments/*.txt ground truth
(time label per line, 'end' sentinel) + Harmonix_melspecs.tgz (their mels; params
in info.json). Pipeline: their mel -> aggregate to 0.5s frames -> log/z-score ->
novelty_curve/boundaries straight from tools/segment.py (same code that ships).
Score: boundary precision/recall/F at ±0.5s and ±3s (MIREX windows), macro-avg.

The point: firing 20's two-witness battery becomes a 912-witness scoreboard.
Numbers land in eval/harmonix_bench.json; expect classic-Foote territory
(F@3 well under neural SOTA) — this is the honest baseline the neural lane must
beat when natten wheels catch up.
"""
import argparse, json, os, sys, tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
from segment import novelty_curve, boundaries

BENCH = os.path.join(ROOT, "library", "benchmarks", "harmonix")
SEGS = os.path.join(BENCH, "segments")
MELS = os.path.join(BENCH, "melspecs")


def truth_bounds(path):
    ts = []
    for line in open(path):
        parts = line.split()
        if len(parts) < 2:
            continue
        t, lab = float(parts[0]), parts[1]
        if lab == "end":
            return ts, t
        if t > 0.0:
            ts.append(t)
    return ts, (ts[-1] if ts else 0.0)


def frames_05s(mel, sr, hop):
    """their mel (bands x frames) -> 0.5s frames x bands, log + z-score."""
    if mel.shape[0] > mel.shape[1]:
        mel = mel.T
    fps = sr / hop
    step = max(1, int(round(fps * 0.5)))
    n = mel.shape[1] // step
    F = np.array([mel[:, i * step:(i + 1) * step].mean(axis=1) for i in range(n)])
    F = np.log1p(np.maximum(F, 0.0) * 1000.0)
    mu, sd = F.mean(axis=0), F.std(axis=0) + 1e-9
    return (F - mu) / sd, 0.5


def score(got, truth, tol):
    if not got or not truth:
        return 0.0, 0.0, 0.0
    tp = sum(1 for g in got if min(abs(g - t) for t in truth) <= tol)
    m = sum(1 for t in truth if any(abs(g - t) <= tol for g in got))
    p, r = tp / len(got), m / len(truth)
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--kernel", type=float, default=10.0)
    ap.add_argument("--thresh", type=float, default=0.35)
    ap.add_argument("--gap", type=float, default=8.0)
    a = ap.parse_args()

    info = json.load(open(os.path.join(MELS, "info.json")))
    sr = info.get("SR", info.get("sr", 22050))
    hop = info.get("HOP_LENGTH", info.get("hop_length", 1024))
    print(f"[bench] mel params: sr {sr} hop {hop} ({len(os.listdir(MELS))} files)")

    rows, skipped = [], 0
    names = sorted(f[:-4] for f in os.listdir(SEGS) if f.endswith(".txt"))
    if a.limit:
        names = names[:a.limit]
    for i, name in enumerate(names):
        mp = os.path.join(MELS, f"{name}-mel.npy")
        if not os.path.exists(mp):
            skipped += 1
            continue
        try:
            mel = np.load(mp)
            F, hop_s = frames_05s(mel, sr, hop)
            if len(F) < 12:
                skipped += 1
                continue
            nov = novelty_curve(F, kernel_s=a.kernel, hop_s=hop_s)
            got = [t for t, _ in boundaries(nov, hop_s=hop_s,
                                            min_gap_s=a.gap, thresh=a.thresh)]
            truth, _end = truth_bounds(os.path.join(SEGS, f"{name}.txt"))
            r05 = score(got, truth, 0.5)
            r3 = score(got, truth, 3.0)
            rows.append({"name": name, "n_got": len(got), "n_truth": len(truth),
                         "p3": r3[0], "r3": r3[1], "f3": r3[2], "f05": r05[2]})
        except Exception as e:
            skipped += 1
            if skipped <= 3:
                print(f"[bench] {name} error: {e}")
        if (i + 1) % 200 == 0:
            print(f"[bench] {i + 1}/{len(names)}…", flush=True)

    if not rows:
        raise SystemExit("[bench] nothing scored — check melspecs dir")
    agg = {k: round(float(np.mean([r[k] for r in rows])), 3)
           for k in ("p3", "r3", "f3", "f05")}
    out = {"tracks_scored": len(rows), "skipped": skipped,
           "params": {"kernel": a.kernel, "thresh": a.thresh, "gap": a.gap},
           "macro": agg,
           "worst": sorted(rows, key=lambda r: r["f3"])[:5],
           "best": sorted(rows, key=lambda r: -r["f3"])[:5]}
    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "eval", "harmonix_bench.json"), "w"),
              indent=1)
    print(f"[bench] {len(rows)} tracks (skipped {skipped}): "
          f"F@3s {agg['f3']} (P {agg['p3']} / R {agg['r3']}), F@0.5s {agg['f05']}")
    print("[bench] -> eval/harmonix_bench.json")


if __name__ == "__main__":
    main()
