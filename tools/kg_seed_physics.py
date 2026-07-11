#!/usr/bin/env python3
"""E12 THE PHYSICS CIRCLE — bench + null verdicts flow into the graph.

Two weaves (idempotent MERGE, provenance on every node — S6 law):
  1. BenchCert nodes: one per instruments/certs/*.cert.json — the measured identity
     of a voice/fx (FR/THD/alias/noise/latency + verdict pass flags + cert sha).
     Linked BenchCert-[:CERTIFIES]->SoundRecipe where names coincide; else the
     cert node stands alone as a durable measured fact skills can query.
  2. psr_floor on MixTargets (E6 THE DYNAMICS FLOOR): per-genre PSR floor from
     published mastering practice (MeterPlugs PSR guidance + streaming-normalized
     dynamics discourse). Provenance marks it seed/D3-pending — Chezy may replace
     with crate-measured floors; a KG floor always wins at read time (dynamics_ears).

usage: kg_seed_physics.py [--dry]   (--dry prints, writes nothing)
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERTS = os.path.join(ROOT, "instruments", "certs")
sys.path.insert(0, os.path.join(ROOT, "tools"))

PROV = "physics:claude/2026-07-06-THE_PHYSICS-E12"

# The PSR floor numbers live in ONE place — tools/psr_floors.py (D6 no-spaghetti).
# This seeder WRITES them onto MixTargets; dynamics_ears READS them back. No table here.
import psr_floors                                                            # noqa: E402


def floor_for(mix_name):
    """The seed value for a MixTarget (named <genre>_mix). None = no seed match
    (leave it to the read-time default; never write a guessed floor)."""
    return psr_floors.seed_floor(mix_name.lower().replace("_mix", ""))


def headline(cert):
    keys = ("kind", "dsp_sha", "m1_md5", "latency_samples", "gd_ms",
            "fr_mean_db_100_10k", "fr_std_db_100_10k", "alias_dbc_worst",
            "noise_dbfs", "peak_dbfs", "clipped_samples", "sustain_centroid_hz",
            "decay_to_m60_s", "attack_ms")
    out = {k: cert[k] for k in keys if k in cert and cert[k] is not None}
    v = cert.get("verdicts") or {}
    out["verdicts_pass"] = all(bool(x) for x in v.values()) if v else None
    out["verdict_detail"] = json.dumps(v) if v else None
    return out


def main():
    dry = "--dry" in sys.argv
    if not os.path.isdir(CERTS):
        print("no certs — run dsp_bench.py cert --all first")
        return 1
    kg = None
    if not dry:
        import kg as kgmod
        kg = kgmod.KG()
        recipe_names = {r[0] for r in kg.q("MATCH (s:SoundRecipe) RETURN s.name")}
        mix_names = [r[0] for r in kg.q("MATCH (m:MixTarget) RETURN m.name")]
    else:
        recipe_names, mix_names = set(), []

    # 1. BenchCert nodes
    n_cert, n_link = 0, 0
    for f in sorted(os.listdir(CERTS)):
        if not f.endswith(".cert.json"):
            continue
        cert = json.load(open(os.path.join(CERTS, f)))
        name = cert["name"]
        cert_sha = hashlib.sha256(
            open(os.path.join(CERTS, f), "rb").read()).hexdigest()[:16]
        attrs = headline(cert)
        attrs["cert_sha"] = cert_sha
        attrs["voice"] = name
        node = f"cert_{name}"
        if dry:
            print(f"[cert] {node}: {json.dumps(attrs)[:120]}")
        else:
            kg.upsert("BenchCert", node, PROV, **attrs)
            if name in recipe_names:
                kg.link("BenchCert", node, "CERTIFIES", "SoundRecipe", name)
                n_link += 1
        n_cert += 1

    # 2. psr_floor on MixTargets
    n_floor = 0
    for mix in mix_names or ([] if not dry else []):
        fl = floor_for(mix)
        if fl is None:
            continue
        if dry:
            print(f"[floor] {mix}: psr_floor={fl}")
        else:
            kg.upsert("MixTarget", mix, PROV + " (psr_floor=seed:published-practice/D3-pending)",
                      psr_floor=fl, psr_floor_source="seed:published-practice/D3-pending")
        n_floor += 1
    if dry:
        # dry can't read the graph; show the seed table coverage instead
        print(f"[dry] would write {n_cert} BenchCert nodes; psr_floors from "
              f"{len(psr_floors.SEED_PSR_FLOORS)} genre keys")
        return 0

    print(f"[kg-physics] {n_cert} BenchCert nodes ({n_link} CERTIFIES links) + "
          f"{n_floor} MixTarget psr_floors — provenance {PROV}")
    # proof read-back
    bc = kg.q("MATCH (n:BenchCert) RETURN count(n)")[0][0]
    fl = kg.q("MATCH (m:MixTarget) WHERE m.psr_floor IS NOT NULL RETURN count(m)")[0][0]
    print(f"[verify] graph now holds {bc} BenchCert nodes, {fl} MixTargets with psr_floor")
    sample = kg.q("MATCH (n:BenchCert {name:'cert_fx_truepeak'}) RETURN properties(n)")
    if sample:
        p = sample[0][0]
        print(f"[verify] cert_fx_truepeak: fr_mean={p.get('fr_mean_db_100_10k')} "
              f"alias={p.get('alias_dbc_worst')} latency={p.get('latency_samples')} "
              f"pass={p.get('verdicts_pass')}")
    return 0


def ingest_verdicts(dry=False):
    """E12: fold telemetry/null_verdicts.jsonl (written live by the sidecar's audio
    court) into KG NullVerdict nodes — one per song, verified/total counts + last
    claim. The physics circle's telemetry->graph leg, mirroring kg_ingest_telemetry."""
    path = os.path.join(ROOT, "telemetry", "null_verdicts.jsonl")
    if not os.path.exists(path):
        print("[verdicts] no telemetry/null_verdicts.jsonl yet (run a proposal with "
              "SOTADAW_AUDIO_RECEIPTS=1)")
        return 0
    agg = {}
    for line in open(path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        song = r.get("song") or "?"
        a = agg.setdefault(song, {"total": 0, "verified": 0, "last_claim": [],
                                  "last_oos": []})
        a["total"] += 1
        a["verified"] += 1 if r.get("audio_verified") else 0
        a["last_claim"] = r.get("claim", [])
        a["last_oos"] = r.get("out_of_scope", [])
    if dry:
        print(f"[dry] would write {len(agg)} NullVerdict nodes: "
              + ", ".join(f"{s}({a['verified']}/{a['total']})" for s, a in agg.items()))
        return 0
    import kg as kgmod
    kg = kgmod.KG()
    for song, a in agg.items():
        kg.upsert("NullVerdict", f"nv_{song}", PROV,
                  song=song, total=a["total"], verified=a["verified"],
                  last_claim=json.dumps(a["last_claim"]),
                  last_out_of_scope=json.dumps(a["last_oos"]),
                  audio_proven_rate=round(a["verified"] / max(1, a["total"]), 3))
    n = kg.q("MATCH (n:NullVerdict) RETURN count(n)")[0][0]
    print(f"[verdicts] {len(agg)} songs -> KG; graph now holds {n} NullVerdict nodes")
    return 0


if __name__ == "__main__":
    if "--verdicts" in sys.argv:
        sys.exit(ingest_verdicts("--dry" in sys.argv))
    sys.exit(main())
