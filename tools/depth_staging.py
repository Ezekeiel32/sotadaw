#!/usr/bin/env python3
"""DEPTH STAGING — wave 89 (r-7 item 255): front/back placement as
deterministic reverb + EQ physics. distance 0..1 per lane maps to:

  FRONT (0.0-0.3)  send <= -20dB, pre-delay 20-40ms (kept forward),
                   no HF damping, no level cut
  MID   (0.3-0.7)  interpolated
  BACK  (0.7-1.0)  send -14..-10dB, darker/longer verb, HF damped
                   (air absorption: fx_filter rolls the lane's highs),
                   -6dB per distance 'doubling', shorter pre-delay

THE ROOM LAW: jazz/folk/live share ONE room (one bus, roles at
different sends); pop/EDM get distinct spaces (front + back buses).
Everything static symbolic params — no automation, fully inspectable.

  stage_depth(song, placements, genre)   placements = {track: 0..1}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ONE_ROOM = ("jazz", "folk", "acoustic", "live", "bossa", "swing",
             "bigband", "blues", "country", "soul")


def depth_params(d):
    """The physics map for one lane at distance d (0..1)."""
    d = max(0.0, min(1.0, float(d)))
    send_db = -20.0 + d * 8.0                 # -20 (front) .. -12 (back)
    if d > 0.7:
        send_db = -12.0 + (d - 0.7) / 0.3 * 2.0   # .. -10 at the wall
    predelay_ms = 40.0 - d * 30.0             # 40 front .. 10 back
    level_cut_db = -6.0 * max(d - 0.3, 0.0) / 0.7 * 1.0  # 0 .. -6
    hf_cut = None
    if d >= 0.5:
        hf_cut = 12000.0 - (d - 0.5) / 0.5 * 7500.0   # 12k .. 4.5k
    return {"send_db": round(send_db, 1),
            "predelay_ms": round(predelay_ms, 1),
            "level_cut_db": round(level_cut_db, 2),
            "hf_cut": round(hf_cut, 0) if hf_cut else None}


def stage_depth(song, placements, genre=""):
    """Land the depth map: room bus(es) + sends + per-lane EQ/level.
    Hand work sacred: lanes with existing depth sends skip. Mutates;
    returns the ledger."""
    g = str(genre or "").lower()
    one_room = any(w in g for w in _ONE_ROOM)
    buses = song.setdefault("buses", [])
    sends = song.setdefault("sends", [])
    rooms = {}

    def ensure_room(name, decay, damp):
        if not any(b.get("name") == name for b in buses
                   if isinstance(b, dict)):
            buses.append({"name": name, "fx": [
                {"id": "fx_reverb", "params": {"decay": decay,
                                               "predelay": 20}}]})
        rooms[name] = True
        return name

    edits = []
    by_name = {t.get("name"): t for t in song.get("tracks", []) or []
               if isinstance(t, dict)}
    for track_name, d in (placements or {}).items():
        t = by_name.get(track_name)
        if t is None:
            continue
        if any(s.get("from") == track_name and
               str(s.get("to", "")).startswith("room_")
               for s in sends if isinstance(s, dict)):
            continue                          # hand work sacred
        p = depth_params(d)
        if one_room:
            room = ensure_room("room_shared", 1.6, 4500)
        elif float(d) >= 0.5:
            room = ensure_room("room_back", 2.4, 3500)
        else:
            room = ensure_room("room_front", 1.1, 8000)
        sends.append({"from": track_name, "to": room,
                      "gainDb": p["send_db"]})
        if p["level_cut_db"] < -0.5:
            t["gainDb"] = round(float(t.get("gainDb", 0) or 0)
                                + p["level_cut_db"], 2)
        if p["hf_cut"]:
            fx = t.setdefault("fx", [])
            if not any(str(f.get("id")) == "fx_filter" for f in fx):
                fx.append({"id": "fx_filter",
                           "params": {"cutoff": p["hf_cut"],
                                      "res": 0.7}})
        edits.append({"kind": "depth", "track": track_name,
                      "distance": float(d), "room": room, **p,
                      "why": (f"'{track_name}' at distance {d:.2f}: "
                              f"send {p['send_db']}dB to {room}"
                              + (f", highs rolled at {p['hf_cut']:.0f}Hz "
                                 "(air absorption)" if p["hf_cut"]
                                 else "")
                              + (f", level {p['level_cut_db']}dB"
                                 if p["level_cut_db"] < -0.5 else ""))})
    if edits:
        edits.append({"kind": "depth_staging",
                      "room_law": "one shared room" if one_room
                      else "distinct spaces",
                      "why": (f"{'jazz/live: one room, roles at '
                              'different sends' if one_room else
                              'pop/EDM: front and back are different '
                              'spaces'}")})
    return edits


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="DEPTH STAGING (w89)")
    ap.add_argument("song")
    ap.add_argument("--place", action="append", required=True,
                    metavar="track=0.8")
    ap.add_argument("--genre", default="")
    a = ap.parse_args()
    song = json.load(open(a.song))
    placements = {}
    for kv in a.place:
        k, v = kv.split("=")
        placements[k] = float(v)
    eds = stage_depth(song, placements, a.genre)
    if eds:
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps(eds, indent=1))
