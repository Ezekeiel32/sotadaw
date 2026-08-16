#!/usr/bin/env python3
"""THE SEARCH LAW battery (AMAZING PIII generate-side) — fixture-pure.

Proves THE INCUMBENT LAW mechanics: ties never displace curated DNA, an
off-key incumbent falls to a key-clean challenger, dry/model-less/killed
lanes leave the expander untouched with an honest why, results are
deterministic, and the shape contract holds (never raises, notes ride
through)."""
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import composer_cells as cc
import search_law as sl

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


def _mel(seq, t0=0.0, step=0.5, vel=0.8, dur=0.5):
    return [{"start": t0 + i * step, "len": dur, "pitch": p, "vel": vel}
            for i, p in enumerate(seq)]


def corpus_docs():
    a_minor = [57, 59, 60, 62, 64, 65, 67]
    rng = random.Random(41)

    def walk(n, lo=55, hi=79):
        deg, out = 3, []
        for _ in range(n):
            deg = max(0, min(20, deg + rng.choice((-2, -1, -1, 0, 1, 1, 2))))
            p = a_minor[deg % 7] + 12 * (deg // 7)
            while p < lo:
                p += 12
            while p > hi:
                p -= 12
            out.append(p)
        return out

    return [({"key": "A minor", "bpm": 120 + i, "genre": g,
              "tracks": [{"name": "lead", "notes": _mel(walk(400))},
                         {"name": "bass",
                          "notes": _mel(walk(200, lo=40, hi=55),
                                        step=1.0, dur=0.9)}]}, g, f"d{i+1}")
            for i, g in enumerate(("uk garage", "deep house", "garage",
                                   "2step"))]


def main():
    docs = corpus_docs()
    with tempfile.TemporaryDirectory(prefix="slaw_") as root:
        cc.mine(docs, root=root)

        # cells provide when there is no incumbent
        r0 = sl.search("uk garage", "F minor", 4, "bass", 7, incumbent=None,
                       root=root)
        need(r0["source"] == "cells" and len(r0["notes"] or []) >= 4,
             f"no incumbent -> cells provide (got {r0['source']})")
        need("SEARCH LAW" in r0["why"], "why names the law")

        # THE INCUMBENT LAW: a tie never displaces (incumbent == the winner)
        r1 = sl.search("uk garage", "F minor", 4, "bass", 7,
                       incumbent=r0["notes"], root=root)
        need(r1["source"] == "expander" and r1["notes"] is r0["notes"],
             f"tie -> incumbent stands untouched (got {r1['source']})")

        # an off-key incumbent falls to a key-clean challenger
        offkey = _mel([42, 47, 42, 47, 42, 47, 42, 47,
                       42, 47, 42, 47, 42, 47, 42, 47], step=1.0)
        r2 = sl.search("uk garage", "F minor", 4, "bass", 7,
                       incumbent=offkey, root=root)
        need(r2["source"] == "cells" and "vs BAD" in r2["why"]
             and "key ok" in r2["why"],
             f"off-key incumbent displaced, why carries both keys (got "
             f"{r2['why'][:90]})")

        # determinism: same ask twice = byte-identical
        r3 = sl.search("uk garage", "F minor", 4, "bass", 7,
                       incumbent=offkey, root=root)
        need(json.dumps(r2, sort_keys=True) == json.dumps(r3, sort_keys=True),
             "same ask = byte-identical result")

        # dry role (no pad cells in the fixture) -> honest stand-down
        inc = _mel([48, 52, 55, 48], step=4.0, dur=3.5)
        r4 = sl.search("uk garage", "F minor", 4, "pad", 7, incumbent=inc,
                       root=root)
        need(r4["source"] == "expander" and r4["notes"] is inc
             and "refused" in r4["why"],
             f"dry bin -> expander stands, why honest (got {r4['why'][:80]})")

        # unparseable key -> cells refuse -> expander stands
        r5 = sl.search("uk garage", "not a key", 4, "bass", 7,
                       incumbent=inc, root=root)
        need(r5["source"] == "expander" and r5["notes"] is inc,
             "bad key -> expander stands")

    # no model at all (empty root) -> expander stands, why says so
    with tempfile.TemporaryDirectory(prefix="slaw2_") as r2root:
        r6 = sl.search("house", "C major", 4, "lead", 3,
                       incumbent=_mel([60, 62, 64]), root=r2root)
        need(r6["source"] == "expander" and "no cell model" in r6["why"],
             f"model-less root -> honest stand-down (got {r6['why'][:60]})")

    # kill-switch: SOTADAW_SEARCH_LAW=0 short-circuits everything
    os.environ["SOTADAW_SEARCH_LAW"] = "0"
    try:
        r7 = sl.search("uk garage", "F minor", 4, "bass", 7,
                       incumbent=[{"start": 0, "len": 1, "pitch": 40,
                                   "vel": 0.9}])
        need(r7["source"] == "expander" and "off" in r7["why"],
             "kill-switch leaves the expander untouched")
    finally:
        del os.environ["SOTADAW_SEARCH_LAW"]

    # the contract never raises: garbage everywhere -> expander survives
    r8 = sl.search(None, None, 0, "xyz", "notanint", incumbent="junk")
    need(r8["source"] == "expander" and r8["notes"] == "junk",
         "garbage in -> incumbent out, no exception")

    # ---- learned_contour (THE MARRIAGE, wave 3 + THE GIT-TRUTH LAW: the
    # sealed generator reads the COMMITTED bank, never the living model —
    # the freshness rail re-mined the cell model and bossanova:5 diverged
    # from a 1h-old seal, caught by the suite 2026-07-17)
    docs2 = corpus_docs()
    with tempfile.TemporaryDirectory(prefix="slaw3_") as root:
        cc.mine(docs2, root=root)
        rep = sl.bank_contours(root=root, per_family=4)
        need(os.path.exists(sl.contour_bank_path(root))
             and rep.get("any", 0) >= 1,
             f"the contour bank curates from the model (got {rep})")
        h = sl.learned_contour("uk garage", "F minor", 4, 9, root=root)
        need(callable(h), "a banked family serves a contour")
        vals = [h(i / 31.0) for i in range(32)]   # the grid's own resolution
        need(all(0.0 <= v <= 1.0 for v in vals),
             "contour lives in [0,1] (renormalized after smoothing)")
        need(abs(max(vals) - 1.0) < 1e-3 and abs(min(vals)) < 1e-3,
             "full span survives THE LOW-FREQUENCY LAW (climax reaches top)")
        h2 = sl.learned_contour("uk garage", "F minor", 4, 9, root=root)
        need([h(x / 8) for x in range(9)] == [h2(x / 8) for x in range(9)],
             "same seed = the same arc")
        # the LIVING model changing must NOT move a banked arc (the seal law)
        flat = [({"key": "A minor", "bpm": 120, "genre": "uk garage",
                  "tracks": [{"name": "lead", "notes": _mel([60] * 64)}]},
                 "uk garage", "flat1")]
        cc.mine(flat, root=root)
        sl._CACHE.pop(root, None)
        h3 = sl.learned_contour("uk garage", "F minor", 4, 9, root=root)
        need(callable(h3) and [h3(x / 8) for x in range(9)]
             == [h(x / 8) for x in range(9)],
             "a re-mined LIVING model never moves a BANKED arc (seal law)")
        need(sl.bank_contours(root=root, per_family=4) == {},
             "banking from a flat model banks NOTHING (never invent shape)")
        sl._BANKS.pop(root, None)
        need(sl.learned_contour("uk garage", "F minor", 4, 9,
                                root=root) is None,
             "an empty bank -> None (synthetic shapes stand)")
    with tempfile.TemporaryDirectory(prefix="slaw4_") as r2:
        need(sl.learned_contour("house", "C major", 4, 3, root=r2) is None,
             "no bank file at all -> None")
        syn = _mel([60, 62, 64, 62, 60, 62, 64, 65])
        lrn = _mel([60, 72, 55, 70, 48, 74, 52, 69])
        need(sl.pick_hook("house", syn, lrn, root=r2)
             == (syn, "synthetic"),
             "no banked hists -> the synthetic incumbent stands")
        os.makedirs(os.path.join(r2, "library"), exist_ok=True)
        import prior_floor as pf
        json.dump({"version": 1, "lead": {},
                   "lane_hists": {"lead": [pf.interval_hist(syn)]}},
                  open(sl.contour_bank_path(r2), "w"))
        sl._BANKS.pop(r2, None)
        need(sl.pick_hook("house", syn, lrn, root=r2)[1] == "synthetic",
             "a corpus-perfect synthetic take is NEVER displaced")
        json.dump({"version": 1, "lead": {},
                   "lane_hists": {"lead": [pf.interval_hist(lrn)]}},
                  open(sl.contour_bank_path(r2), "w"))
        sl._BANKS.pop(r2, None)
        need(sl.pick_hook("house", syn, lrn, root=r2)[1] == "learned",
             "the learned take wins ONLY when measurably closer")

    # ---- THE GIT-TRUTH LAW closes over hook_search too (2026-07-17: its
    # transplant drew cells from the LIVING model inside the SEALED path)
    import hook_search as hs
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "hook_search.py")).read()
    need("import composer_cells" not in src,
         "hook_search never imports the living cell model (structural)")
    need("_judges(" not in src,
         "hook_search never calls the living corpus judges (structural)")
    with tempfile.TemporaryDirectory(prefix="slaw5_") as r3:
        need(hs._cell_deltas("house", 3, root=r3) is None,
             "no bank -> no transplant (synthetic candidates only)")
        os.makedirs(os.path.join(r3, "library"), exist_ok=True)
        json.dump({"version": 2, "lead": {},
                   "cell_deltas": {"lead": {"any": [[1, -1, 2, -2, 1]]}},
                   "lane_hists": {}},
                  open(sl.contour_bank_path(r3), "w"))
        sl._BANKS.pop(r3, None)
        need(hs._cell_deltas("house", 3, root=r3) == [1, -1, 2, -2, 1],
             "transplant deltas come from the COMMITTED bank")
    os.environ["SOTADAW_HOOK_CELLS"] = "0"
    try:
        need(sl.learned_contour("uk garage", "F minor", 4, 9) is None,
             "SOTADAW_HOOK_CELLS=0 -> None (byte-exact fallback proven "
             "against the old seal 2026-07-17)")
    finally:
        del os.environ["SOTADAW_HOOK_CELLS"]

    # ---- THE MARRIAGE (hook_search): contour on DNA rhythm, laws pinned.
    # FIXTURE ROOT ONLY: the first cut judged against the PROD cells model
    # and the transplant legitimately beat 'good' on real corpus distance —
    # a battery must never breathe organic telemetry.
    import hook_search as hs
    scale_abs = [0, 2, 4, 5, 7, 9, 11]
    bad = [{"start": i * 0.5, "len": 0.4, "pitch": 61 + (i % 2), "vel": 0.8}
           for i in range(16)]
    good = [{"start": i * 0.5, "len": 0.4,
             "pitch": [60, 62, 64, 67, 69, 67, 64, 62][i % 8], "vel": 0.8}
            for i in range(16)]
    with tempfile.TemporaryDirectory(prefix="slaw3_") as hroot:
        cc.mine(corpus_docs(), root=hroot)
        notes, why = hs.improve(bad, lambda s: good, "house", "C major",
                                scale_abs, 7, root=hroot)
        need(notes is not bad and bool(why) and "SEARCH LAW" in why,
             "a terrible canonical falls to a better path roll")
        n2, w2 = hs.improve(good, lambda s: good, "house", "C major",
                            scale_abs, 7, root=hroot)
        need(n2 is good and w2 is None,
             "ties never displace (INCUMBENT LAW, silent)")
    tv = hs.transplant(good, [1, -1, 2, -2, 1], scale_abs)
    need([n["start"] for n in tv] == [n["start"] for n in good]
         and [n["len"] for n in tv] == [n["len"] for n in good]
         and [n["vel"] for n in tv] == [n["vel"] for n in good],
         "TRANSPLANT: rhythm + dynamics bit-exact (the DNA is sacred)")
    need(all(n["pitch"] % 12 in set(scale_abs) for n in tv),
         "TRANSPLANT: diatonic by construction")
    order = sorted(range(len(good)), key=lambda i: good[i]["start"])
    by_bar = {}
    for i in order:
        by_bar.setdefault(int(good[i]["start"] // 4), []).append(i)
    need(all(tv[ix[0]]["pitch"] == good[ix[0]]["pitch"]
             and tv[ix[-1]]["pitch"] == good[ix[-1]]["pitch"]
             for ix in by_bar.values()),
         "TRANSPLANT: bar head+tail anchors hold the engine's intent")
    need(hs.transplant([], [1], scale_abs) is None
         and hs.transplant(good, [], scale_abs) is None,
         "transplant refuses empty inputs")
    os.environ["SOTADAW_HOOKSEARCH"] = "0"
    try:
        n3, w3 = hs.improve(bad, lambda s: good, "house", "C major",
                            scale_abs, 7)
        need(n3 is bad and w3 is None, "hook-search kill-switch stands down")
    finally:
        del os.environ["SOTADAW_HOOKSEARCH"]

    print(f"searchlaw_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
