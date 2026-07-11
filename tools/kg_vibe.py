#!/usr/bin/env python3
"""kg_vibe.py — SEMANTIC GENRE ROUTING (pass 5): vibe words -> the graph's
nearest genres, via MiniLM sentence embeddings stored on the Genre nodes.

The literal routers (start_session tag match, the sidecar's dna-seed substring
match) only fire when the ask NAMES a genre; "give me smoky late night jazz
bar energy" routed nowhere. This embeds every Genre as SHORT caption variants
("<name> music", "<name> music, <family> style, <bpm> bpm") and KNNs any vibe
phrase against them.

MEASURED DESIGN (2026-07-10, probes in the battery):
- Model: sentence-transformers/all-MiniLM-L6-v2 through the ALREADY-INSTALLED
  transformers stack (Apache-2.0, 22M params, ~3s load — no new package).
  CLAP was tried first and REJECTED for this job: its text tower matches
  captions to AUDIO, so caption<->caption cosine is muddy ("warehouse rave" ->
  shoegaze). MiniLM's world knowledge carries the genre names instead
  ("lofi study beats" -> lofi 0.73).
- MINIMAL texts win: technique-name/desc-enriched texts DILUTED the genre
  signal (production jargon is not a vibe). Bare names (no "music") are
  hubness noise — dropped.
- Multi-vector max-sim over the 2 variants; scores are cosine similarity.
- KNOWN LIMIT: heavy filler ("sad mellow X with vinyl crackle") can drown a
  short query's genre term by ~0.01-0.02 — top score < WEAK_BELOW ships
  "weak": true and callers treat the route as advisory.

Rails: kg/vibe_vecs.npz (PRIMARY query rail: exact multi-vector, instant) +
Genre.vibe_vec vecf32 attr + vector index in FalkorDB (durable store, single-
variant graph-side fallback + genre<->genre similarity for graph queries).

  kg_vibe.py --seed                  embed genres -> graph attrs + index + npz
  kg_vibe.py "<vibe text>" [--k 5]   VIBE_JSON {"available":true,"results":[..],
                                     "weak":bool}
  kg_vibe.py --selftest              degrade contract (no model needed)

Graceful: model/graph unavailable -> VIBE_JSON {"available":false,...} exit 3
(callers MUST degrade to the literal path, never crash).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
NPZ = os.path.join(ROOT, "kg", "vibe_vecs.npz")
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384
WEAK_BELOW = 0.35


def _fail(reason):
    print("VIBE_JSON " + json.dumps({"available": False, "reason": reason}))
    return 3


_MSTATE = {}


def _embed(texts):
    """Mean-pooled, L2-normalized MiniLM embeddings (the model's documented
    recipe), model memoized per process. Raises on any unavailability —
    callers map to the degrade line."""
    import torch
    from transformers import AutoTokenizer, AutoModel
    if "tok" not in _MSTATE:
        _MSTATE["tok"] = AutoTokenizer.from_pretrained(MODEL)
        _MSTATE["mdl"] = AutoModel.from_pretrained(MODEL)
        _MSTATE["mdl"].eval()
    tok, mdl = _MSTATE["tok"], _MSTATE["mdl"]
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), 64):
            b = tok(texts[i:i + 64], padding=True, truncation=True,
                    return_tensors="pt")
            h = mdl(**b).last_hidden_state
            m = b["attention_mask"].unsqueeze(-1).float()
            v = (h * m).sum(1) / m.sum(1)
            out.append(torch.nn.functional.normalize(v, dim=1))
    return torch.cat(out).numpy().astype("float32")


def genre_variants():
    """[(genre, [caption variants])] — minimal, measured (see header)."""
    from kg import KG
    rows = KG().g.query(
        "MATCH (n:Genre) RETURN n.name, n.form_family, n.bpm_lo, n.bpm_hi").result_set
    out = []
    for n, fam, lo, hi in rows:
        w = str(n).replace("_", " ")
        rich = (f"{w} music" + (f", {fam} style" if fam else "")
                + (f", {int(lo)}-{int(hi)} bpm" if lo and hi else ""))
        out.append((str(n), sorted({f"{w} music", rich})))
    return out


def seed():
    import numpy as np
    try:
        pairs = genre_variants()
    except Exception as e:
        return _fail(f"graph unavailable: {type(e).__name__}")
    if not pairs:
        return _fail("no Genre nodes in the graph")
    flat, owner = [], []
    for i, (_, vs) in enumerate(pairs):
        for v in vs:
            flat.append(v)
            owner.append(i)
    try:
        vecs = _embed(flat)
    except Exception as e:
        return _fail(f"MiniLM unavailable: {type(e).__name__}")
    from kg import KG
    g = KG().g
    for i, (name, vs) in enumerate(pairs):
        # the graph carries the "<name> music" variant (durable, graph-side sim)
        j = next(k for k in range(len(flat))
                 if owner[k] == i and flat[k].endswith(" music"))
        lit = ", ".join(f"{x:.6f}" for x in vecs[j].tolist())
        g.query("MATCH (n:Genre {name: '%s'}) SET n.vibe_vec = vecf32([%s])"
                % (name.replace("'", "\\'"), lit))
    mk = ("CREATE VECTOR INDEX FOR (n:Genre) ON (n.vibe_vec) "
          "OPTIONS {dimension: %d, similarityFunction: 'cosine'}" % DIM)
    try:
        g.query(mk)
    except Exception as e:
        if "already indexed" not in str(e) and "already exists" not in str(e):
            raise
        # a prior seed may have indexed a DIFFERENT dimension (the CLAP-era
        # 512 index over MiniLM 384 vectors broke queryNodes) — rebuild it
        g.query("DROP VECTOR INDEX FOR (n:Genre) ON (n.vibe_vec)")
        g.query(mk)
    os.makedirs(os.path.dirname(NPZ), exist_ok=True)
    np.savez(NPZ, ids=np.array([n for n, _ in pairs]),
             vecs=vecs, owner=np.array(owner, dtype="int32"))
    print(f"[kg_vibe] seeded {len(pairs)} genres ({len(flat)} caption vectors) "
          f"-> graph + {os.path.relpath(NPZ, ROOT)}")
    return 0


def query(text, k=5):
    try:
        qv = _embed([str(text)])[0]
    except Exception as e:
        return _fail(f"MiniLM unavailable: {type(e).__name__}")
    results = None
    try:                                    # PRIMARY: npz multi-vector max-sim
        import numpy as np
        d = np.load(NPZ, allow_pickle=True)
        sims = d["vecs"] @ qv
        best = {}
        for j, o in enumerate(d["owner"]):
            if sims[j] > best.get(int(o), -9.0):
                best[int(o)] = float(sims[j])
        top = sorted(best.items(), key=lambda kv: -kv[1])[:int(k)]
        results = [{"genre": str(d["ids"][o]), "score": round(s, 4)}
                   for o, s in top]
    except Exception:
        pass
    if not results:                         # fallback: graph single-vector KNN
        try:
            from kg import KG
            lit = ", ".join(f"{x:.6f}" for x in qv.tolist())
            res = KG().g.query(
                "CALL db.idx.vector.queryNodes('Genre', 'vibe_vec', %d, vecf32([%s])) "
                "YIELD node, score RETURN node.name, score" % (int(k), lit))
            results = [{"genre": str(n), "score": round(1.0 - float(s), 4)}
                       for n, s in res.result_set]
        except Exception:
            return _fail("no npz and no graph index — run kg_vibe.py --seed")
    weak = not results or results[0]["score"] < WEAK_BELOW
    print("VIBE_JSON " + json.dumps({"available": True, "query": str(text),
                                     "weak": weak, "results": results}))
    return 0


def selftest():
    """Degrade contract, zero model deps: the jail flag must yield the machine
    not-available line + exit 3, never a traceback."""
    import subprocess
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "x",
                        "--model-jail"], capture_output=True, text=True)
    ok = r.returncode == 3 and '"available": false' in r.stdout
    print("SELFTEST " + ("PASS" if ok else
                         f"FAIL rc={r.returncode} out={r.stdout[:200]}"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", default=None)
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--model-jail", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.model_jail:                        # selftest hook: force the degrade path
        return _fail("model jailed (selftest)")
    if a.selftest:
        return selftest()
    if a.seed:
        return seed()
    if not a.text:
        ap.print_help()
        return 2
    return query(a.text, a.k)


if __name__ == "__main__":
    sys.exit(main())
