#!/usr/bin/env python3
"""MOVEMENT IS MANDATORY — wave 53 (R-17 item 079).

The bass/pad archetypes are DEFINED by their motion, not their
oscillator: a reese without filter travel, a pad without slow cutoff
drift, a static psy bass — incomplete patches, the r-17 finding.
Symbolic court on song.json (advisory) + a deterministic bounded heal
(proposals only): give the lane an fx_filter and a slow late-bloom
cutoff journey via automation[] — the house motion primitive.

  court_movement(song, genre)   static sustained archetype lanes flagged
  heal_movement(song, verdict)  fx_filter (only if the lane has NO
                                filter — hand work sacred) + a 4-point
                                cutoff arc over the lane's sounding span
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ARCH_WORDS = ("pad", "reese", "bass", "drone", "atmo", "texture",
               "string", "choir")
_MIN_BARS = 16          # under this, stillness is a phrase, not a patch


def _archetype_lanes(song):
    out = []
    for i, t in enumerate((song or {}).get("tracks", []) or []):
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")):
            continue
        if any(w in nm for w in _ARCH_WORDS):
            out.append((i, t))
    return out


def _sounding_span_bars(t):
    starts = [float(n.get("start", 0)) for n in t.get("notes") or []]
    ends = [float(n.get("start", 0)) + float(n.get("len", 0) or 0)
            for n in t.get("notes") or []]
    if not starts:
        return 0, 0, 0
    a, b = min(starts), max(ends)
    return a / 4.0, b / 4.0, (b - a) / 4.0


def _has_motion(song, idx, t):
    """Motion = automation on this track, velocity life, or an fx knob
    journey already riding it."""
    for a in (t.get("automation") or []):
        if (a.get("points") or []) and len(a["points"]) >= 2:
            return True
    vels = [int(n.get("vel", 96)) for n in (t.get("notes") or [])]
    if vels and (max(vels) - min(vels)) >= 12:
        return True
    return False


def court_movement(song, genre=""):
    advisories = []
    for idx, t in _archetype_lanes(song):
        a, b, span = _sounding_span_bars(t)
        if span < _MIN_BARS:
            continue
        if _has_motion(song, idx, t):
            continue
        advisories.append({
            "kind": "static_archetype", "track": t.get("name"),
            "bars": round(span, 1),
            "why": (f"'{t.get('name')}' holds {span:.0f} bars with no "
                    "automation, flat velocities and no knob journey — "
                    "the pad/bass families are DEFINED by motion; a "
                    "static patch reads as a preset, not a part")})
    return {"court": "movement", "ok": True, "advisories": advisories}


def heal_movement(song, verdict=None):
    """The slow filter journey: fx_filter (minted only when the lane has
    no filter) + 4 cutoff points over the sounding span, late-bloom
    curve — motion, bounded, one undo step."""
    v = verdict or court_movement(song)
    actions = []
    by_name = {t.get("name"): t for t in (song or {}).get("tracks", [])
               if isinstance(t, dict)}
    for adv in v.get("advisories", []):
        t = by_name.get(adv.get("track"))
        if t is None:
            continue
        fx = t.setdefault("fx", [])
        fi = next((i for i, f in enumerate(fx)
                   if "filter" in str(f.get("id", ""))), None)
        if fi is None:
            fx.append({"id": "fx_filter",
                       "params": {"cutoff": 9000, "res": 0.9}})
            fi = len(fx) - 1
        elif any(a.get("target", "").startswith(f"fx[{fi}]")
                 for a in t.get("automation") or []):
            continue                    # its filter already journeys
        a, b, span = _sounding_span_bars(t)
        a_beat, b_beat = a * 4.0, b * 4.0
        third = (b_beat - a_beat) / 3.0
        t.setdefault("automation", []).append({
            "target": f"fx[{fi}].cutoff",
            "points": [{"beat": round(a_beat, 2), "v": 1800, "curve": 0.5},
                       {"beat": round(a_beat + third, 2), "v": 6500,
                        "curve": -0.3},
                       {"beat": round(a_beat + 2 * third, 2), "v": 3200,
                        "curve": 0.5},
                       {"beat": round(b_beat, 2), "v": 8500}]})
        actions.append({
            "kind": "movement_heal", "track": t.get("name"),
            "fx_index": fi,
            "why": (f"'{t.get('name')}': slow cutoff journey landed "
                    f"(1.8k -> 6.5k -> 3.2k -> 8.5k over bars "
                    f"{a:.0f}-{b:.0f}) — the archetype breathes; "
                    "reshape it, never re-freeze it")})
    return actions


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="MOVEMENT IS MANDATORY (w53)")
    ap.add_argument("song")
    ap.add_argument("--heal", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    v = court_movement(song)
    if a.heal and v["advisories"]:
        v["healed"] = heal_movement(song, v)
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps(v, indent=1))
