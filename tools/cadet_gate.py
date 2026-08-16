#!/usr/bin/env python3
"""THE BRAIN BR-E — THE CADET GATE (docs/SPEC_THE_BRAIN.md PART II B5).

The graduation contract for any small model that wants a routing rung:
TIER-INVARIANCE — its gate-pass rate on a blind brief suite must sit within
TOLERANCE (5%) of the reference tier's. Until it graduates, it rides shotgun
(logged, never routed).

This module is the JUDGE, not the trainer:
- readiness(): how far the training bank (telemetry/brain_tuples.jsonl,
  BR-A's CIRCLE) is from the cadet's data floor — honest counts, no hope.
- graduate(cand_results, ref_results): the pure verdict over paired brief
  outcomes [{brief, passed}] — pass-rate delta + a McNemar-style discordance
  check so 10 lucky briefs can't graduate anyone.
- verdict_from_eval(): reads eval/history.jsonl rows (the real brief ledger,
  'model' field when present) and judges any two tiers found there —
  "insufficient evidence" is a first-class answer.

LAW: graduation is decided by THIS resolver only; the pick_model ladder may
mount a cadet rung ONLY behind a persisted graduation certificate
(telemetry/cadet_cert.json) minted here. No certificate, no rung.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

TOLERANCE = 0.05          # tier-invariance band (the spec's 5%)
MIN_BRIEFS = 20           # blind suite floor
DATA_FLOORS = {"D13": 200}  # banked tuples before training even starts
CERT_NAME = "cadet_cert.json"


def cert_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", CERT_NAME)


def readiness(root=None):
    """The honest distance to the cadet's data floor."""
    try:
        import brain_ledger
        led = brain_ledger.ledger(root)
        ok, misses = brain_ledger.check_floors(DATA_FLOORS, led, root)
        return {"ready_to_train": ok, "misses": misses,
                "banked_tuples": (led.get("D13") or {}).get("count", -1),
                "floor": DATA_FLOORS["D13"]}
    except Exception as e:
        return {"ready_to_train": False, "misses": [f"ledger unavailable: {e!r}"],
                "banked_tuples": -1, "floor": DATA_FLOORS["D13"]}


def graduate(cand_results, ref_results, tolerance=TOLERANCE, min_briefs=MIN_BRIEFS):
    """Pure verdict. cand/ref = [{brief, passed}] on the SAME brief set.
    Graduates only when (1) >= min_briefs paired briefs, (2) pass-rate within
    tolerance, (3) the discordant pairs don't contradict invariance (a sign
    test at ~95%: the cadet may not lose significantly more head-to-heads)."""
    cand = {str(r.get("brief")): bool(r.get("passed")) for r in cand_results or []}
    ref = {str(r.get("brief")): bool(r.get("passed")) for r in ref_results or []}
    briefs = sorted(set(cand) & set(ref))
    rep = {"paired_briefs": len(briefs), "graduated": False}
    if len(briefs) < min_briefs:
        rep["why"] = (f"insufficient evidence: {len(briefs)} paired briefs "
                      f"< {min_briefs} — the suite decides, not hope")
        return rep
    c_pass = sum(1 for b in briefs if cand[b])
    r_pass = sum(1 for b in briefs if ref[b])
    delta = (r_pass - c_pass) / len(briefs)
    lose = sum(1 for b in briefs if ref[b] and not cand[b])   # cadet-only misses
    win = sum(1 for b in briefs if cand[b] and not ref[b])
    rep.update({"cand_pass_rate": round(c_pass / len(briefs), 4),
                "ref_pass_rate": round(r_pass / len(briefs), 4),
                "delta": round(delta, 4), "cand_only_wins": win,
                "ref_only_wins": lose})
    if delta > tolerance:
        rep["why"] = f"pass-rate gap {delta:.1%} > tolerance {tolerance:.0%}"
        return rep
    n_disc = win + lose
    if n_disc > 0:
        # one-sided sign test: P(losses >= lose | p=0.5); graduate only if
        # the discordance is explainable by chance
        p = sum(math.comb(n_disc, k) for k in range(lose, n_disc + 1)) / (2 ** n_disc)
        rep["sign_test_p"] = round(p, 4)
        if p < 0.05:
            rep["why"] = (f"discordant head-to-heads contradict invariance "
                          f"(cadet loses {lose}/{n_disc}, p={p:.3f})")
            return rep
    rep["graduated"] = True
    return rep


def mint(rep, cand_tier, ref_tier, root=None):
    """Persist the certificate the routing ladder requires. Refuses to mint
    a non-graduated report."""
    if not rep.get("graduated"):
        return None
    doc = {"t": round(time.time(), 1), "cand": str(cand_tier),
           "ref": str(ref_tier), **rep}
    p = cert_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, p)
    return doc


def certificate(root=None):
    try:
        return json.load(open(cert_path(root)))
    except Exception:
        return None


def verdict_from_eval(cand_tier, ref_tier, root=None):
    """Judge two tiers from eval/history.jsonl rows that carry {model|tier,
    brief|genre, pass|passed|ok}. Honest when the ledger can't answer."""
    rows = []
    try:
        for ln in open(os.path.join(root or DEF_ROOT, "eval", "history.jsonl")):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass

    def _pick(tier):
        out = []
        for r in rows:
            m = str(r.get("model") or r.get("tier") or "")
            if tier.lower() not in m.lower():
                continue
            brief = r.get("brief") or r.get("genre")
            passed = r.get("passed", r.get("pass", r.get("ok")))
            if brief is None or passed is None:
                continue
            out.append({"brief": brief, "passed": bool(passed)})
        return out

    return graduate(_pick(cand_tier), _pick(ref_tier))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print(json.dumps(verdict_from_eval(sys.argv[1], sys.argv[2]), indent=1))
    else:
        print(json.dumps({"readiness": readiness(),
                          "certificate": certificate()}, indent=1))
