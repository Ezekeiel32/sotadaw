#!/usr/bin/env python3
"""ENERGY CURVE — the song's energy over bars, as data + sight (read-only).

  energy_curve.py <song> [--track NAME]

The Tier-1 'energy canvas' data source (docs/SURFACE_LEDGER.md #2): per-bar
energy = mean velocity x note density, drums weighted whole, melodic weighted
by sustain coverage. Emits a per-bar total + per-track rows + per-section
means, an ASCII sparkline (sight, not metrology — the hear-tensor law), and
ENERGY_JSON for the canvas/agent. Pairs with intensify: the curve SHOWS where
the contrast law is violated (a build as loud as its drop = no impact);
intensify(section,+/-) is the fix. Symbolic, no render, ~ms.

Why velocity x DENSITY and not level: Farbood's tension studies — 65% of
responses found loudness change did NOT read as tension change; the climax is
marked by a sudden increase in TEXTURAL DENSITY, and onset frequency is a
first-class parameter of her tension model (docs/SURFACE_LEDGER.md refs).
"""
import argparse, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import is_drum_track
import songname

BLOCKS = " .:-=+*#%@"


def track_bar_energy(t, bar):
    """One track's energy inside [bar, bar+1): velocity mass x coverage.
    Drums count ONSETS in the bar; melodic counts SUSTAIN OVERLAP — a held pad
    keeps radiating energy across every bar it spans (the eval_house lesson:
    start-bar-only read a 16-beat pad as 0.5,0,0,0)."""
    a, b = bar * 4.0, bar * 4.0 + 4.0
    if is_drum_track(t):
        win = [n for n in t.get("notes", []) if a <= float(n["start"]) < b]
        if not win:
            return 0.0
        vel = sum(float(n.get("vel", 0.8)) for n in win) / len(win)
        return vel * min(1.0, len(win) / 16.0)      # 16 hits/bar = saturated
    cov, vmass = 0.0, 0.0
    for n in t.get("notes", []):
        s = float(n["start"]); e = s + float(n.get("len", 0.25))
        ov = min(b, e) - max(a, s)
        if ov > 0:
            cov += ov
            vmass += ov * float(n.get("vel", 0.8))
    if cov <= 0:
        return 0.0
    return (vmass / cov) * min(1.0, cov / 4.0)      # full-bar sustain = saturated


def energy(song, only_track=None):
    bars = int(math.ceil(float(song.get("lengthBars", 0))))
    tracks = [t for t in song.get("tracks", []) if t.get("notes")
              and (only_track is None or t.get("name") == only_track)]
    rows = {t.get("name", "?"): [round(track_bar_energy(t, b), 3) for b in range(bars)]
            for t in tracks}
    total = [round(sum(r[b] for r in rows.values()), 3) for b in range(bars)]
    peak = max(total) if total and max(total) > 0 else 1.0
    curve = [round(v / peak, 3) for v in total]     # normalized 0..1, peak = 1
    secs = sorted(song.get("sections", []), key=lambda s: float(s["startBar"]))
    sections = []
    for i, s in enumerate(secs):
        lo = int(float(s["startBar"]))
        hi = int(float(secs[i + 1]["startBar"])) if i + 1 < len(secs) else bars
        span = curve[lo:hi]
        sections.append({"name": s.get("name", "?"), "from_bar": lo, "to_bar": hi,
                         "mean": round(sum(span) / len(span), 3) if span else 0.0})
    # the contrast law, checked: a drop-like section should sit clearly above its
    # predecessor; name the flattest offender so intensify knows where to cut
    flat = None
    for i in range(1, len(sections)):
        a, b2 = sections[i - 1], sections[i]
        if any(k in b2["name"].lower() for k in ("drop", "chorus", "hook")) \
                and b2["mean"] > 0 and a["mean"] >= b2["mean"] * 0.85:
            gap = round(b2["mean"] - a["mean"], 3)
            if flat is None or gap < flat["gap"]:
                flat = {"before": a["name"], "drop": b2["name"], "gap": gap,
                        "fix": f"intensify('{a['name']}', -0.4) + intensify('{b2['name']}', +0.4)"}
    return {"bars": bars, "curve": curve, "tracks": rows, "sections": sections,
            "contrast_violation": flat}


def spark(curve):
    return "".join(BLOCKS[min(len(BLOCKS) - 1, int(v * (len(BLOCKS) - 1) + 0.5))]
                   for v in curve)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--track", default=None)
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    rep = energy(song, a.track)
    print(f"[energy] {name}: {rep['bars']} bars, peak-normalized")
    print("  " + spark(rep["curve"]))
    for s in rep["sections"]:
        bar = "#" * int(s["mean"] * 24)
        print(f"  {s['name']:<10} bars {s['from_bar']:>3}-{s['to_bar']:<3} {s['mean']:.2f} {bar}")
    if rep["contrast_violation"]:
        cv = rep["contrast_violation"]
        print(f"  CONTRAST LAW: '{cv['before']}' is as loud as '{cv['drop']}' "
              f"(gap {cv['gap']}) — the drop has nowhere to go. Fix: {cv['fix']}")
    print("ENERGY_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
