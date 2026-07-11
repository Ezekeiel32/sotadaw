#!/usr/bin/env python3
"""clap_query.py — SEMANTIC EARS query (V53).

Embed a text query with CLAP and rank the library/embeddings.npz index by
cosine. Prints JSON:
  {"available":true,"query":..,"results":[{id,kind,name,path,category,score}..]}
On any unavailability prints {"available":false,"reason":..} and exits 3, so
callers (daw_mcp search_library) fall back to substring — never an error.

  clap_query.py "<text>" [--k N] [--kinds kit,preset,sample,song]
  clap_query.py --audio <wav>                       # library neighbors of a sound
  clap_query.py --sim "<text>" --audio a.wav [b..]  # direct text<->audio cosine
                                                    # (C5 s5: the judge's ears) —
                                                    # scores in INPUT ORDER, null
                                                    # for unreadable/silent wavs
  clap_query.py --ab gen.wav --refs r1 r2 ...       # R3 real-record ruler kernel:
                                                    # multi-window embeddings;
                                                    # gen_insiderness = mean cos(gen,
                                                    # refs); baseline[i] = leave-one-
                                                    # out mean cos(ref_i, others)
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=None)
    ap.add_argument("--audio", nargs="+", default=None,
                    help="rank library neighbors of this wav; with --sim, the wav(s) to score")
    ap.add_argument("--sim", default=None,
                    help="direct text<->audio similarity for each --audio wav (no index needed)")
    ap.add_argument("--ab", default=None, metavar="GEN_WAV",
                    help="R3 ruler: insiderness of GEN_WAV vs --refs real records")
    ap.add_argument("--refs", nargs="+", default=None,
                    help="reference record audio files for --ab")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--kinds", default="")
    a = ap.parse_args()
    if not a.query and not a.audio and not a.ab:
        print(json.dumps({"available": False, "reason": "need a text query or --audio <wav>"}))
        return 2

    import clap_embed
    if not clap_embed.available():
        print(json.dumps({"available": False, "reason": "clap unavailable"}))
        return 3

    if a.ab:                                                # R3 REAL-RECORD RULER kernel
        if not a.refs or len(a.refs) < 3:
            print(json.dumps({"available": False,
                              "reason": "--ab needs --refs with >=3 record files"}))
            return 2
        try:
            import numpy as np
            V = clap_embed.embed_audio_multiwindow([a.ab] + list(a.refs))
            g, R = V[0], V[1:]
            if not np.abs(g).any():
                print(json.dumps({"available": False,
                                  "reason": f"unreadable/silent: {a.ab}"}))
                return 3
            live = [i for i in range(len(R)) if np.abs(R[i]).any()]
            if len(live) < 3:
                print(json.dumps({"available": False,
                                  "reason": "fewer than 3 readable refs"}))
                return 3
            R = R[live]
            gen_ins = float((R @ g).mean())
            base = []
            for i in range(len(R)):
                others = np.delete(R, i, axis=0)
                base.append(float((others @ R[i]).mean()))
            print(json.dumps({"available": True, "gen": a.ab,
                              "refs": [a.refs[i] for i in live],
                              "gen_insiderness": round(gen_ins, 4),
                              "baseline": [round(b, 4) for b in base],
                              "ref_cos": [round(float(R[i] @ g), 4)
                                          for i in range(len(R))]}))
            return 0
        except Exception as e:
            print(json.dumps({"available": False, "reason": f"ab failed: {e!r}"}))
            return 3

    if a.sim:                                               # DIRECT text<->audio cosine (C5 s5)
        if not a.audio:
            print(json.dumps({"available": False, "reason": "--sim needs --audio <wav ...>"}))
            return 2
        try:
            import numpy as np
            t = clap_embed.embed_texts([a.sim])[0]
            av = clap_embed.embed_audio(a.audio)            # one load scores all wavs
            sims = [{"path": p,
                     "score": (round(float(av[i] @ t), 4) if np.abs(av[i]).any() else None)}
                    for i, p in enumerate(a.audio)]         # INPUT order; null = unreadable
            print(json.dumps({"available": True, "text": a.sim, "similarities": sims}))
            return 0
        except Exception as e:
            print(json.dumps({"available": False, "reason": f"sim failed: {e!r}"}))
            return 3

    import embed_library
    ids, vecs, meta = embed_library.load_index()
    if len(ids) == 0:
        print(json.dumps({"available": False,
                          "reason": "no index (run tools/embed_library.py)"}))
        return 3

    try:
        import numpy as np
        import os as _os
        if a.audio:                                         # AUDIO -> nearest library neighbors
            av = clap_embed.embed_audio(a.audio[:1])
            if not np.abs(av).any():
                print(json.dumps({"available": False,
                                  "reason": f"unreadable/silent audio: {a.audio[0]}"}))
                return 3
            q = av[0]
            self_path = _os.path.abspath(a.audio[0])
            label = "audio:" + _os.path.basename(a.audio[0])
        else:                                               # TEXT
            q = clap_embed.embed_texts([a.query])[0]
            self_path, label = None, a.query
        sims = vecs @ q                                     # (N,)
        want = set(k.strip() for k in a.kinds.split(",") if k.strip())
        order = np.argsort(-sims)
        results = []
        for j in order:
            m = meta.get(ids[j], {})
            if want and m.get("kind") not in want:
                continue
            if self_path and m.get("path") and _os.path.abspath(m["path"]) == self_path:
                continue                                    # never return the query itself
            results.append({
                "id": ids[j], "kind": m.get("kind"), "name": m.get("name"),
                "path": m.get("path"), "category": m.get("category"),
                "score": round(float(sims[j]), 4),
            })
            if len(results) >= a.k:
                break
        print(json.dumps({"available": True, "query": label, "results": results}))
        return 0
    except Exception as e:
        print(json.dumps({"available": False, "reason": f"query failed: {e!r}"}))
        return 3


if __name__ == "__main__":
    sys.exit(main())
