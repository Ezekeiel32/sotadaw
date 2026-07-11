#!/usr/bin/env python3
"""EARS v4 — THE BEAT BRAIN (Beat This!, CPJKU, MIT — ledger-verified 2026-07-05).

beatgrid.py <audio> [--json] [--cpu]

Neural beat/downbeat tracking on demand: bpm (median inter-beat), first beat, bar count,
meter estimate, stability. Lives OUTSIDE the hot analyze2 path by design — metrology
stays instant; the beat brain loads when a lane needs truth (imports, DJ grids, groove
extraction). First run downloads the checkpoint to ~/.cache (offline after that).
"""
import argparse, json, sys

import numpy as np


def analyze_grid(path, device=None):
    from beat_this.inference import File2Beats
    if device is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"
    f2b = File2Beats(checkpoint_path="final0", device=device, dbn=False)
    beats, downbeats = f2b(path)
    beats = np.asarray(beats, dtype=float)
    downbeats = np.asarray(downbeats, dtype=float)
    out = {"file": path, "n_beats": int(len(beats)), "n_downbeats": int(len(downbeats)),
           "bpm": None, "bpm_stability": None, "first_beat_s": None, "first_downbeat_s": None,
           "meter_estimate": None, "device": device}
    if len(beats) >= 2:
        ibis = np.diff(beats)
        med = float(np.median(ibis))
        out["bpm"] = round(60.0 / med, 2) if med > 1e-6 else None
        iqr = float(np.percentile(ibis, 75) - np.percentile(ibis, 25))
        out["bpm_stability"] = round(1.0 - min(1.0, iqr / max(med, 1e-6)), 3)
        out["first_beat_s"] = round(float(beats[0]), 4)
        out["beats_head"] = [round(float(b), 4) for b in beats[:16]]
    if len(downbeats) >= 2:
        out["first_downbeat_s"] = round(float(downbeats[0]), 4)
        if len(beats) >= 2:
            per_bar = np.diff(downbeats) / np.median(np.diff(beats))
            out["meter_estimate"] = int(round(float(np.median(per_bar))))
        out["downbeats_head"] = [round(float(d), 4) for d in downbeats[:8]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    g = analyze_grid(a.audio, device="cpu" if a.cpu else None)
    if a.json:
        print(json.dumps(g, indent=1))
        return
    print(f"BEAT GRID — {g['file']}")
    print(f"  bpm {g['bpm']}  (stability {g['bpm_stability']})  meter ~{g['meter_estimate']}/4")
    print(f"  {g['n_beats']} beats / {g['n_downbeats']} downbeats; "
          f"first beat {g['first_beat_s']}s, first downbeat {g['first_downbeat_s']}s")


if __name__ == "__main__":
    main()
