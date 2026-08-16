#!/usr/bin/env python3
"""THE BRAIN BR-D rendered leg — B1's TRUE FLOOR LAW through THE RELEASE GATE.

SPEC_THE_BRAIN.md B1: the prior ships only if its candidates' RELEASE-GATE
pass-rate beats the un-learned baseline by >= 10 points on the 20-brief
blind suite, judged by the same gates. The gate assembled (release_gate.py)
— this grows the leg prior_floor.py's honesty line promised.

FAIRNESS LAW: both sides land on the SAME minimal bed (kick 4x4 + offbeat
hat, both rooted to the brief tonic so no key court noise), the SAME
staging (one fx_trim aim at the genre LUFS window mid + the fx_truepeak
wall), the SAME render rail, the SAME gate. Only the candidate lane
differs. A dry prior brief counts as a FAIL for the prior — refusal is
honest but it doesn't pass gates.

BUDGET LAW: hard render cap; a breach stops the suite with the honest gap
line and the partial tally — never a silent grind.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import budget_law as bl
import composer_cells as cc
import composer_prior as cp
import prior_floor as pf
import release_gate as rg

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
ROLE_VOICE = {"bass": "bass_warm", "lead": "pluck", "pad": "pad_evolve"}


def _rooted(target, root_pc):
    p = (target // 12) * 12 + root_pc
    return min((p - 12, p, p + 12), key=lambda x: abs(x - target))


def bed_song(genre, key, role, notes, bpm):
    import theory
    k = theory.parse_key(key)
    root = int(k["tonic_pc"]) if k else 0
    kick_p, hat_p = _rooted(36, root), _rooted(48, root)
    return {
        "version": 2, "bpm": float(bpm), "key": key, "lengthBars": 4,
        "masterGainDb": 0,
        "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
        "tracks": [
            {"name": "kick", "gainDb": -1.0, "pan": 0,
             "source": {"kind": "faust", "id": "kick_punch"},
             "notes": [{"start": float(b), "len": 0.2, "pitch": kick_p,
                        "vel": 0.95} for b in range(16)]},
            {"name": "hat", "gainDb": -10.0, "pan": 0.1,
             "source": {"kind": "faust", "id": "hat"},
             "notes": [{"start": b + 0.5, "len": 0.1, "pitch": hat_p,
                        "vel": 0.5} for b in range(16)]},
            {"name": role, "gainDb": -3.0 if role == "bass" else -6.0,
             "pan": 0,
             "source": {"kind": "faust", "id": ROLE_VOICE[role]},
             "notes": notes},
        ]}


def _render(doc, workdir, tag, budget):
    if not budget.allow("renders"):
        return None
    budget.spend("renders")
    sj = os.path.join(workdir, f"{tag}.json")
    wav = os.path.join(workdir, f"{tag}.wav")
    with open(sj, "w") as f:
        json.dump(doc, f)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True,
                       text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(wav):
        return None
    return sj, wav


def land_and_gate(genre, key, role, notes, bpm, target_lufs, workdir, tag,
                  budget):
    """Bed -> render -> one fx_trim aim at the window mid -> wall render ->
    THE GATE. Returns (passed, verdict-or-reason)."""
    import analyze2
    doc = bed_song(genre, key, role, notes, bpm)
    try:
        # THE BED RIDES THE COURT'S OWN HEALS (smoke 2026-07-16: a rigid
        # constant-vel grid is a toy — the groove court convicted EVERY
        # take on BOTH sides and the meter read nothing). Drum-lane heals
        # only; candidate lanes stay exactly what the organ emitted.
        import groove_court
        groove_court.court_groove(doc, genre, heal=True)
    except Exception:
        pass
    first = _render(doc, workdir, tag + "_raw", budget)
    if first is None:
        return False, "render failed or budget wall"
    if isinstance(target_lufs, (int, float)):
        try:
            lufs = analyze2.analyze(first[1]).get("lufs_integrated")
        except Exception:
            lufs = None
        if isinstance(lufs, (int, float)):
            trim = max(-24.0, min(24.0, target_lufs - lufs))
            doc["master"] = [
                {"id": "fx_trim", "params": {"level": round(trim, 2)}},
                {"id": "fx_truepeak", "params": {"ceiling": -1.2}}]
    landed = _render(doc, workdir, tag, budget)
    if landed is None:
        return False, False, ["landing render failed or budget wall"]
    v = rg.gate_take(landed[0], wav=landed[1], genre=genre, root=ROOT,
                     render=False)
    g = v.get("gates") or {}
    why = ((g.get("census") or {}).get("hard", [])
           + (g.get("reference") or {}).get("hard", []))
    if (g.get("taste") or {}).get("state") == "fail":
        why.append("taste reject")
    if (g.get("novelty") or {}).get("state") == "fail":
        why.append("novelty theft")
    # structural = G1/G2/G4 — taste's bank is 8 rows deep today; its verdict
    # counts in the FULL law but the structural rate keeps the meter legible
    ok_struct = (bool((g.get("census") or {}).get("pass"))
                 and bool((g.get("reference") or {}).get("pass"))
                 and (g.get("novelty") or {}).get("state") != "fail")
    return bool(v.get("pass")), ok_struct, (why or ["pass"])


def main():
    ap = argparse.ArgumentParser(description="B1 FLOOR LAW, rendered")
    ap.add_argument("--organ", choices=("cells", "markov"), default="cells")
    ap.add_argument("--briefs", type=int, default=20)
    ap.add_argument("--seed-base", type=int, default=200)
    a = ap.parse_args()
    if not os.path.exists(M1):
        print("m1 binary missing — build first")
        return 2
    organ = cc if a.organ == "cells" else cp
    model = organ.load_model()
    if model is None:
        print(f"no trained {a.organ} model")
        return 2
    budget = bl.Budget("prior_gate_floor",
                       caps={"renders": 6 * a.briefs, "seconds": 3600,
                             "orders": 10_000})
    briefs = pf.BRIEFS[:a.briefs]
    rows, p_pass, b_pass, ps_pass, bs_pass = [], 0, 0, 0, 0
    with tempfile.TemporaryDirectory(prefix="pgf_") as wd:
        for i, (genre, key, role) in enumerate(briefs):
            gold, _gn = rg.gold_for(genre, ROOT)
            mt = (gold or {}).get("mixtarget") or {}
            bpm = (mt["bpm_lo"] + mt["bpm_hi"]) / 2.0 \
                if isinstance(mt.get("bpm_lo"), (int, float)) else 124.0
            target = (mt["lufs_lo"] + mt["lufs_hi"]) / 2.0 \
                if isinstance(mt.get("lufs_lo"), (int, float)) else None
            cands = organ.generate(model, genre, key, 4, role,
                                   seed=a.seed_base + i, n=1)
            if cands:
                ok_p, st_p, why_p = land_and_gate(
                    genre, key, role, cands[0]["notes"], bpm, target, wd,
                    f"p{i}", budget)
            else:
                ok_p, st_p = False, False
                why_p = ["prior dry (refused) — counts as fail"]
            ok_b, st_b, why_b = land_and_gate(
                genre, key, role,
                pf.random_baseline(key, 4, role, seed=a.seed_base + i),
                bpm, target, wd, f"b{i}", budget)
            p_pass += ok_p
            b_pass += ok_b
            ps_pass += st_p
            bs_pass += st_b
            row = {"brief": f"{genre}/{key}/{role}",
                   "prior": {"pass": ok_p, "structural": st_p,
                             "why": why_p[:3]},
                   "base": {"pass": ok_b, "structural": st_b,
                            "why": why_b[:3]}}
            rows.append(row)
            print(json.dumps(row))
            if budget.breaches:
                print(f"BUDGET WALL: {budget.gap_line()} — partial tally is "
                      f"the honest tally")
                break
    n = len(rows)
    delta = (p_pass - b_pass) * 100.0 / max(n, 1)
    sdelta = (ps_pass - bs_pass) * 100.0 / max(n, 1)
    rep = {"organ": a.organ, "briefs": n,
           "prior_pass": p_pass, "base_pass": b_pass,
           "prior_rate": round(p_pass / max(n, 1), 3),
           "base_rate": round(b_pass / max(n, 1), 3),
           "delta_points": round(delta, 1),
           "structural": {"prior_pass": ps_pass, "base_pass": bs_pass,
                          "delta_points": round(sdelta, 1),
                          "why": "G1/G2/G4 only — the taste bank is 8 rows "
                                 "deep today; full law is the verdict"},
           "floor_law": "prior must beat baseline by >= 10 points",
           "budget": {"renders_spent": budget.spent.get("renders", 0),
                      "breaches": budget.breaches}}
    print(json.dumps(rep, indent=1))
    print("VERDICT:", "B1 FLOOR LAW MET — mount rights earned"
          if delta >= 10.0 else "floor stands (honest)")
    return 0 if delta >= 10.0 else 1


if __name__ == "__main__":
    sys.exit(main())
