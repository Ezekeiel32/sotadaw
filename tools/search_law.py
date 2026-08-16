#!/usr/bin/env python3
"""AMAZING PART III — THE SEARCH LAW, generate-side (symbolic tier v1).

The gate judges RENDERS; the search law judges CANDIDATES — render-free,
deterministic, cheap — so quality stops depending on any single generation
being brilliant. B1's mount contract (spec: candidates emitted "straight
into AMAZING's SEARCH LAW as generate-side candidates beside the
deterministic expanders") lands here.

THE INCUMBENT LAW: the deterministic expander's take competes as the
incumbent and a challenger must be STRICTLY better to displace it —
key-court first, then advisory count, then nearest-real-lane corpus
distance by more than DIST_MARGIN (a hair's edge never overthrows curated
genre DNA). No model / dry bin / bad key / any exception => the incumbent
rides through untouched with an honest why line. Kill-switch:
SOTADAW_SEARCH_LAW=0.

Judges reused verbatim from the floor rigs: prior_floor.court_take (key
hard + melody/harmony advisories) and the nearest-lane interval meter (the
MIXTURE-TRAP-safe form). Corpus lane histograms + the cell model load once
per process (warm residents keep them).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DIST_MARGIN = 0.05
K = 3

_CACHE = {}          # per-root: a bench's tmp root must never poison prod


def _judges(root=None):
    rk = root or ""
    if rk not in _CACHE:
        try:
            import composer_cells as cc
            import composer_prior as cp
            import prior_floor as pf
            _CACHE[rk] = (cc.load_model(root),
                          pf.corpus_interval_hist(cp.corpus_docs(root,
                                                                 cap=60)))
        except Exception:
            _CACHE[rk] = (None, None)
    return _CACHE[rk]


def _score(notes, genre, key, role, lanes):
    import prior_floor as pf
    key_ok, adv = pf.court_take(notes, genre, key, role)
    d = pf.nearest_lane_dist(pf.interval_hist(notes),
                             (lanes or {}).get(role) or [])
    return {"key_bad": 0 if key_ok else 1, "adv": int(adv),
            "dist": round(d if d is not None else 9.9, 3)}


def _stands(notes, why):
    return {"notes": notes, "source": "expander", "why": why, "scores": []}


def search(genre, key, bars, role, seed, incumbent=None, k=K, root=None):
    """Never raises. {"notes", "source": cells|expander, "why", "scores"}.
    source "expander" = the incumbent survived (or judging was impossible)."""
    if os.environ.get("SOTADAW_SEARCH_LAW", "1") == "0":
        return _stands(incumbent, "SEARCH LAW off (SOTADAW_SEARCH_LAW=0)")
    try:
        import composer_cells as cc
        model, lanes = _judges(root)
        if model is None:
            return _stands(incumbent,
                           "SEARCH LAW: no cell model — expander stands")
        cands = cc.generate(model, genre, key, bars, role,
                            seed=int(seed) & 0x7fffffff, n=k, root=root)
        if not cands:
            return _stands(incumbent,
                           f"SEARCH LAW: cells refused {role} for this brief "
                           f"(dry/keyless) — expander stands")
        best, best_s = None, None
        for cd in cands:
            s = _score(cd["notes"], genre, key, role, lanes)
            if best_s is None or (s["key_bad"], s["adv"], s["dist"]) < \
                    (best_s["key_bad"], best_s["adv"], best_s["dist"]):
                best, best_s = cd, s
        if not incumbent:
            return {"notes": best["notes"], "source": "cells",
                    "why": f"SEARCH LAW: cells provided {role} "
                           f"(no incumbent; {best_s})",
                    "scores": [best_s]}
        inc = _score(incumbent, genre, key, role, lanes)
        beats = (best_s["key_bad"] < inc["key_bad"]
                 or (best_s["key_bad"] == inc["key_bad"]
                     and best_s["adv"] < inc["adv"])
                 or (best_s["key_bad"] == inc["key_bad"]
                     and best_s["adv"] == inc["adv"]
                     and best_s["dist"] + DIST_MARGIN < inc["dist"]))
        if beats:
            return {"notes": best["notes"], "source": "cells",
                    "why": (f"SEARCH LAW: cells displaced the {role} expander "
                            f"(key {'ok' if not best_s['key_bad'] else 'BAD'}"
                            f" vs {'ok' if not inc['key_bad'] else 'BAD'}, "
                            f"advisories {best_s['adv']} vs {inc['adv']}, "
                            f"corpus-dist {best_s['dist']} vs {inc['dist']})"),
                    "scores": [inc, best_s]}
        return {"notes": incumbent, "source": "expander",
                "why": (f"SEARCH LAW: {role} expander stands (challenger "
                        f"adv {best_s['adv']}/dist {best_s['dist']} did not "
                        f"strictly beat adv {inc['adv']}/dist {inc['dist']})"),
                "scores": [inc, best_s]}
    except Exception as e:
        return _stands(incumbent,
                       f"SEARCH LAW unavailable ({type(e).__name__}) — "
                       f"expander stands")


ROOT = os.path.dirname(HERE)
CONTOUR_BANK = "contours.json"     # library/ = GIT TRUTH
_BANKS = {}


def contour_bank_path(root=None):
    return os.path.join(root or ROOT, "library", CONTOUR_BANK)


def _contour_grid(notes, points=32):
    """A corpus line -> its LOW-FREQUENCY shape on a fixed grid, or None.
    THE LOW-FREQUENCY LAW (measured 2026-07-17: the raw trajectory LOST
    the A/B 1-of-6 — funk 0.000 -> 0.625; anchors sample the plan arc
    sparsely and jaggedness scatters them into leaps the corpus never
    makes): two boxcar passes, then re-span to 0..1 so the climax law can
    still reach the window top; a flat line carries no shape."""
    if not notes or len(notes) < 4:
        return None
    ns = sorted(notes, key=lambda n: n["start"])
    span = max(n["start"] for n in ns) or 1.0
    ps = [n["pitch"] for n in ns]
    lo, hi = min(ps), max(ps)
    if hi - lo < 3:
        return None
    pts = [(n["start"] / span, (n["pitch"] - lo) / float(hi - lo))
           for n in ns]
    grid = []
    for i in range(points):
        x = i / float(points - 1)
        left = max((p for p in pts if p[0] <= x), key=lambda p: p[0],
                   default=pts[0])
        right = min((p for p in pts if p[0] >= x), key=lambda p: p[0],
                    default=pts[-1])
        if right[0] <= left[0]:
            grid.append(left[1])
        else:
            t = (x - left[0]) / (right[0] - left[0])
            grid.append(left[1] + t * (right[1] - left[1]))
    w = max(2, points // 4)
    for _pass in range(2):
        grid = [sum(grid[max(0, i - w):i + w + 1])
                / len(grid[max(0, i - w):i + w + 1])
                for i in range(points)]
    glo, ghi = min(grid), max(grid)
    if ghi - glo < 0.15:
        return None
    return [round((v - glo) / (ghi - glo), 4) for v in grid]


def bank_contours(root=None, per_family=24, points=32):
    """Curate library/contours.json from the CURRENT cell model — an
    EXPLICIT act that changes sealed generator output: reseal
    generation_court in the same commit. (THE SEAL vs THE LIVING MODEL,
    caught 2026-07-17: the freshness rail re-mined the cell model and
    bossanova:5 diverged from a 1h-old seal — the sealed path may only
    read GIT-TRUTH data, so hooks draw arcs from THIS committed bank
    while compose_line keeps drinking from the living model.)"""
    import composer_cells as cc
    import composer_prior as cp
    model = cc.load_model(root)
    bank = {}
    if model:
        for fam in ("any",) + tuple(sorted(cp.FAMILY_WORDS)):
            genre = "" if fam == "any" else sorted(
                cp.FAMILY_WORDS[fam])[0]
            pool, seed = [], 1
            while len(pool) < per_family and seed <= per_family * 6:
                cands = cc.generate(model, genre, "A minor", 4, "lead",
                                    seed=seed, n=1, root=root)
                seed += 1
                if not cands:
                    if fam != "any":
                        break            # dry family: the any pool serves
                    continue
                g = _contour_grid(cands[0]["notes"], points)
                if g and g not in pool:
                    pool.append(g)
            if pool:
                bank[fam] = pool
    # THE JUDGE'S REFERENCE RIDES THE BANK: every judge on the sealed path
    # (pick_hook + hook_search.improve, lead AND bass) reads lane
    # histograms from git truth — the living corpus would re-break the
    # seal the moment a song lands
    lane_hists = {}
    try:
        import prior_floor as pf
        all_h = pf.corpus_interval_hist(cp.corpus_docs(root, cap=60))
        lane_hists = {role: [[round(x, 4) for x in h] for h in hs]
                      for role, hs in all_h.items() if hs}
    except Exception:
        lane_hists = {}
    # hook_search's CONTOUR TRANSPLANT draws a corpus cell's degree-delta
    # sequence — banked per (role, family) for the same reason
    cell_deltas = {}
    if model:
        for role in ("lead", "bass"):
            by_fam = {}
            for fam in ("any",) + tuple(sorted(cp.FAMILY_WORDS)):
                cells = (model.get("bins") or {}).get(f"{fam}/{role}") or []
                if len(cells) < 24:
                    continue
                pool, i = [], 0
                while len(pool) < per_family and i < len(cells):
                    c = cells[i]
                    i += 1
                    lins = [d + 7 * o for d, o in zip(c["d"], c["o"])]
                    seq = [b - a for a, b in zip(lins, lins[1:])]
                    seq = [d for d in seq if abs(d) <= 7]
                    if seq and seq not in pool:
                        pool.append(seq)
                if pool:
                    by_fam[fam] = pool
            if by_fam:
                cell_deltas[role] = by_fam
    p = contour_bank_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"version": 2, "points": points, "lead": bank,
                   "lane_hists": lane_hists, "cell_deltas": cell_deltas}, f)
    os.replace(tmp, p)
    _BANKS.pop(root or "", None)
    return {fam: len(pool) for fam, pool in bank.items()}


def _bank(root=None):
    rk = root or ""
    if rk not in _BANKS:
        try:
            _BANKS[rk] = json.load(open(contour_bank_path(root)))
        except Exception:
            _BANKS[rk] = None
    return _BANKS[rk]


def learned_contour(genre, key, bars, seed, points=32, root=None):
    """THE MARRIAGE (B1 mount wave 3): a LEARNED melodic arc for loop_gen's
    hook engine, drawn from the COMMITTED contour bank (never the living
    cell model — the sealed path reads git truth only). Returns a callable
    h(x in 0..1) -> 0..1 or None (no bank / dry family / kill-switch) —
    None means the synthetic shapes stand, byte-exact. Deterministic per
    seed; key/bars ride the signature for caller compat (a contour is
    shape-only)."""
    if os.environ.get("SOTADAW_HOOK_CELLS", "1") == "0":
        return None
    try:
        import composer_prior as cp
        bank = _bank(root)
        lead = (bank or {}).get("lead") or {}
        pool = lead.get(cp.family_of(genre)) or lead.get("any")
        if not pool:
            return None
        grid = pool[int(seed) % len(pool)]
        n = len(grid)

        def h(x):
            x = max(0.0, min(1.0, float(x)))
            f = x * (n - 1)
            i = int(f)
            if i >= n - 1:
                return grid[-1]
            return grid[i] + (f - i) * (grid[i + 1] - grid[i])
        return h
    except Exception:
        return None


def pick_hook(genre, synthetic_notes, learned_notes, root=None):
    """THE INCUMBENT LAW at the hook seam (measured 2026-07-17: the bank
    served indiscriminately and funk's PERFECT synthetic take 0.000 went
    to 0.674 — the per-brief refusals of the living-model rail were doing
    silent work). Judge BOTH takes against the BANKED lane histograms
    (git truth, seal-safe); the synthetic incumbent wins ties and margins.
    Returns (notes, 'synthetic'|'learned'). No bank hists -> synthetic."""
    try:
        import prior_floor as pf
        bank = _bank(root) or {}
        hists = (bank.get("lane_hists") or {}).get("lead") or []
        if not hists or not learned_notes:
            return synthetic_notes, "synthetic"
        d0 = pf.nearest_lane_dist(pf.interval_hist(synthetic_notes), hists)
        d1 = pf.nearest_lane_dist(pf.interval_hist(learned_notes), hists)
        if d0 is None or d1 is None:
            return synthetic_notes, "synthetic"
        if d1 + DIST_MARGIN < d0:
            return learned_notes, "learned"
        return synthetic_notes, "synthetic"
    except Exception:
        return synthetic_notes, "synthetic"


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE SEARCH LAW (symbolic tier)")
    ap.add_argument("--genre", default="")
    ap.add_argument("--key", default=None)
    ap.add_argument("--bars", type=int, default=4)
    ap.add_argument("--role", default="lead", choices=("bass", "lead", "pad"))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bank-contours", action="store_true",
                    help="curate library/contours.json from the current "
                         "cell model — CHANGES SEALED OUTPUT: reseal "
                         "generation_court in the same commit")
    a = ap.parse_args()
    if a.bank_contours:
        rep = bank_contours()
        print(json.dumps({"banked": rep}, indent=1))
        sys.exit(0)
    if not a.key:
        ap.error("--key is required (unless --bank-contours)")
    r = search(a.genre, a.key, a.bars, a.role, a.seed)
    print(json.dumps({"source": r["source"], "why": r["why"],
                      "notes": len(r["notes"] or [])}, indent=1))
    sys.exit(0)
