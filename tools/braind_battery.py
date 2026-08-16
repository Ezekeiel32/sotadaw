#!/usr/bin/env python3
"""THE BRAIN BR-D battery — composer prior + pocket net + budget law,
fixture-pure. Proves: tokenization is witness-blind and in-key at train time,
generation is deterministic / in-key by construction / tessitura-clamped,
THE NOVELTY COURT kills a verbatim single-source line, dry bins refuse,
the pocket net reproduces a planted feel under the ceiling and refuses dry
bins, and the budget stops a planted runaway with an honest gap line."""
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget_law as bl
import composer_cells as cc
import composer_prior as cp
import pocket_net as pn

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
    """4 fixture docs in A minor. BRANCHING corpus, seed-pinned: pure-loop
    fixtures were correctly EATEN by the novelty court (every walk replays a
    single-source line verbatim — first fixture proved the court works, not
    that generation does). A stochastic scale-walk corpus branches like the
    real 184-doc corpus, so walks can mix sources legally."""
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

    docs = []
    for i, genre in enumerate(("uk garage", "deep house", "garage", "2step")):
        d = {"key": "A minor", "bpm": 120 + i, "genre": genre,
             "tracks": [{"name": "lead", "notes": _mel(walk(400))},
                        {"name": "bass", "notes": _mel(walk(200, lo=40, hi=55),
                                                       step=1.0, dur=0.9)}]}
        if i == 0:
            d["tracks"].append({"name": "lead_sketch",
                                "notes": _mel([61, 66, 63, 68] * 8)})
        docs.append((d, genre, f"d{i + 1}"))
    # accidental-bearing doc — exercises the CELL organ's chroma gate (blue
    # notes kept at mine time, gated per target key at realize time)
    blue = [p + (1 if i % 7 == 3 else 0) for i, p in enumerate(walk(80))]
    docs.append(({"key": "A minor", "bpm": 124, "genre": "deep house",
                  "tracks": [{"name": "lead", "notes": _mel(blue)}]},
                 "deep house", "d5"))
    return docs


def main():
    docs = corpus_docs()

    # ---- tokenization
    toks = cp.tokenize(docs[0][0])
    roles = sorted(r for r, _t, _o in toks)
    need(roles == ["bass", "lead"], f"witness lane excluded, roles found (got {roles})")
    lead = next(t for r, t, _o in toks if r == "lead")
    need(all(0 <= t[0] <= 15 and 0 <= t[1] <= 6 for t in lead),
         "tokens carry slot 0..15 and degree 0..6")
    need(cp.tokenize({"key": "", "tracks": []}) == [], "keyless doc -> [] (never guess)")

    with tempfile.TemporaryDirectory(prefix="braind_") as root:
        m = cp.train(docs, root=root)
        need(os.path.exists(cp.model_path(root)), "model persisted")
        need(m["bins"]["any/lead"]["events"] >= 64, "any/lead bin fed")
        need("house/bass" in m["bins"], "family bins ride genre words")

        # ---- generation: in-key by construction, deterministic, clamped
        c1 = cp.generate(m, "uk garage", "F minor", 4, "lead", seed=9, n=3, root=root)
        need(len(c1) >= 1, f"candidates generated (got {len(c1)})")
        import theory
        fmin = set(theory.allowed_pcs(theory.parse_key("F minor"), ""))
        allpcs = {n["pitch"] % 12 for cd in c1 for n in cd["notes"]}
        need(allpcs <= fmin, f"IN-KEY BY CONSTRUCTION (got extras {sorted(allpcs - fmin)})")
        lo, hi = cp.TESSITURA["lead"]
        need(all(lo <= n["pitch"] <= hi for cd in c1 for n in cd["notes"]),
             "tessitura clamped")
        need(all(n["start"] < 16.0 and n["start"] + n["len"] <= 16.0 + 1e-6
                 for cd in c1 for n in cd["notes"]), "window bounds honored")
        c2 = cp.generate(m, "uk garage", "F minor", 4, "lead", seed=9, n=3, root=root)
        need(json.dumps(c1) == json.dumps(c2), "same seed = byte-identical candidates")
        c3 = cp.generate(m, "uk garage", "F minor", 4, "lead", seed=10, n=3, root=root)
        need(json.dumps(c1) != json.dumps(c3), "different seed = different music")

        # ---- honest refusals
        need(cp.generate(m, "x", "not a key", 4, "lead", root=root) == [],
             "unparseable key -> []")
        m_dry = {"bins": {"any/lead": {"events": 10, "trans": {},
                                       "starts": {"0.0.1.1|4.2.1.1": 1},
                                       "oct": {}}}, "ngrams": {}}
        need(cp.generate(m_dry, "", "C major", 4, "lead") == [],
             "dry bin (<MIN_EVENTS) refuses — expanders stand")
        need(cp.generate(None, "", "C major", 4, "lead", root=root) is not None,
             "model auto-load path returns (list)")

        # ---- THE NOVELTY COURT: a model whose ONLY continuation replays one
        # doc's unique line must reject every candidate
        seq = [f"{i % 16}.{i % 7}.1.1" for i in range(24)]
        forced = {"bins": {"any/lead": {
            "events": 999, "starts": {f"{seq[0]}|{seq[1]}": 1},
            "trans": {f"{seq[i]}|{seq[i + 1]}": {seq[i + 2]: 1}
                      for i in range(len(seq) - 2)},
            "oct": {}}},
            "ngrams": {"|".join(seq[i:i + cp.NGRAM]): ["only_doc"]
                       for i in range(len(seq) - cp.NGRAM + 1)}}
        need(cp.generate(forced, "", "C major", 4, "lead") == [],
             "NOVELTY COURT: verbatim single-source line rejected")
        forced_shared = dict(forced)
        forced_shared = json.loads(json.dumps(forced))
        for h in forced_shared["ngrams"]:
            forced_shared["ngrams"][h] = ["a", "b"]      # shared idiom = language
        need(len(cp.generate(forced_shared, "", "C major", 4, "lead")) >= 1,
             "shared idioms are language, not theft")

        # ---- THE CELL PRIOR (BR-D wave 2): phrase-level recombination organ
        cm = cc.mine(docs, root=root)
        need(os.path.exists(cc.model_path(root)), "cell model persisted")
        lead_cells = cm["bins"].get("any/lead") or []
        need(len(lead_cells) >= cc.MIN_CELLS,
             f"any/lead cell bank fed (got {len(lead_cells)})")
        need(all(len(c["d"]) <= cc.MAX_NOTES and c["span"] <= cc.MAX_SPAN
                 for c in lead_cells),
             "cells bounded <= MAX_NOTES/<= MAX_SPAN (< RUN_HARD by law)")
        need(any(any(ch != 0 for ch in c["c"]) for c in lead_cells),
             "accidentals mined as chroma (blue notes kept)")
        am = sorted({0, 2, 4, 5, 7, 9, 11})
        probe = cc._cell_of(_mel([59, 60, 64]), am, "probe")
        rp = cc._realize(probe, am, set(range(12)), 0, 40, 90, None)
        need([b - a for a, b in zip(rp, rp[1:])] == [1, 4],
             "realization preserves intervals bit-true at ds=0 (octave-borrow law)")
        g1 = cc.generate(cm, "uk garage", "F minor", 4, "lead",
                         seed=5, n=3, root=root)
        need(len(g1) >= 1, f"cell candidates generated (got {len(g1)})")
        pcs = {n["pitch"] % 12 for cd in g1 for n in cd["notes"]}
        fmin_g = set(theory.allowed_pcs(theory.parse_key("F minor"),
                                        "uk garage"))
        need(pcs <= fmin_g,
             f"cells IN-KEY per THE COURT'S OWN genre allowance "
             f"(extras {sorted(pcs - fmin_g)})")
        need(all(lo <= n["pitch"] <= hi for cd in g1 for n in cd["notes"]),
             "cell tessitura clamped")
        need(all(n["start"] < 16.0 and n["start"] + n["len"] <= 16.0 + 1e-6
                 for cd in g1 for n in cd["notes"]), "cell window bounds honored")
        g2 = cc.generate(cm, "uk garage", "F minor", 4, "lead",
                         seed=5, n=3, root=root)
        need(json.dumps(g1) == json.dumps(g2), "cell prior deterministic")
        g3 = cc.generate(cm, "uk garage", "F minor", 4, "lead",
                         seed=6, n=3, root=root)
        need(json.dumps(g1) != json.dumps(g3), "cell prior varies by seed")
        need(all(a[0] != b[0] for cd in g1
                 for a, b in zip(cd["srcs"], cd["srcs"][1:])),
             "ADJACENCY LAW: neighbor cells never share a source")
        cover_ok = True
        for cd in g1:
            tot = sum(nn for _s, nn in cd["srcs"]) or 1
            per = {}
            for s, nn in cd["srcs"]:
                per[s] = per.get(s, 0) + nn
            if max(per.values()) > cc.COVER_FRAC * tot or len(per) < 2:
                cover_ok = False
        need(cover_ok, "COVERAGE LAW: no source > half a take, >= 2 sources")
        need(cc.generate(cm, "x", "not a key", 4, "lead", root=root) == [],
             "cells: unparseable key -> []")
        need(cc.generate({"bins": {"any/lead": lead_cells[:5]}}, "", "C major",
                         4, "lead") == [],
             "cells: dry bin refuses — expanders stand")

        # ---- THE CELL BANK STAYS FRESH: is_stale's pure gate
        need(cc.is_stale(root=os.path.join(root, "nowhere")),
             "no model at all -> always stale")
        mt = os.path.getmtime(cc.model_path(root))
        need(not cc.is_stale(root=root, now=mt + 10),
             "inside the cooldown -> never stale (accept storms = ONE mine)")
        need(not cc.is_stale(root=root, cooldown_s=0, now=mt + 10),
             "no corpus growth -> fresh even past cooldown")
        sd = os.path.join(root, "songs")
        os.makedirs(sd, exist_ok=True)
        for nm, dt in (("_prop_x.json", 99), ("grown.json", 50)):
            p = os.path.join(sd, nm)
            open(p, "w").write("{}")
            os.utime(p, (mt + dt, mt + dt))
        need(cc.is_stale(root=root, cooldown_s=0, now=mt + 60),
             "a grown corpus past cooldown -> stale")
        os.remove(os.path.join(sd, "grown.json"))
        need(not cc.is_stale(root=root, cooldown_s=0, now=mt + 120),
             "witness/_prop_ files never count as growth")

        # ---- WRITE-IF-SANE: the automated re-mine may never ship a
        # starved or collapsed organ
        ok_s, _w = cc.sane_model(cm, None)
        need(ok_s, "the fixture model is sane by its own gate")
        starved = {"bins": dict(cm["bins"], **{"any/lead": []})}
        need(not cc.sane_model(starved, None)[0],
             "a starved lead bin is REFUSED")
        nb = len(cm["bins"]["any/bass"])
        k = max(cc.MIN_CELLS, int(0.4 * nb))   # fed, but < half the old bin
        half = {"bins": dict(cm["bins"], **{"any/bass": cm["bins"]["any/bass"][:k]})}
        need(nb > 2 * cc.MIN_CELLS and not cc.sane_model(half, cm)[0],
             f"a collapsed-not-starved bin vs the old model is REFUSED "
             f"({nb} -> {k})")

        # ---- pocket net: planted feel reproduced under the ceiling
        # 512 onsets = 32 per 16th-slot (MIN_SAMPLES=24 per bin); odd slots
        # pushed +0.012 beats = +6ms at 120 bpm
        feel = {"key": "A minor", "bpm": 120, "genre": "funk",
                "tracks": [{"name": "hats", "notes": [
                    {"start": b * 0.25 + (0.012 if b % 2 else 0.0),
                     "len": 0.1, "pitch": 42,
                     "vel": 0.9 if b % 4 == 0 else 0.55}
                    for b in range(512)]}]}
        pm = pn.mine([(feel, "funk", "f1")])
        need(any(k.startswith("band/hat/") or k.startswith("any/hat/")
                 for k in pm["bins"]), f"hat bins mined (got {list(pm['bins'])[:4]})")
        rng = random.Random(3)
        offs = []
        for _ in range(200):
            s = pn.sample(pm, "funk", "hat", 1, rng)       # odd 16th slot = pushed
            need(s is not None, "sample returns on a fed bin") if _ == 0 else None
            if s:
                offs.append(s[0])
        mean_off = sum(offs) / max(len(offs), 1)
        need(4.0 < mean_off < 8.0,
             f"planted +6ms push reproduced in sign+scale (mean {mean_off:.1f}ms)")
        cap = pn._ceiling_ms("funk")
        need(all(abs(o) <= cap + 1e-9 for o in offs),
             f"CEILING LAW holds (cap {cap:.1f}ms)")
        need(pn.sample(pm, "funk", "kick", 0, rng) is None,
             "dry role -> None (pocket_dna stands)")
        need(pn.sample(None, "funk", "hat", 1, rng) is None, "no model -> None")
        vels = [pn.sample(pm, "funk", "hat", 0, rng) for _ in range(50)]
        need(all(v is None or 0.7 <= v[1] <= 1.3 for v in vels),
             "vel scale clamped 0.7..1.3")

        # ---- budget law
        clock = {"t": 0.0}
        b = bl.Budget("r1", caps={"renders": 3, "seconds": 100, "orders": 5},
                      clock=lambda: clock["t"])
        need(b.allow("renders") and b.spend("renders") == 2, "spend counts down")
        b.spend("renders")
        b.spend("renders")
        need(not b.allow("renders"), "render cap refuses the 4th")
        need("renders 3 at cap 3" in b.gap_line() and "silent grind" in b.gap_line(),
             "gap line is honest and numbered")
        clock["t"] = 101.0
        need(not b.allow("orders"), "wall breach refuses EVERYTHING")
        need("wall 101s > cap 100s" in b.gap_line(), "wall breach named")
        need(b.breaches == ["renders", "seconds"], "breach ledger deduped, ordered")
        b2 = bl.Budget("r2", clock=lambda: 0.0)
        need(b2.caps["renders"] == bl.DEFAULT_CAPS["renders"], "default caps stand")
        bb = bl.for_run("rq77", caps={"renders": 2})
        need(bl.for_run("rq77") is bb, "for_run is one budget per run id")
        row = bl.close("rq77", root=root)
        need(row is not None and row["run_id"] == "rq77", "close returns the row")
        need(os.path.exists(os.path.join(root, "telemetry", "budget.jsonl")),
             "budget telemetry lands")
        need(bl.close("rq77", root=root) is None, "double close is benign")

    print(f"braind_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
