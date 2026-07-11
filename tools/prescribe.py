#!/usr/bin/env python3
"""PRESCRIBE — diagnose (doctor) then auto-APPLY the safe fixes, one call.

  prescribe.py <song> [--out name] [--write]

Closes the 'make it better' loop: doctor finds the issues, prescribe applies the
fix tools that are SAFE to auto-run (non-destructive, additive), then re-diagnoses
to PROVE the issue count dropped. Self-verifying, symbolic, no render.

Applied automatically (safe, additive):
  M1/M2/M3 mix issues  -> automix (center subs, widen pads, unmask, center focal)
  F1 dead-mechanical    -> humanize the offending track
  X1 no master limiter  -> add fx_truepeak ceiling -1.2 (release wall)
Reported but NOT auto-applied (need a creative decision):
  A1 no arrangement     -> suggest finish/arrange (would restructure the song)
  A2 doesn't breathe    -> suggest harmonize sectioned (rewrites parts)
  H1 no harmony         -> suggest writing a chordal part
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import doctor as D
import automix as M
from expressive import humanize, nomml_level
from chordvote import is_drum_track
import songname

AUTO = {"M1", "M2", "M3", "F1", "X1"}
SUGGEST = {"A1", "A2", "H1", "C1", "C2", "C3", "C4"}


def prescribe(song):
    before = D.diagnose(song)
    before_codes = [c for c, _, _ in before]
    applied, suggested = [], []

    # X1: master limiter — fx_truepeak (firing-100 release wall: BS.1770 detector +
    # 1dB reconstruction margin; ceiling means output dBTP, no -3 insurance tax)
    if "X1" in before_codes and not any(f.get("id") in ("fx_truepeak", "fx_brickwall")
                                        for f in song.get("master", [])):
        song.setdefault("master", []).append({"id": "fx_truepeak", "params": {"ceiling": -1.2}})
        song["masterGainDb"] = 0.0
        applied.append("added fx_truepeak ceiling -1.2 dBTP (release wall)")

    # F1: humanize each dead-mechanical melodic track
    for t in song.get("tracks", []):
        if is_drum_track(t) or not t.get("notes") or t.get("locked") or len(t["notes"]) < 8:
            continue
        _, cls = nomml_level(t["notes"])
        vels = {round(n.get("vel", 0.8), 2) for n in t["notes"]}
        if cls == "mechanical" and len(vels) <= 1:
            t["notes"] = humanize(t["notes"], 0.6, seed=0)
            applied.append(f"humanized '{t.get('name')}' (was dead-mechanical)")

    # M1/M2/M3: automix (idempotent, only moves what's wrong)
    if any(c in before_codes for c in ("M1", "M2", "M3")):
        mv = M.automix(song)
        if mv:
            applied.append(f"automix: {len(mv)} mix moves (subs/pads/unmask/focal)")

    # suggestions for the creative-decision issues
    for c, what, fix in before:
        if c in SUGGEST:
            suggested.append(f"[{c}] {what} -> {fix}")

    after = D.diagnose(song)
    after_codes = [c for c, _, _ in after]
    # only AUTO codes should have dropped; SUGGEST codes remain by design
    auto_before = [c for c in before_codes if c in AUTO]
    auto_after = [c for c in after_codes if c in AUTO]
    return {"before": before_codes, "after": after_codes,
            "auto_fixed": sorted(set(auto_before) - set(auto_after)),
            "auto_remaining": auto_after, "applied": applied, "suggested": suggested}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--out", default=None)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    rep = prescribe(song)
    out = re.sub(r"[^a-z0-9_]", "", a.out.lower()) if a.out else name
    if a.write or a.out:
        json.dump(song, open(os.path.join(ROOT, "songs", f"{out}.json"), "w"), indent=1)
    print(f"[prescribe] {name}: {len(rep['before'])} issues -> {len(rep['after'])} "
          f"(auto-fixed {rep['auto_fixed']})")
    for x in rep["applied"]:
        print("  APPLIED " + x)
    for x in rep["suggested"]:
        print("  SUGGEST " + x)
    print("PRESCRIBE_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
