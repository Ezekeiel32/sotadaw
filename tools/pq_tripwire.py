#!/usr/bin/env python3
"""THE PQ TRIPWIRE — wave 94 (r-19 items 217 + 218): Audiobox-
Aesthetics PQ (CC-BY 4.0, license-verified) as a CHEAP production-
quality tripwire — never a target. Two laws bind it:

  217 TRIPWIRE-ONLY   PQ gates nothing and optimizes nothing; a take
                      under its genre floor gets ONE advisory line.
                      (Optimizing a learned metric = Goodhart; the
                      MUSHRA-lite harness watches for exactly that.)
  218 CONTENT-BIAS    learned metrics favor punchy electronic material
                      and punish sparse/lo-fi/ambient — floors are
                      PER-GENRE, born from the house's own corpus
                      (eval winners), floor = genre_mean - 1.0.

  seed      score the eval corpus -> library/pq_floors.json
  score     one wav -> the four axes (CE/CU/PC/PQ)
  check     wav + genre -> tripwire verdict vs the genre floor
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOORS = os.path.join(ROOT, "library", "pq_floors.json")
MARGIN = 1.0


def _predictor():
    from audiobox_aesthetics.infer import initialize_predictor
    return initialize_predictor()


def _duration_s(path):
    import wave as wv
    try:
        w = wv.open(path, "rb")
        d = w.getnframes() / w.getframerate()
        w.close()
        return d
    except Exception:
        return 0.0


def score(paths, chunk_s=30.0):
    """THE CHUNK LAW (sing.py's lesson, again): WavLM's attention is
    O(T^2) — a 2-minute wav asks 6.5GB and the 5.7GB GPU dies. Long
    files score in 30s windows, axes averaged."""
    import tempfile
    import wave as wv
    p = _predictor()
    out = []
    for x in paths:
        d = _duration_s(x)
        if d <= chunk_s * 1.5:
            out.append(p.forward([{"path": x}])[0])
            continue
        w = wv.open(x, "rb")
        sr, sw, ch = w.getframerate(), w.getsampwidth(), w.getnchannels()
        n = int(sr * chunk_s)
        tmp = tempfile.mkdtemp(prefix="pq_")
        parts = []
        i = 0
        while True:
            raw = w.readframes(n)
            if len(raw) < n * sw * ch // 2:
                break
            cp = os.path.join(tmp, f"c{i}.wav")
            o = wv.open(cp, "wb")
            o.setnchannels(ch)
            o.setsampwidth(sw)
            o.setframerate(sr)
            o.writeframes(raw)
            o.close()
            parts.append(cp)
            i += 1
        w.close()
        rows = p.forward([{"path": c} for c in parts]) if parts else []
        for c in parts:
            os.remove(c)
        if not rows:
            out.append(p.forward([{"path": x}])[0])
            continue
        avg = {k: sum(float(r[k]) for r in rows) / len(rows)
               for k in rows[0]}
        out.append(avg)
    return out


def seed():
    import glob
    wavs = sorted(glob.glob(os.path.join(ROOT, "songs", "eval_*.wav")))
    if not wavs:
        print("no eval corpus on this box")
        return 1
    rows = score(wavs)
    floors = {}
    for w, r in zip(wavs, rows):
        g = os.path.basename(w)[5:-4].replace("_master", "")
        floors[g] = {"pq_mean": round(float(r["PQ"]), 2),
                     "floor": round(float(r["PQ"]) - MARGIN, 2)}
    default = sorted(v["floor"] for v in floors.values())
    floors["_default"] = {"floor": round(default[len(default) // 4], 2),
                          "note": "p25 of the corpus floors — unbanked "
                                  "genres get the lenient quartile"}
    floors["_law"] = ("TRIPWIRE ONLY (item 217): never optimized, never "
                      "a gate; per-genre floors (item 218) because "
                      "learned metrics punish sparse/ambient material; "
                      "mushra_lite watches for proxy drift")
    json.dump(floors, open(FLOORS, "w"), indent=1)
    print(f"[pq] {len(floors) - 2} genre floors -> {FLOORS}")
    for g, v in sorted(floors.items()):
        if not g.startswith("_"):
            print(f"  {g:16} mean {v['pq_mean']:.2f} floor {v['floor']:.2f}")
    return 0


def floor_for(genre):
    try:
        fl = json.load(open(FLOORS))
    except Exception:
        return None
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    for k, v in fl.items():
        if k.startswith("_"):
            continue
        if k in g or g in k:
            return v["floor"]
    return fl.get("_default", {}).get("floor")


def check(wav, genre):
    fl = floor_for(genre)
    if fl is None:
        return {"ok": True, "skipped": "no floors seeded"}
    r = score([wav])[0]
    pq = float(r["PQ"])
    out = {"ok": pq >= fl, "pq": round(pq, 2), "floor": fl,
           "genre": genre, "axes": {k: round(float(v), 2)
                                    for k, v in r.items()}}
    if pq < fl:
        out["why"] = (f"PQ {pq:.2f} under the {genre} floor {fl:.2f} "
                      "(corpus-born, bias-corrected) — a tripwire "
                      "LINE, not a gate: listen before believing "
                      "either way")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if cmd == "seed":
        sys.exit(seed())
    if cmd == "score":
        print(json.dumps(score(sys.argv[2:]), indent=1, default=float))
    elif cmd == "check":
        print(json.dumps(check(sys.argv[2],
                               sys.argv[3] if len(sys.argv) > 3
                               else ""), indent=1))
