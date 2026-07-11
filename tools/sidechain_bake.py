#!/usr/bin/env python3
"""sidechain_bake.py — TRUE keyed sidechain as BAKED automation. fx_pump is an
LFO that assumes four-on-the-floor; on swung trap, breakbeats or half-time the
duck lands where no kick is. This reads the trigger track's ACTUAL notes and
writes the duck as gainDb automation on the target tracks — real sidechain
feel, zero engine routing, fully inspectable/hand-editable points.

  sidechain_bake.py <song> [--trigger kick] [--targets bass,pad]
                    [--depth 4] [--attack 0.05] [--hold 0.05] [--release 0.4]
                    [--write]

Envelope per trigger note: dip to -depth over `attack` beats, hold, linear
release back; overlapping triggers merge by deepest-duck. Points are ABSOLUTE
gainDb (base + delta), thinned to the corners (vocal_rider.thin). --write
replaces each target's prior gainDb automation (other targets kept), like the
rider. Machine line: SIDECHAIN_JSON {...}.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from songname import resolve as resolve_song  # noqa: E402
from vocal_rider import thin  # noqa: E402

TRIGGER_WORDS = ("kick", "bd", "fourfloor")
TARGET_WORDS = ("bass", "808", "sub", "pad", "keys", "chord", "stab", "pluck")
GRID = 0.125  # 32nd-note envelope grid


def duck_envelope(trigger_beats, total_beats, depth=4.0, attack=0.05,
                  hold=0.05, release=0.4, grid=GRID):
    """Gain deltas (<= 0) on a grid UNIONED with each trigger's exact corner
    beats (onset / plateau start / plateau end / recovery) — automation plays
    linear between points, so without the corners a short attack+hold between
    grid points would bake a duck shallower than asked. Overlaps merge by
    deepest duck."""
    nb = int(np.ceil(total_beats / grid)) + 1
    corners = []
    for s in trigger_beats:
        corners += [s, s + attack, s + attack + hold, s + attack + hold + release]
    gb = np.unique(np.round(np.concatenate(
        [np.arange(nb) * grid, np.asarray(corners, dtype=float)]), 6))
    gb = gb[(gb >= 0) & (gb <= total_beats)]
    env = np.zeros(len(gb))
    for s in trigger_beats:
        rel_t = gb - s
        c = np.zeros(len(gb))
        m = (rel_t >= 0) & (rel_t < attack)
        c[m] = -depth * (rel_t[m] / max(attack, 1e-6))
        m = (rel_t >= attack) & (rel_t < attack + hold)
        c[m] = -depth
        m = (rel_t >= attack + hold) & (rel_t < attack + hold + release)
        c[m] = -depth * (1.0 - (rel_t[m] - attack - hold) / max(release, 1e-6))
        env = np.minimum(env, c)
    return gb, env


def pick_tracks(song, trigger=None, targets=None):
    tracks = song.get("tracks", [])
    trig = None
    if trigger:
        trig = next((t for t in tracks if t.get("name", "").lower() == trigger.lower()), None)
    if trig is None:
        trig = next((t for t in tracks
                     if any(w in t.get("name", "").lower() for w in TRIGGER_WORDS)
                     and t.get("notes")), None)
    if targets:
        names = [x.strip().lower() for x in targets.split(",") if x.strip()]
        tgts = [t for t in tracks if t.get("name", "").lower() in names]
    else:
        tgts = [t for t in tracks
                if any(w in t.get("name", "").lower() for w in TARGET_WORDS)
                and t is not trig]
    return trig, tgts


def plan(song, trigger=None, targets=None, depth=4.0, attack=0.05,
         hold=0.05, release=0.4):
    trig, tgts = pick_tracks(song, trigger, targets)
    if trig is None or not trig.get("notes"):
        return {"available": False, "why": "no trigger track with notes "
                "(name one with --trigger; kick-ish names auto-match)"}
    if not tgts:
        return {"available": False, "why": "no target tracks "
                "(--targets a,b; bass/pad-ish names auto-match)"}
    beats = sorted({round(float(n.get("start", 0)), 4) for n in trig["notes"]})
    total = float(song.get("lengthBars", 8)) * 4.0
    gb, env = duck_envelope(beats, total, depth, attack, hold, release)
    out = {"available": True, "trigger": trig.get("name"), "n_triggers": len(beats),
           "depth": depth, "attack": attack, "hold": hold, "release": release,
           "targets": []}
    for t in tgts:
        base = float(t.get("gainDb", 0.0))
        keep = thin(gb, env + base, eps=0.1, hard_cap=1200)
        pts = [{"beat": round(float(gb[i]), 3), "v": round(float(base + env[i]), 2)}
               for i in keep]
        out["targets"].append({"track": t.get("name"), "baseGainDb": base,
                               "n_points": len(pts),
                               "automation": {"target": "gainDb", "points": pts}})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="bake note-keyed sidechain duck automation")
    ap.add_argument("song")
    ap.add_argument("--trigger", default=None)
    ap.add_argument("--targets", default=None)
    ap.add_argument("--depth", type=float, default=4.0)
    ap.add_argument("--attack", type=float, default=0.05)
    ap.add_argument("--hold", type=float, default=0.05)
    ap.add_argument("--release", type=float, default=0.4)
    ap.add_argument("--write", action="store_true",
                    help="land the duck on each target track's automation")
    a = ap.parse_args(argv)

    songs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "songs")
    if a.song.endswith(".json") and os.path.exists(a.song):
        path = a.song
    elif "/" in a.song and ".." not in a.song \
            and os.path.exists(os.path.join(songs_dir, a.song + ".json")):
        path = os.path.join(songs_dir, a.song + ".json")   # crate/<name> etc.
    else:
        path = os.path.join(songs_dir, resolve_song(a.song) + ".json")
    if not os.path.exists(path):
        print("SIDECHAIN_JSON " + json.dumps(
            {"available": False, "why": f"song not found: {a.song}"}))
        return 3
    song = json.load(open(path))
    out = plan(song, a.trigger, a.targets, a.depth, a.attack, a.hold, a.release)
    print("SIDECHAIN_JSON " + json.dumps(
        {k: v for k, v in out.items() if k != "targets"}
        | ({"targets": [{k: v for k, v in t.items() if k != "automation"}
                        for t in out["targets"]]} if out.get("available") else {})))
    if not out.get("available"):
        return 3
    if a.write:
        by_name = {t["track"]: t for t in out["targets"]}
        for tr in song.get("tracks", []):
            hit = by_name.get(tr.get("name"))
            if not hit:
                continue
            autos = [x for x in tr.get("automation", []) if x.get("target") != "gainDb"]
            autos.append(hit["automation"])
            tr["automation"] = autos
        json.dump(song, open(path, "w"), indent=1)
        print(f"[sidechain_bake] wrote {len(by_name)} duck lane(s) into {path}")
    else:
        for t in out["targets"]:
            print(f"  {t['track']}: {t['n_points']} points "
                  f"(apply via automate, or --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
