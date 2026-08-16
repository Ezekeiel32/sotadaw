#!/usr/bin/env python3
"""THE BRAIN BR-D --real leg — THE COMPOSER PRIOR vs THE FLOOR (courts as judges).

20 briefs (genre x key x role) across the families. For each: the prior's
candidate vs a degree-uniform in-key random baseline (what un-learned
generation looks like), both judged by the SAME music courts (key + melody
advisories, symbolic). Reports pass rates + corpus-closeness (interval
distribution distance) honestly.

HONESTY LINE: this is the SYMBOLIC floor (courts). The full RELEASE-GATE
floor (rendered audio + taste head) is AMAZING PART III machinery — when it
assembles, THIS tool grows that leg; it does not pretend to have it today.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

BRIEFS = [
    ("uk garage", "F minor", "bass"), ("uk garage", "A minor", "lead"),
    ("deep house", "C major", "bass"), ("house", "G minor", "lead"),
    ("techno", "D minor", "bass"), ("trance", "E minor", "lead"),
    ("trap", "F minor", "lead"), ("drill", "C minor", "bass"),
    ("boombap", "Bb major", "lead"), ("memphis rap", "F minor", "bass"),
    ("funk", "E minor", "bass"), ("blues", "A major", "lead"),
    ("pop", "C major", "lead"), ("indie rock", "D major", "bass"),
    ("ambient", "F major", "pad"), ("psybient", "G minor", "lead"),
    ("dnb", "A minor", "bass"), ("2step", "E minor", "lead"),
    ("dub techno", "D minor", "pad"), ("amapiano", "C minor", "bass"),
]


def random_baseline(key, bars, role, seed):
    """Degree-uniform in-key notes on the 8th grid — un-learned generation."""
    import composer_prior as cp
    import theory
    k = theory.parse_key(key)
    scale = sorted(k["scale_pcs"])
    lo, hi = cp.TESSITURA.get(role, (48, 72))
    rng = random.Random(seed)
    notes = []
    beat = 0.0
    while beat < bars * 4.0:
        deg = rng.randrange(len(scale))
        octv = rng.randrange(lo // 12, hi // 12 + 1)
        pitch = octv * 12 + scale[deg]
        while pitch < lo:
            pitch += 12
        while pitch > hi:
            pitch -= 12
        notes.append({"start": round(beat, 4), "len": 0.5, "pitch": int(pitch),
                      "vel": round(rng.uniform(0.5, 1.0), 3)})
        beat += rng.choice((0.5, 0.5, 0.5, 1.0))
    return notes


def court_take(notes, genre, key, role):
    """Judge one candidate through the house courts. Returns (hard_ok,
    advisories) — hard = key court; advisories = melody court count."""
    import music_court as mc
    doc = {"version": 2, "bpm": 130, "key": key, "lengthBars": 4,
           "tracks": [{"name": {"bass": "bass", "lead": "lead",
                                "pad": "pad"}[role], "notes": notes}]}
    v = mc.run_courts(doc, genre, heal=False)
    kv = v.get("key") or {}
    hard_ok = bool(kv.get("ok", True))
    adv = 0
    for part in ("melody", "harmony"):
        pv = v.get(part) or {}
        adv += len(pv.get("flags") or pv.get("advisories") or [])
    return hard_ok, adv


def interval_hist(notes):
    h = [0] * 13
    ps = [n["pitch"] for n in sorted(notes, key=lambda n: n["start"])]
    for a, b in zip(ps, ps[1:]):
        h[min(12, abs(b - a))] += 1
    t = sum(h) or 1
    return [x / t for x in h]


def corpus_interval_hist(model_docs):
    """PER-LANE histograms by role. THE MIXTURE TRAP (measured twice): the
    pooled per-role marginal is multi-modal (octave-bass leads + stepwise
    leads), and NOTHING REAL looks like the average of all styles — but
    broad uniform-random does, so random L1-beat the prior against the
    pool. The honest meter is instance-to-nearest-instance: a candidate
    should look like SOME real lane."""
    import composer_prior as cp
    lanes = {r: [] for r in ("bass", "lead", "pad")}
    for doc, _g, _i in model_docs:
        for tr in doc.get("tracks") or []:
            role = cp.role_of(tr.get("name"))
            if role not in lanes:
                continue
            ns = [n for n in tr.get("notes") or []
                  if isinstance(n.get("pitch"), (int, float))]
            if len(ns) >= 16:
                lanes[role].append(interval_hist(ns))
    return lanes


def nearest_lane_dist(h, lane_hists):
    if not lane_hists:
        return None
    return min(l1(h, lh) for lh in lane_hists)


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE PRIOR vs THE FLOOR")
    ap.add_argument("--organ", choices=("markov", "cells"), default="markov",
                    help="markov = composer_prior (refused 2026-07-16); "
                         "cells = composer_cells (BR-D wave 2)")
    args = ap.parse_args()
    import composer_prior as cp
    if args.organ == "cells":
        import composer_cells as organ
    else:
        organ = cp
    model = organ.load_model()
    if model is None:
        print(f"no trained model — run the {args.organ} organ's train/mine first")
        return 2
    docs = cp.corpus_docs(cap=60)
    corpus_h = corpus_interval_hist(docs)
    rows = []
    for i, (genre, key, role) in enumerate(BRIEFS):
        cands = organ.generate(model, genre, key, 4, role, seed=100 + i, n=2)
        prior_notes = cands[0]["notes"] if cands else None
        base_notes = random_baseline(key, 4, role, seed=100 + i)
        row = {"brief": f"{genre}/{key}/{role}", "prior_generated": bool(cands)}
        role_lanes = corpus_h[role]
        if prior_notes:
            ok_p, adv_p = court_take(prior_notes, genre, key, role)
            row.update({"prior_key_ok": ok_p, "prior_advisories": adv_p,
                        "prior_corpus_dist": round(nearest_lane_dist(
                            interval_hist(prior_notes), role_lanes) or 9.9, 3)})
        ok_b, adv_b = court_take(base_notes, genre, key, role)
        row.update({"base_key_ok": ok_b, "base_advisories": adv_b,
                    "base_corpus_dist": round(nearest_lane_dist(
                        interval_hist(base_notes), role_lanes) or 9.9, 3)})
        rows.append(row)
        print(json.dumps(row))
    gen = [r for r in rows if r["prior_generated"]]
    n = len(gen)
    rep = {
        "organ": args.organ,
        "briefs": len(rows), "prior_yield": n,
        "prior_key_pass": sum(1 for r in gen if r["prior_key_ok"]),
        "base_key_pass": sum(1 for r in rows if r["base_key_ok"]),
        "prior_mean_advisories": round(sum(r["prior_advisories"] for r in gen)
                                       / max(n, 1), 2),
        "base_mean_advisories": round(sum(r["base_advisories"] for r in rows)
                                      / len(rows), 2),
        "prior_mean_corpus_dist": round(sum(r["prior_corpus_dist"] for r in gen)
                                        / max(n, 1), 3),
        "base_mean_corpus_dist": round(sum(r["base_corpus_dist"] for r in rows)
                                       / len(rows), 3),
        "honesty": "symbolic-courts floor; rendered RELEASE-GATE leg lands "
                   "with AMAZING PART III assembly",
    }
    print(json.dumps(rep, indent=1))
    musical_win = (rep["prior_mean_corpus_dist"] < rep["base_mean_corpus_dist"]
                   and rep["prior_mean_advisories"] <= rep["base_mean_advisories"])
    key_ok = n > 0 and rep["prior_key_pass"] == n
    print("VERDICT:", "PRIOR BEATS THE UN-LEARNED FLOOR" if (musical_win and key_ok)
          else "floor stands (honest)")
    return 0 if (musical_win and key_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
