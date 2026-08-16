#!/usr/bin/env python3
"""THE BRAIN BR-E battery — the cadet gate, fixture-pure. Proves: readiness
is honest arithmetic, graduation demands paired evidence + tolerance + the
sign test (10 lucky briefs can't graduate anyone; a one-sided loser is
refused even inside the tolerance band), certificates mint only on a
graduated verdict, and the eval-ledger reader degrades honestly."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadet_gate as cg

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


def res(pattern):
    return [{"brief": f"b{i}", "passed": bool(p)} for i, p in enumerate(pattern)]


def main():
    # ---- insufficiency is first-class
    r = cg.graduate(res([1] * 10), res([1] * 10))
    need(not r["graduated"] and "insufficient" in r["why"],
         "10 briefs < floor: never graduates on luck")
    need(cg.graduate([], [])["paired_briefs"] == 0, "empty evidence honest")
    r = cg.graduate(res([1] * 24), [{"brief": f"x{i}", "passed": True}
                                    for i in range(24)])
    need(not r["graduated"] and r["paired_briefs"] == 0,
         "unpaired briefs never count (SAME suite law)")

    # ---- tolerance band
    r = cg.graduate(res([1] * 24), res([1] * 24))
    need(r["graduated"] and r["delta"] == 0.0, "identical performance graduates")
    r = cg.graduate(res([1] * 20 + [0] * 4), res([1] * 24))
    need(not r["graduated"] and "gap" in r["why"],
         f"16.7% gap refused (delta {r['delta']})")
    r = cg.graduate(res([1] * 23 + [0]), res([1] * 24))
    need(r["graduated"], f"4.2% gap inside 5% tolerance graduates (rep {r})")

    # ---- the sign test: one-sided discordance refused even at delta ~0
    # cand loses 6 head-to-heads, wins 0, but each also passes 6 the other
    # fails? construct: 30 briefs; ref passes 0..23 (24), cand passes 6..29
    # (24) -> delta 0, discordant = 12 (6 each way) -> chance, graduates
    cand = res([0] * 6 + [1] * 24)
    ref = res([1] * 24 + [0] * 6)
    r = cg.graduate(cand, ref)
    need(r["graduated"] and r["cand_only_wins"] == 6 and r["ref_only_wins"] == 6,
         f"balanced discordance = chance, graduates (rep {r})")
    # one-sided: ref passes ALL 40; cand fails exactly 2 (5% = at tolerance)
    # but every discordant pair is a cadet loss -> sign test p = 0.25 -> ok;
    # push to 6 one-sided losses on 120 briefs (5% delta at edge, p=0.016)
    cand = res([0] * 6 + [1] * 114)
    ref = res([1] * 120)
    r = cg.graduate(cand, ref)
    need(not r["graduated"] and "discordant" in r.get("why", ""),
         f"one-sided losses refused by the sign test (rep {r})")

    # ---- certificate law
    with tempfile.TemporaryDirectory(prefix="braine_") as root:
        bad = cg.graduate(res([1] * 10), res([1] * 10))
        need(cg.mint(bad, "gemma", "fable", root=root) is None,
             "mint refuses a non-graduated report")
        need(cg.certificate(root) is None, "no cert file when refused")
        good = cg.graduate(res([1] * 24), res([1] * 24))
        doc = cg.mint(good, "gemma-3", "fable-5", root=root)
        need(doc is not None and doc["cand"] == "gemma-3", "cert minted")
        need(cg.certificate(root)["graduated"] is True, "cert round-trips")

        # ---- eval-ledger reader
        ev = os.path.join(root, "eval")
        os.makedirs(ev, exist_ok=True)
        with open(os.path.join(ev, "history.jsonl"), "w") as f:
            for i in range(24):
                f.write(json.dumps({"model": "claude-fable-5", "brief": f"g{i}",
                                    "passed": True}) + "\n")
                f.write(json.dumps({"model": "gemma-3-4b", "brief": f"g{i}",
                                    "passed": i != 3}) + "\n")
            f.write('{"torn": \n')
        r = cg.verdict_from_eval("gemma", "fable", root=root)
        need(r["paired_briefs"] == 24 and r["graduated"],
             f"eval ledger judged (rep {r})")
        r2 = cg.verdict_from_eval("nonexistent-tier", "fable", root=root)
        need(not r2["graduated"] and "insufficient" in r2["why"],
             "unknown tier -> insufficient, never a guess")
        r3 = cg.verdict_from_eval("a", "b", root=os.path.join(root, "void"))
        need(not r3["graduated"], "missing ledger -> honest refusal")

    # ---- readiness against the REAL tree (arithmetic only, no writes)
    rd = cg.readiness()
    need(isinstance(rd["banked_tuples"], int) and rd["floor"] == 200,
         "readiness reads the live ledger")
    need(rd["ready_to_train"] is (rd["banked_tuples"] >= 200),
         "readiness verdict = pure arithmetic on the floor")

    print(f"braine_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
