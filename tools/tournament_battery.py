#!/usr/bin/env python3
"""THE TOURNAMENT battery (A3-T1, docs/SPEC_TRANSCENDENCE.md).

Pure: the bracket proven with injected courts (no heavy imports), the seed
law proven stable, the bank proven append-only in a tempdir. One REAL leg
at the end (real music_court on a tiny doc) proves the default path wires.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tournament as tn

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def fake_courts(verdicts):
    def c(doc, genre):
        return verdicts[doc["i"]]
    return c


def main():
    # seed law: deterministic, incumbent-first, stable values
    s1 = tn.derive_seeds(42, 3)
    s2 = tn.derive_seeds(42, 3)
    ok(s1 == s2 and s1[0] == 42 and len(s1) == 3, f"seed law stable {s1}")
    ok(len(set(s1)) == 3, "derived seeds distinct")
    ok(tn.derive_seeds(0, 1) == [0], "k=1 = the requested seed only")

    # bracket: clean beats penalized beats DQ; incumbent wins ties
    V = [
        {"key": {"ok": True}, "flow": {"ok": False}, "melody": {"ok": False}},
        {"key": {"ok": True}, "flow": {"ok": True}},
        {"key": {"ok": False}},
    ]
    docs = [{"i": i} for i in range(3)]
    scored = [tn.score_doc(d, "g", courts=fake_courts(V)) for d in docs]
    ok(scored[2]["dq"] and "key" in scored[2]["why"], "off-key = DQ class")
    ok(scored[0]["penalties"] == 2, "penalty count on advisory fails")
    w, summary = tn.pick(scored)
    ok(w == 1, f"cleanest candidate wins (#{w})")
    ok("WINNER" in summary and "DQ" in summary,
       "podium summary names the verdicts")
    # incumbent tie-break: identical scores -> #0
    V2 = [{"key": {"ok": True}}, {"key": {"ok": True}}]
    scored2 = [tn.score_doc({"i": i}, "g", courts=fake_courts(V2))
               for i in range(2)]
    w2, _ = tn.pick(scored2)
    ok(w2 == 0, "INCUMBENT LAW: ties go to the requested seed")
    # constitution violation is DQ-class too
    V3 = [{"constitution": {"ok": False}}, {"key": {"ok": True},
                                            "flow": {"ok": False},
                                            "melody": {"ok": False},
                                            "harmony": {"ok": False}}]
    scored3 = [tn.score_doc({"i": i}, "g", courts=fake_courts(V3))
               for i in range(2)]
    w3, _ = tn.pick(scored3)
    ok(w3 == 1, "a 3-penalty clean take beats a constitution violator")
    # courts crash = neutral, never fatal
    def boom(doc, genre):
        raise RuntimeError("no libs")
    s = tn.score_doc({"i": 0}, "g", courts=boom)
    ok(not s["dq"] and s["penalties"] == 0, "courts crash scores neutral")
    # all-DQ field: least-bad still picked deterministically
    V4 = [{"key": {"ok": False}}, {"key": {"ok": False}}]
    w4, _ = tn.pick([tn.score_doc({"i": i}, "g", courts=fake_courts(V4))
                     for i in range(2)])
    ok(w4 == 0, "all-DQ field: incumbent survives (least-bad, deterministic)")

    # bank: append-only rows in a tempdir
    root = tempfile.mkdtemp(prefix="tourn_bat_")
    try:
        tn.bank(root, "s", "g", s1, scored, w)
        tn.bank(root, "s", "g", s1, scored, w)
        rows = [json.loads(l) for l in
                open(os.path.join(root, "telemetry", "tournament.jsonl"))]
        ok(len(rows) == 2 and rows[0]["winner"] == w
           and rows[0]["seeds"] == s1, "losers banked as preference rows")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # REAL leg: default courts path wires (tiny doc, real music_court)
    doc = {"bpm": 120, "key": "A minor", "lengthBars": 4,
           "tracks": [{"name": "kick", "notes": [
               {"start": float(b), "pitch": 36, "vel": 0.9, "len": 0.5}
               for b in range(16)]}]}
    s_real = tn.score_doc(doc, "house")
    ok(isinstance(s_real, dict) and "penalties" in s_real,
       f"real courts path scores ({s_real['why'][:40]})")

    print(f"\ntournament_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
