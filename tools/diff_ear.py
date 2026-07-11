#!/usr/bin/env python3
"""THE DIFFERENTIAL EAR (BEST_DAW_30 #22b) — "what changed?" answers itself.

Two renders in, ONE honest measured sentence out — plus the Δ artifact:

  diff_ear.py <a.wav> <b.wav> [--json] [--delta out.wav]
  diff_ear.py --song <name>          (base render vs the pending take's render)

Composes the ears that already exist (analyze2 + dynamics_ears) into deltas a
producer says out loud: overall LU, per-band dB, width, centroid, PSR/LRA
(crush/breath), per-quarter arc — ranked by audibility, top moves become THE
SENTENCE. The Δ wav (B minus A, length-matched) is written for the play-Δ
button (chat card leg lands with the C++ batch). Numbers first, words never
without numbers behind them.
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from analyze2 import analyze                       # noqa: E402

SONGS = os.path.join(ROOT, "songs")
BANDS = ["low_20_120", "lowmid_120_500", "mid_500_2k", "himid_2k_6k", "high_6k_up"]
BAND_WORDS = {"low_20_120": "sub/low", "lowmid_120_500": "low-mids",
              "mid_500_2k": "mids", "himid_2k_6k": "presence", "high_6k_up": "air/hats"}


def _dyn(path):
    try:
        import dynamics_ears as DE
        m = DE.measure(path)
        return {k: m.get(k) for k in ("lra", "psr", "plr", "crest_db")}
    except Exception:
        return {}


def _delta_wav(a_path, b_path, out_path):
    """B minus A, length-matched — the audible residue of the change."""
    try:
        import numpy as np
        import soundfile as sf
        a, sra = sf.read(a_path, always_2d=True, dtype="float64")
        b, srb = sf.read(b_path, always_2d=True, dtype="float64")
        if sra != srb:
            return None
        n = min(len(a), len(b))
        ch = min(a.shape[1], b.shape[1])
        d = b[:n, :ch] - a[:n, :ch]
        peak = float(abs(d).max()) if n else 0.0
        sf.write(out_path, d, sra, subtype="FLOAT")
        import math
        return round(20 * math.log10(peak) if peak > 0 else -240.0, 1)
    except Exception:
        return None


def diff(a_path, b_path, delta_out=None):
    A, B = analyze(a_path), analyze(b_path)
    dyA, dyB = _dyn(a_path), _dyn(b_path)
    moves = []   # (audibility score, human phrase, metric row)
    dl = B["lufs_integrated"] - A["lufs_integrated"]
    if abs(dl) >= 0.4:
        moves.append((abs(dl) * 3.0, f"{abs(dl):.1f} LU {'louder' if dl > 0 else 'quieter'} overall",
                      {"metric": "lufs_integrated", "a": A["lufs_integrated"],
                       "b": B["lufs_integrated"], "delta": round(dl, 2), "unit": "LU"}))
    for b in BANDS:
        d = B["band_energy_pct"][b] - A["band_energy_pct"][b]
        if abs(d) >= 2.0:
            moves.append((abs(d), f"{BAND_WORDS[b]} {'up' if d > 0 else 'down'} {abs(d):.1f}%",
                          {"metric": f"band.{b}", "a": A["band_energy_pct"][b],
                           "b": B["band_energy_pct"][b], "delta": round(d, 1), "unit": "%"}))
    dc = B["spectral_centroid_hz"] - A["spectral_centroid_hz"]
    if A["spectral_centroid_hz"] and abs(dc) / max(A["spectral_centroid_hz"], 1) >= 0.12:
        moves.append((abs(dc) / 80.0, "brighter" if dc > 0 else "darker",
                      {"metric": "centroid_hz", "a": round(A["spectral_centroid_hz"]),
                       "b": round(B["spectral_centroid_hz"]), "delta": round(dc), "unit": "Hz"}))
    dw = (B.get("stereo_width_db") or 0) - (A.get("stereo_width_db") or 0)
    if abs(dw) >= 2.0:
        moves.append((abs(dw), f"{'wider' if dw > 0 else 'narrower'} ({abs(dw):.1f} dB side)",
                      {"metric": "width_db", "a": A.get("stereo_width_db"),
                       "b": B.get("stereo_width_db"), "delta": round(dw, 1), "unit": "dB"}))
    if dyA.get("psr") is not None and dyB.get("psr") is not None:
        dp = dyB["psr"] - dyA["psr"]
        if abs(dp) >= 0.5:
            moves.append((abs(dp) * 1.5,
                          f"{'more punch/breath' if dp > 0 else 'more crushed'} (PSR {dp:+.1f})",
                          {"metric": "psr", "a": dyA["psr"], "b": dyB["psr"],
                           "delta": round(dp, 2), "unit": "dB"}))
    if dyA.get("lra") is not None and dyB.get("lra") is not None:
        dr = dyB["lra"] - dyA["lra"]
        if abs(dr) >= 0.5:
            moves.append((abs(dr), f"dynamic range {'opens' if dr > 0 else 'tightens'} (LRA {dr:+.1f})",
                          {"metric": "lra", "a": dyA["lra"], "b": dyB["lra"],
                           "delta": round(dr, 2), "unit": "LU"}))
    qa, qb = A.get("rms_by_quarter_db") or [], B.get("rms_by_quarter_db") or []
    if len(qa) == 4 and len(qb) == 4:
        arc_a, arc_b = max(qa) - min(qa), max(qb) - min(qb)
        da = arc_b - arc_a
        if abs(da) >= 1.5:
            moves.append((abs(da) * 0.8, f"the arrangement {'moves more' if da > 0 else 'flattens'}",
                          {"metric": "quarter_arc_db", "a": round(arc_a, 1),
                           "b": round(arc_b, 1), "delta": round(da, 1), "unit": "dB"}))
    moves.sort(key=lambda m: -m[0])
    residue_db = _delta_wav(a_path, b_path, delta_out) if delta_out else None
    extra = len(moves) - 3
    sentence = ("no audible change (all deltas under threshold)" if not moves
                else ", ".join(m[1] for m in moves[:3])
                + (f" — and {extra} smaller move{'s' if extra > 1 else ''}"
                   if extra > 0 else ""))
    return {"a": os.path.basename(a_path), "b": os.path.basename(b_path),
            "sentence": sentence,
            "moves": [m[2] for m in moves],
            "delta_wav": delta_out if delta_out and residue_db is not None else None,
            "delta_peak_db": residue_db}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a", nargs="?")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--song", help="compare songs/<name>.wav vs songs/_prop_<name>.wav")
    ap.add_argument("--delta", help="write the B-A residue wav here")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.song:
        pa = os.path.join(SONGS, f"{a.song}.wav")
        pb = os.path.join(SONGS, f"_prop_{a.song}.wav")
        if not (os.path.exists(pa) and os.path.exists(pb)):
            sys.exit(f"need both {pa} and {pb} rendered")
        delta = a.delta or os.path.join(SONGS, f"_diff_{a.song}.wav")
    else:
        if not (a.a and a.b):
            sys.exit("need two wavs (or --song)")
        pa, pb = a.a, a.b
        delta = a.delta
    rep = diff(pa, pb, delta_out=delta)
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        print(f"WHAT CHANGED  {rep['a']} -> {rep['b']}")
        print(f"  {rep['sentence']}")
        for m in rep["moves"]:
            print(f"    [{m['metric']}] {m['a']} -> {m['b']}  ({m['delta']:+} {m['unit']})")
        if rep.get("delta_wav"):
            print(f"  Δ residue: {rep['delta_wav']} (peak {rep['delta_peak_db']} dBFS)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
