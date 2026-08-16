#!/usr/bin/env python3
"""THE DRIFT COURT — wave 95 (r-32 item 185): KAD (kernel audio
distance — unbiased MMD, distribution-free, honest at small N; the
strictly-better FAD) between a genre's CURRENT takes and its banked
reference embedding set. A rising KAD = the generator drifting away
from the genre's ears-passed distribution — the population-level
complement to the per-clip PQ tripwire.

  seed                 bank per-genre reference sets from the eval
                       corpus (12 CLAP windows each) + the NULL kad
                       (self-split) that calibrates the threshold
  check <wav> <genre>  KAD(current, reference) + verdict vs 3x null
  --selftest           same-genre halves stay null; funk-vs-ambient
                       screams

Never raw FAD across different N (sample-size bias — the r-32 law).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(ROOT, "eval", "kad_ref")
N_WIN = 12


def window_embeddings(wav, n=N_WIN):
    """n CLAP windows spread across the file -> (m, 512), silent
    windows skipped."""
    import clap_embed as CE
    if not CE.available():
        return None
    import torch
    import wave as wv
    model, proc, dev = CE.load()
    try:
        w = wv.open(wav, "rb")
        dur = w.getnframes() / w.getframerate()
        w.close()
    except Exception:
        dur = 120.0
    span = max(dur - CE._MAXDUR, 0.0)
    vecs = []
    for i in range(n):
        off = (i + 0.5) / n * span
        x = CE._load_audio_at(wav, off)
        if x is None:
            continue
        try:
            with torch.no_grad():
                inp = proc(audio=[x], sampling_rate=CE._SR,
                           return_tensors="pt").to(dev)
                e = model.get_audio_features(**inp).pooler_output
                nv = CE._norm(e)
                v = (nv.cpu().numpy() if hasattr(nv, "cpu")
                     else nv)[0]
            vecs.append(v)
        except Exception:
            continue
    return np.array(vecs, "float32") if vecs else None


def kad(X, Y):
    """Unbiased MMD^2 with a Gaussian kernel (median heuristic)."""
    X, Y = np.asarray(X, "float64"), np.asarray(Y, "float64")
    if len(X) < 3 or len(Y) < 3:
        return None
    Z = np.vstack([X, Y])
    d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
    med = np.median(d2[d2 > 0])
    if med <= 0:
        return 0.0
    K = np.exp(-d2 / (2.0 * med))
    m, n = len(X), len(Y)
    Kxx = K[:m, :m]
    Kyy = K[m:, m:]
    Kxy = K[:m, m:]
    xx = (Kxx.sum() - np.trace(Kxx)) / (m * (m - 1))
    yy = (Kyy.sum() - np.trace(Kyy)) / (n * (n - 1))
    xy = Kxy.mean()
    return float(max(xx + yy - 2 * xy, 0.0))


def seed():
    import glob
    os.makedirs(REF_DIR, exist_ok=True)
    nulls = {}
    for w in sorted(glob.glob(os.path.join(ROOT, "songs", "eval_*.wav"))):
        g = os.path.basename(w)[5:-4].replace("_master", "")
        E = window_embeddings(w)
        if E is None or len(E) < 6:
            print(f"  [skip] {g}")
            continue
        np.save(os.path.join(REF_DIR, f"{g}.npy"), E)
        half = len(E) // 2
        null = kad(E[:half], E[half:])
        nulls[g] = round(null, 6) if null is not None else None
        print(f"  {g:16} {len(E)} windows, null KAD {nulls[g]}")
    json.dump(nulls, open(os.path.join(REF_DIR, "nulls.json"), "w"),
              indent=1)
    print(f"[drift] {len(nulls)} genre references -> {REF_DIR}")
    return 0


def check(wav, genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    ref_p = os.path.join(REF_DIR, f"{g}.npy")
    if not os.path.exists(ref_p):
        return {"ok": True, "skipped": f"no reference set for '{g}'"}
    ref = np.load(ref_p)
    cur = window_embeddings(wav)
    if cur is None or len(cur) < 3:
        return {"ok": True, "skipped": "too few audible windows"}
    d = kad(cur, ref)
    nulls = json.load(open(os.path.join(REF_DIR, "nulls.json")))
    null = float(nulls.get(g) or 0.001) or 0.001
    ratio = d / null
    out = {"ok": ratio <= 3.0, "kad": round(d, 6),
           "null": round(null, 6), "ratio": round(ratio, 2),
           "genre": g}
    if ratio > 3.0:
        out["why"] = (f"KAD {d:.4f} = {ratio:.1f}x the genre's own null "
                      f"({null:.4f}) — the take's sound DISTRIBUTION "
                      "has drifted from the ears-passed reference; "
                      "population drift, not one bad clip")
    return out


def selftest():
    fails = []
    funk = os.path.join(ROOT, "songs", "eval_funk.wav")
    amb = os.path.join(ROOT, "songs", "eval_ambient.wav")
    Ef = window_embeddings(funk)
    Ea = window_embeddings(amb)
    if Ef is None or Ea is None:
        print("[skip] CLAP unavailable")
        return 0
    half = len(Ef) // 2
    null = kad(Ef[:half], Ef[half:])
    cross = kad(Ef, Ea)
    print(f"funk self-split KAD {null:.5f}  funk-vs-ambient {cross:.5f}")
    if not (cross > 4 * max(null, 1e-6)):
        fails.append("cross-genre KAD does not dominate the null")
    r = check(funk, "funk")
    print("funk vs its own reference:", r)
    if not r.get("ok", False):
        fails.append("the winner drifted from itself")
    r2 = check(amb, "funk")
    print("ambient vs funk reference:", {k: r2.get(k) for k in
                                         ("ok", "ratio")})
    if r2.get("ok", True):
        fails.append("ambient passed as funk — the court is blind")
    for f in fails:
        print(f"[FAIL] {f}")
    print("drift_court selftest:",
          "ALL GREEN" if not fails else f"{len(fails)} RED")
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if cmd == "seed":
        sys.exit(seed())
    if cmd == "--selftest":
        sys.exit(selftest())
    if cmd == "check":
        print(json.dumps(check(sys.argv[2], sys.argv[3]), indent=1))
