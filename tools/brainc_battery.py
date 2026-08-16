#!/usr/bin/env python3
"""THE BRAIN BR-C battery — timbre oracle + taste head, fixture-pure (no
renders, no CLAP load, no live telemetry writes). Proves: zone parsing skips
performance zones, the window meter hinges right, the ES lands planted
targets deterministically + early-stops, the forge log amortizes, and the
taste head learns separable taste / refuses under-fed data / persists only
past the floors / scores honestly."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timbre_oracle as to
import taste_head as th

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


DSP = '''
freq = hslider("freq", 55, 20, 400, 0.001);
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
punch = hslider("punch", 0.5, 0, 1, 0.01);
decay = hslider("v:env/decay", 0.9, 0.2, 3, 0.01);
drop  = nentry("drop", 2.0, 0.5, 6, 0.1);
bad   = hslider("bad", 1, 5, 5, 1);
'''


def main():
    # ---- zone parsing
    sp = to.zone_space(DSP)
    names = [z["name"] for z in sp]
    need(names == ["punch", "decay", "drop"],
         f"performance zones + degenerate bounds excluded (got {names})")
    need(sp[1]["name"] == "decay" and sp[1]["lo"] == 0.2,
         "grouped path 'v:env/decay' -> leaf name with bounds")
    need(to.zone_space("") == [] and to.zone_space(None) == [], "empty dsp -> []")

    # ---- the window meter
    w = {"centroid_hz": [800, 1400], "crest_db": [15, 25]}
    need(to.window_distance({"centroid_hz": 1000, "crest_db": 20}, w) == 0.0,
         "inside the window = 0")
    d = to.window_distance({"centroid_hz": 1700, "crest_db": 20}, w)
    need(abs(d - 1.0) < 1e-9, f"one half-width out = 1.0 (got {d})")
    d2 = to.window_distance({"crest_db": 20}, w)
    need(abs(d2 - 1.0) < 1e-9, "missing feature = one full violation, never assumed in")
    need(to.window_distance({}, {}) == 0.0, "empty window = 0")
    need(to.window_distance({"x": 5}, {"x": ["lo", "hi"]}) == 0.0,
         "garbage band skipped, no raise")

    # ---- the search: plants a 3-dim toy voice, must land inside
    space = [{"name": "punch", "default": 0.5, "lo": 0.0, "hi": 1.0, "step": 0.01},
             {"name": "decay", "default": 1.0, "lo": 0.2, "hi": 3.0, "step": 0.01},
             {"name": "drop", "default": 2.0, "lo": 0.5, "hi": 6.0, "step": 0.1}]
    target = {"punch": 0.82, "decay": 0.45, "drop": 3.4}

    def synth(pd):
        return {"centroid_hz": 900 + 2400 * abs(pd["punch"] - target["punch"])
                + 400 * abs(pd["drop"] - target["drop"]),
                "decay_ms": 300 + 800 * abs(pd["decay"] - target["decay"])}
    win = {"centroid_hz": [820, 1150], "decay_ms": [260, 420]}
    res = to.search(synth, space, win, budget=120, seed=5)
    need(res["best_distance"] == 0.0, f"ES lands the window (d={res['best_distance']})")
    need(res["evals"] < 120, f"early stop under budget (evals={res['evals']})")
    res2 = to.search(synth, space, win, budget=120, seed=5)
    need(res2["trace"] == res["trace"] and res2["best_params"] == res["best_params"],
         "same seed = same trajectory (deterministic replay)")
    res3 = to.search(synth, space, win, budget=6, seed=5)
    need(res3["evals"] <= 6, "budget is a hard cap")
    need(to.search(synth, [], win)["best_distance"] == float("inf"),
         "empty space = honest inf, no raise")
    hits = []
    to.search(synth, space, win, budget=20, seed=5,
              on_eval=lambda pd, f, d: hits.append(d))
    need(len(hits) == 20 or 0.0 in hits, "on_eval sees every evaluation")
    got_quant = to.search(synth, space, win, budget=30, seed=9)["best_params"]
    need(abs(got_quant["drop"] * 10 - round(got_quant["drop"] * 10)) < 1e-6,
         "step quantization honored")

    with tempfile.TemporaryDirectory(prefix="brainc_") as root:
        # ---- forge log + one_shot amortization
        need(to.one_shot("kick_808", win, root=root) == (None, None),
             "empty forge log -> honest (None, None)")
        to.forge_append("kick_808", {"punch": 0.8}, {"centroid_hz": 5000}, root=root, t=1)
        to.forge_append("kick_808", target, synth(target), root=root, t=2)
        to.forge_append("other", {"x": 1}, {"centroid_hz": 900}, root=root, t=3)
        ws, wd = to.one_shot("kick_808", win, root=root)
        need(ws == target and wd == 0.0, "one_shot returns the LANDED neighbor")
        with open(to.forge_path(root), "a") as f:
            f.write('{"torn: \n')
        ws2, _ = to.one_shot("kick_808", win, root=root)
        need(ws2 == target, "torn forge line never poisons")

        # ---- taste bank IO
        # THE FIXTURE LAW here: clean isotropic clusters make nearest-centroid
        # provably as good as logistic (first draft measured 0.9 == 0.9 and the
        # floor CORRECTLY refused). The head's reason to exist is correlated
        # noise ON the signal axis — centroid distance is fooled by the noise's
        # shadow; a learned line cancels it (LDA law). Measured on this seed:
        # head LOO 1.0 vs cold floor 0.75.
        import numpy as np
        rng = np.random.default_rng(11)

        def emb(label):
            e = rng.normal(0, 0.12, 64)
            n = rng.normal(0, 1.2)
            e[0] += (0.7 if label else -0.7) + n
            e[1] += n
            return (e / np.linalg.norm(e)).tolist()

        need(th.bank_rows(root) == [], "empty bank -> []")
        for i in range(20):
            th.bank_append(f"s{i}", True, emb(True), root=root, t=i)
        for i in range(10):
            th.bank_append(f"r{i}", False, emb(False), root=root, t=100 + i)
        rows = th.bank_rows(root)
        need(len(rows) == 30 and sum(r["accepted"] for r in rows) == 20,
             "bank rows round-trip with labels")

        # ---- train: learns separable taste, beats floors, persists
        rep = th.train(root=root)
        need(rep["trained"] is True, f"separable taste trains (rep={rep})")
        need(rep["loo_balanced_acc"] > max(rep["cold_floor_balanced_acc"], 0.5) - 1e-9
             and rep["loo_balanced_acc"] > 0.8,
             f"LOO beats floors (head={rep['loo_balanced_acc']} cold={rep['cold_floor_balanced_acc']})")
        need(os.path.exists(th.head_path(root)), "head persisted")
        pa = [th.score_emb(emb(True), root=root) for _ in range(8)]
        pr = [th.score_emb(emb(False), root=root) for _ in range(8)]
        need(all(s == "head" for _, s in pa + pr), "scores come from the head")
        mean_a = sum(p for p, _ in pa) / len(pa)
        mean_r = sum(p for p, _ in pr) / len(pr)
        need(mean_a > 0.5 > mean_r,
             f"head separates in expectation (acc={mean_a:.3f} rej={mean_r:.3f})")

        # ---- floors refuse: under-fed + unseparable
        with tempfile.TemporaryDirectory(prefix="brainc2_") as r2:
            for i in range(20):
                th.bank_append(f"s{i}", True, emb(True), root=r2, t=i)
            for i in range(3):                       # only 3 rejects < MIN_MINORITY
                th.bank_append(f"r{i}", False, emb(False), root=r2, t=50 + i)
            rep2 = th.train(root=r2)
            need(rep2["trained"] is False and "under-fed" in rep2["why"],
                 "skewed bank refused (the 111/11 reality)")
            need(not os.path.exists(th.head_path(r2)), "no head persisted when refused")
            p3, src3 = th.score_emb(emb(True), root=r2)
            need(src3 == "cold-floor" and p3 is not None,
                 "refused head -> cold floor still scores")
        with tempfile.TemporaryDirectory(prefix="brainc3_") as r3:
            for i in range(15):                      # SAME cloud both labels: no signal
                th.bank_append(f"s{i}", True, emb(True), root=r3, t=i)
            for i in range(15):
                th.bank_append(f"r{i}", False, emb(True), root=r3, t=50 + i)
            rep3 = th.train(root=r3)
            need(rep3["trained"] is False, f"unseparable taste NOT persisted (rep={rep3})")
        with tempfile.TemporaryDirectory(prefix="brainc4_") as r4:
            need(th.score_emb([0.1] * 64, root=r4) == (None, "no-data"),
                 "no bank at all -> honest (None, 'no-data')")

    # ---- GENRE KICK WINDOWS (BR-C wave 2): pure kernels — measured
    # envelopes only, tight aliases, honest misses
    import kick_windows as kw
    rows = [{"spectral_centroid_hz": 900.0, "crest_factor_db": 14.0},
            {"spectral_centroid_hz": 1500.0, "crest_factor_db": 18.0}]
    w = kw.rows_to_window(rows)
    need(w["spectral_centroid_hz"] == [630.0, 2175.0]
         and w["crest_factor_db"] == [10.0, 24.0],
         f"window = measured envelope, padded (got {w})")
    need(kw.rows_to_window([{"spectral_centroid_hz": 50.0,
                             "crest_factor_db": 10.0}]
                           )["spectral_centroid_hz"][0] == kw.CENT_FLOOR,
         "centroid floor clamps a sub-floor reference")
    need(kw.rows_to_window([{}]) is None,
         "no measurements -> no window (never invent a number)")
    bank = {"genres": {"goa": {"spectral_centroid_hz": [500, 4000],
                               "crest_factor_db": [8, 30]}}}
    need(kw.window_for("goa", bank) == bank["genres"]["goa"],
         "exact measured genre hit")
    via = kw.window_for("Psytrance", bank)
    need(bool(via) and via.get("via") == "goa",
         f"psytrance rides the MEASURED goa family window (got {via})")
    need(kw.window_for("dnb", bank) is None,
         "unmeasured genre -> None (generic window stands, honestly)")
    need(kw.window_for("goa", None) is None, "no bank -> None")
    notes = ([{"start": float(b)} for b in range(0, 8)] +
             [{"start": 40.0 + b * 0.5} for b in range(16)])
    need(kw.densest_span(notes) == 40.0,
         "densest span found past a sparse head (breakdown fallback)")
    sl = kw.slice_shift([{"start": 41.0, "len": 9.0}], 40.0)
    need(sl == [{"start": 1.0, "len": 7.0}],
         f"slice shifts to zero + clamps len (got {sl})")

    print(f"brainc_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
