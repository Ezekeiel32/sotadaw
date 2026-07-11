#!/usr/bin/env python3
"""ENERGY CURVE battery — the curve tells the truth about the arrangement.

  E1 a hard drop reads higher than a soft intro (ordering truth)
  E2 flat song -> flat curve (no invented dynamics)
  E3 silence reads zero; normalization peaks at 1.0
  E4 sections aggregate correctly (drop mean > intro mean)
  E5 contrast law: build-as-loud-as-drop is FLAGGED with the intensify fix;
     a proper valley before the drop is NOT flagged
  E6 intensify(drop,+) RAISES the drop's curve mean (the pair composes)
  E7 sparkline length == bars; only legal glyphs
Exit 1 on any failure. Pure symbolic."""
import copy, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from energy_curve import energy, spark, BLOCKS
from intensify import intensify

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def song_with(intro_vel, drop_vel, drop_dense=True):
    """8 bars: intro (0-4) vs drop (4-8)."""
    hats, lead = [], []
    for bar in range(8):
        v = drop_vel if bar >= 4 else intro_vel
        step = 0.25 if (bar >= 4 and drop_dense) else 0.5
        b = bar * 4.0
        while b < bar * 4.0 + 4.0:
            hats.append({"start": round(b, 3), "len": 0.1, "pitch": 42, "vel": v})
            b += step
        lead.append({"start": bar * 4.0, "len": 3.5, "pitch": 60, "vel": v})
    return {"version": 2, "bpm": 124, "lengthBars": 8, "key": "C minor",
            "sections": [{"name": "intro", "startBar": 0}, {"name": "drop", "startBar": 4}],
            "tracks": [
                {"name": "hats", "source": {"kind": "faust", "id": "hat_metal"}, "notes": hats},
                {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "notes": lead}]}


def main():
    s = song_with(0.35, 0.95)
    rep = energy(s)
    intro = [v for v in rep["curve"][:4]]
    drop = [v for v in rep["curve"][4:]]
    check("E1 hard drop > soft intro on every bar",
          min(drop) > max(intro), f"intro max {max(intro)} vs drop min {min(drop)}")

    flat = song_with(0.7, 0.7, drop_dense=False)
    rf = energy(flat)
    check("E2 flat song -> flat curve",
          max(rf["curve"]) - min(rf["curve"]) < 0.05, f"range {max(rf['curve'])-min(rf['curve']):.3f}")

    empty = {"version": 2, "bpm": 120, "lengthBars": 4, "sections": [],
             "tracks": [{"name": "x", "source": {"kind": "faust", "id": "pluck"},
                         "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}]}]}
    re_ = energy(empty)
    check("E3 silent bars read 0; peak normalizes to 1.0",
          re_["curve"][0] == 1.0 and all(v == 0.0 for v in re_["curve"][1:]), str(re_["curve"]))

    secs = {x["name"]: x["mean"] for x in rep["sections"]}
    check("E4 section means aggregate (drop > intro)",
          secs["drop"] > secs["intro"] * 1.5, json.dumps(secs))

    # E5 the contrast law
    loudbuild = song_with(0.92, 0.95, drop_dense=False)   # build ~as loud as drop
    rl = energy(loudbuild)
    v = rl["contrast_violation"]
    check("E5a build-as-loud-as-drop is FLAGGED with the intensify pair",
          v is not None and "intensify" in v["fix"] and v["drop"] == "drop", json.dumps(v))
    check("E5b a proper valley is NOT flagged", energy(s)["contrast_violation"] is None)

    # E6 compose with intensify: harder drop -> higher drop mean. The drop must
    # have HEADROOM (moderate vel + 8th hats) — a maxed drop honestly can't rise
    # (first battery run proved it: vel .95 + 16ths -> only +2%).
    s2 = song_with(0.35, 0.7, drop_dense=False)
    s = song_with(0.35, 0.7, drop_dense=False)
    intensify(s2, "drop", 0.8)
    # renormalize caveat: compare UNNORMALIZED by scaling with the new peak — use
    # section mean of the raw totals instead: recompute both raw
    def raw_drop_mean(sng):
        r = energy(sng)
        peak_rows = r["tracks"]
        tot = [sum(rr[b] for rr in peak_rows.values()) for b in range(r["bars"])]
        return sum(tot[4:]) / 4.0
    check("E6 intensify(drop,+) raises the drop's raw energy",
          raw_drop_mean(s2) > raw_drop_mean(s) * 1.05,
          f"{raw_drop_mean(s):.3f} -> {raw_drop_mean(s2):.3f}")

    sp = spark(rep["curve"])
    check("E7 sparkline: one glyph per bar, legal alphabet",
          len(sp) == rep["bars"] and all(ch in BLOCKS for ch in sp), sp)

    # E8 sustain spill: a single 16-beat pad radiates across all 4 bars equally
    pad = {"version": 2, "bpm": 120, "lengthBars": 4, "sections": [],
           "tracks": [{"name": "pad", "source": {"kind": "faust", "id": "warmpad"},
                       "notes": [{"start": 0, "len": 16, "pitch": 60, "vel": 0.8}]}]}
    rp = energy(pad)
    check("E8 a held pad sustains energy across every bar it spans",
          rp["curve"] == [1.0, 1.0, 1.0, 1.0], str(rp["curve"]))

    print(f"\n== ENERGY: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE CURVE TELLS THE TRUTH (canvas data source ready)")


if __name__ == "__main__":
    main()
