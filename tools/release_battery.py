#!/usr/bin/env python3
"""THE RELEASE GATE battery (AMAZING PART III assembly) — fixture-pure.

Proves: the band-order kernel never guesses, G2 convicts every window
breach and names every unknowable, G3 blocks only on a FED verdict (skips
are honest), G4 kills foreign replay / pardons self-match / honors shared
idioms / skips index-less, G1 surfaces key-court and floor hard traps, and
the assembled verdict enforces the pass law with G5 always named."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import composer_prior as cp
import release_gate as rg

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


def _song(pitches, key="A minor", step=0.25):
    return {"version": 2, "bpm": 128, "key": key, "lengthBars": 4,
            "tracks": [{"name": "lead",
                        "notes": [{"start": i * step, "len": 0.2,
                                   "pitch": p, "vel": 0.8}
                                  for i, p in enumerate(pitches)]}]}


def main():
    # ---- band-order kernel
    bands = {"low_20_120": 60.0, "lowmid_120_500": 25.0, "mid_500_2k": 10.0,
             "himid_2k_6k": 4.0, "high_6k_up": 1.0}
    need(rg.band_rank_ok("low>lowmid>mid", bands) is True, "band order holds")
    need(rg.band_rank_ok("mid>low", bands) is False, "band order broken -> False")
    need(rg.band_rank_ok("low>sub", bands) is None, "unknown band -> None (never guess)")
    need(rg.band_rank_ok("", bands) is None, "no law -> None")
    need(rg.band_rank_ok("low>mid", {}) is None, "no metrics -> None")

    # ---- G2 REFERENCE
    gold = {"mixtarget": {"lufs_lo": -14, "lufs_hi": -8, "psr_floor": 6.0,
                          "band_order": "low>lowmid>mid",
                          "clipped_samples": 0},
            "measured": {"lufs": -11.0, "bands": dict(bands)}}
    a_ok = {"lufs_integrated": -10.5, "clipped_samples": 0,
            "true_peak_dbtp": -1.6, "psr": 7.2,
            "band_energy_pct": dict(bands)}
    g2 = rg.g2_reference(a_ok, gold, "house")
    need(g2["pass"] and not g2["hard"], f"in-window take passes (got {g2['hard']})")
    need(g2["readout"].get("lufs") == [-10.5, -14, -8]
         and g2["readout"].get("psr") == [7.2, 6.0],
         "readout carries the measured-vs-window rows")
    need(g2["readout"].get("measured_lufs_delta") == 0.5
         and g2["readout"].get("measured_bands_l1") == 0.0,
         "gold measured closeness is a readout row")
    need(not rg.g2_reference(dict(a_ok, lufs_integrated=-6.0), gold, "house")["pass"],
         "LUFS past the window convicts")
    need(not rg.g2_reference(dict(a_ok, clipped_samples=12), gold, "house")["pass"],
         "clipped samples convict")
    need(not rg.g2_reference(dict(a_ok, true_peak_dbtp=-0.3), gold, "house")["pass"],
         "true peak past the wall convicts")
    need(not rg.g2_reference(dict(a_ok, psr=4.0), gold, "house")["pass"],
         "PSR under the genre floor convicts")
    bad_bands = dict(bands, lowmid_120_500=5.0, mid_500_2k=25.0)
    need(not rg.g2_reference(dict(a_ok, band_energy_pct=bad_bands),
                             gold, "house")["pass"],
         "broken band order convicts")
    g2n = rg.g2_reference(dict(a_ok, psr=9.0), None, "no_such_genre")
    need(g2n["pass"] and any("no gold exemplar" in g for g in g2n["gaps"]),
         f"goldless genre: unjudged windows are NAMED, never guessed (got {g2n})")

    # ---- G3 TASTE (injected rails — no clap/model in the fixture)
    g3 = rg.g3_taste(__file__, embed=lambda p: [0.1] * 8,
                     score=lambda e, root=None: (0.9, "head"))
    need(g3["state"] == "pass" and g3["score"] == 0.9, "fed head passing take")
    g3f = rg.g3_taste(__file__, embed=lambda p: [0.1] * 8,
                      score=lambda e, root=None: (0.2, "cold-floor"))
    need(g3f["state"] == "fail", "a FED floor saying reject blocks")
    g3s = rg.g3_taste(__file__, embed=lambda p: [0.1] * 8,
                      score=lambda e, root=None: (None, "no-data"))
    need(g3s["state"] == "skip" and "dry" in g3s["why"], "dry bank skips honestly")
    g3x = rg.g3_taste(__file__,
                      embed=lambda p: (_ for _ in ()).throw(RuntimeError()),
                      score=None)
    need(g3x["state"] == "skip", "a dying taste rail skips, never crashes the gate")
    need(rg.g3_taste("/nonexistent.wav")["state"] == "skip", "no audio -> skip")

    # ---- G4 NOVELTY
    fix = _song([57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76,
                 77, 79, 81, 83, 84, 83, 81, 79, 77, 76, 74, 72])
    toks = cp.tokenize(fix)
    seq = [cp._tkey(t) for t in toks[0][1]]
    foreign = {"ngrams": {"|".join(seq[i:i + cp.NGRAM]): ["other_song"]
                          for i in range(len(seq) - cp.NGRAM + 1)}}
    g4 = rg.g4_novelty(fix, self_ids=(), model=foreign)
    need(g4["state"] == "fail" and g4["stolen_roles"] == ["lead"],
         f"foreign verbatim replay convicts (got {g4})")
    need(rg.g4_novelty(fix, self_ids={"other_song"},
                       model=foreign)["state"] == "pass",
         "SELF-MATCH pardoned: a song may resemble its own history")
    shared = {"ngrams": {h: ["a", "b"] for h in foreign["ngrams"]}}
    need(rg.g4_novelty(fix, model=shared)["state"] == "pass",
         "shared idioms are language, not theft")
    need(rg.g4_novelty(fix, model={"ngrams": {}})["state"] == "skip",
         "no corpus index -> honest skip")
    need(any("gold exemplar" in g for g in g4.get("gaps") or []),
         "the self-clone-vs-gold gap is NAMED")

    # ---- G1 CENSUS (real courts on deterministic fixtures)
    sour = _song([61, 61, 66, 66, 68, 68, 61, 66, 68, 61, 66, 68] * 2,
                 key="C major")
    v1 = rg.g1_census(sour, "pop", None)
    need(any("key court" in h for h in v1["hard"]),
         f"sour take convicted by the key court (got {v1['hard']})")
    clean = _song([60, 62, 64, 65, 67, 69, 71, 72, 71, 69, 67, 65] * 2,
                  key="C major")
    v2 = rg.g1_census(clean, "pop", None)
    need(not any("key court" in h for h in v2["hard"]),
         f"clean take has no key conviction (got {v2['hard']})")
    v3 = rg.g1_census(clean, "pop",
                      {"lufs_integrated": -40.0, "peak_dbfs": -30.0})
    need(any(h == "floor:silent_take" for h in v3["hard"]),
         f"worldclass floor hard trap surfaces (got {v3['hard']})")

    # ---- the assembled verdict: pass law + honest-gap ledger
    ok = {"pass": True, "hard": []}
    ref = {"pass": True, "hard": [], "gaps": ["band order unknowable"],
           "readout": {}}
    tp = {"state": "pass", "score": 0.8}
    ts = {"state": "skip", "why": "clap unavailable"}
    tf = {"state": "fail", "score": 0.1}
    npv = {"state": "pass", "gaps": []}
    nf = {"state": "fail", "stolen_roles": ["lead"], "gaps": []}
    v = rg.assemble(ok, ref, tp, npv, song_name="x", genre="house")
    need(v["pass"] is True, "all gates green -> pass")
    need(any("G5 BLIND" in g for g in v["gaps"]),
         "G5 is ALWAYS named — no silent fifth gate")
    need("band order unknowable" in v["gaps"], "reference gaps propagate")
    need(rg.assemble(ok, ref, ts, npv)["pass"] is True,
         "a SKIPPED taste never blocks")
    need(rg.assemble(ok, ref, tf, npv)["pass"] is False,
         "a FED taste reject blocks")
    need(rg.assemble(ok, ref, tp, nf)["pass"] is False, "novelty theft blocks")
    need(rg.assemble({"pass": False, "hard": ["x court: not ok"]},
                     ref, tp, npv)["pass"] is False, "census hard blocks")
    need(rg.assemble(ok, {"pass": False, "hard": ["LUFS out"], "gaps": []},
                     tp, npv)["pass"] is False, "reference breach blocks")
    v5 = rg.assemble(ok, ref, ts, {"state": "skip", "why": "no index"},
                     extra_gaps=["RENDER FAILED"])
    need("RENDER FAILED" in v5["gaps"]
         and any("G4 NOVELTY skipped" in g for g in v5["gaps"]),
         "extra + skip gaps all land in the ledger")

    # ---- THE GATE CHIP (PART V rider) + prop-twin self-pardon
    chip = rg.gate_chip(rg.assemble(
        {"pass": False, "hard": ["x court: not ok", "y court: not ok"]},
        {"pass": False, "hard": ["LUFS out"], "gaps": ["g"]}, ts, npv))
    need(chip["pass"] is False and chip["hard"] == 3
         and chip["hard_top"][0] == "x court: not ok"
         and chip["novelty"] == "pass",
         f"gate chip mirrors the verdict compactly (got {chip})")
    need(rg.gate_chip({}) == {"pass": False, "hard": 0, "hard_top": [],
                              "gaps": 0, "taste": None, "novelty": "skip"},
         "empty verdict -> safe empty chip")
    sid = rg._self_ids("/x/songs/_prop_untitled_9.json")
    need("songs/untitled_9.json" in sid and "songs/_prop_untitled_9.json" in sid,
         f"prop twin pardons its own BASE song (got {sorted(sid)})")

    # ---- THE READOUT (AMAZING PART V): stable fields, honest unknowns,
    # the diff mechanics
    import tempfile
    import readout as ro
    need(ro._ears({})[0].startswith("unrendered"),
         "no render -> the EARS line SAYS so")
    et, ev = ro._ears({"lufs_integrated": -10.53, "psr": 7.24,
                       "clipped_samples": 0})
    need(ev == {"lufs": -10.5, "psr": 7.2, "clipped": 0}
         and et.startswith("lufs "),
         f"ears rounds + keeps stable order (got {ev})")
    ct, cd = ro._court_lines({"key": {"ok": False}, "melody": {"flags": [1, 2]},
                              "arc": {"ok": True}})
    need(ct.startswith("bad: key") and "melody 2" in ct and "ok: arc" in ct,
         f"courts: bad first, flagged counted, ok last (got {ct})")
    need("first readout" in ro._diff(None, {}),
         "no stamp -> first-readout line")
    prev = {"lanes": {"lead": 10}, "ears": {"lufs": -12.0},
            "courts": {"bad": ["groove"]}, "gate": {"census": "FAIL"}}
    cur = {"lanes": {"lead": 28, "bass": 4}, "ears": {"lufs": -10.4},
           "courts": {"bad": []}, "gate": {"census": "ok"}}
    d = ro._diff(prev, cur)
    need("notes +22" in d and "lead +18" in d and "lufs +1.6" in d
         and "groove court healed" in d and "census FAIL->ok" in d,
         f"diff carries deltas, heals, gate flips (got {d})")
    need("NEW-BAD" in ro._diff({"lanes": {}, "courts": {"bad": []}},
                               {"lanes": {}, "courts": {"bad": ["key"]}}),
         "a newly bad court is CALLED OUT")
    need(ro._diff(prev, prev) == "no change since the last readout",
         "identical stamps -> honest no-change")
    with tempfile.TemporaryDirectory(prefix="ro_") as td:
        spath = os.path.join(td, "fix.json")
        json.dump(_song([60, 62, 64, 65, 67, 69, 71, 72] * 3,
                        key="C major"), open(spath, "w"))
        t1, d1 = ro.readout(spath, genre="pop")
        lines = t1.splitlines()
        need([ln.split()[0] for ln in lines] ==
             ["TAKE", "EARS", "GATE", "COURTS", "DIFF"],
             f"THE STABLE PAGE: five fields, fixed order (got "
             f"{[ln.split()[0] for ln in lines]})")
        need(d1["text_chars"] <= ro.MAX_CHARS, "<=2K chars by law")
        need("unrendered" in lines[1] and "first readout" in lines[4],
             "unrendered + first-readout honesty on a fresh fixture")
        need(os.path.exists(os.path.join(td, ".readout", "fix.json")),
             "stamp lands BESIDE the song (tmp fixtures never pollute prod)")
        s2 = _song([60, 62, 64, 65, 67, 69, 71, 72] * 3, key="C major")
        s2["tracks"][0]["notes"] += [{"start": 12.0, "len": 0.5,
                                      "pitch": 64, "vel": 0.8}]
        json.dump(s2, open(spath, "w"))
        t2, _ = ro.readout(spath, genre="pop")
        need("notes +1" in t2.splitlines()[4],
             f"the diff SEES the added note (got {t2.splitlines()[4]})")

    print(f"release_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
