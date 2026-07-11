#!/usr/bin/env python3
"""INTENSIFY — shape a section's ENERGY up or down ('make the drop harder').

  intensify.py <song> <section> <amount> [--write]   # amount -1..+1

The energy_contour verb (KG technique seeded firing 86): energy = velocity +
density. amount>0 hardens (louder hits + more 16th subdivisions on hats/perc);
amount<0 softens (quieter + thinned offbeats). ONLY the named section changes;
everything else is byte-identical. Locked tracks untouched. Composes surgical ops
at the section level so 'make the drop harder' is one call, not five.
"""
import argparse, copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import is_drum_track
import songname


def _section_span(song, name):
    secs = sorted(song.get("sections", []), key=lambda s: float(s["startBar"]))
    for i, s in enumerate(secs):
        if str(s.get("name", "")).lower() == name.lower():
            lo = float(s["startBar"])
            hi = float(secs[i + 1]["startBar"]) if i + 1 < len(secs) else float(song.get("lengthBars", lo + 4))
            return lo * 4.0, hi * 4.0
    return None


def intensify(song, section, amount):
    span = _section_span(song, section)
    if span is None:
        raise SystemExit(f"no section '{section}' (have: "
                         f"{[s.get('name') for s in song.get('sections', [])]})")
    a, b = span
    amount = max(-1.0, min(1.0, float(amount)))
    changed = {"section": section, "amount": amount, "tracks": {}}
    for t in song.get("tracks", []):
        if t.get("locked") or not t.get("notes"):
            continue
        win = [n for n in t["notes"] if a <= n["start"] < b]
        if not win:
            continue
        drum = is_drum_track(t)
        nm = str(t.get("name", "")).lower()
        is_hat = drum and any(k in nm for k in ("hat", "hi", "perc", "shaker", "ride"))
        n0 = len(win)
        # 1. velocity: harder -> toward 1.0, softer -> toward 0.3
        for n in win:
            v = float(n.get("vel", 0.8))
            target = 1.0 if amount > 0 else 0.3
            n["vel"] = round(min(1.0, max(0.06, v + (target - v) * abs(amount) * 0.5)), 3)
        # 2. density: harder hats -> add 16th subdivisions; softer -> thin offbeats
        added = removed = 0
        if is_hat and amount > 0.25:
            base = {round(n["start"] * 4) / 4.0 for n in win}   # existing 16th slots
            new = []
            for n in list(win):
                mid = round((n["start"] + 0.25) * 4) / 4.0       # the 16th after
                if a <= mid < b and mid not in base and mid not in {x["start"] for x in new}:
                    new.append(dict(n, start=mid, vel=round(n["vel"] * 0.6, 3)))
                    base.add(mid)
            # keep it musical: cap additions at the original count
            new = new[:max(1, int(n0 * abs(amount)))]
            t["notes"].extend(new); added = len(new)
        elif amount < -0.25:
            # thin: drop the softest offbeat notes in the window
            offs = sorted([n for n in win if abs((n["start"] % 1.0) - 0.5) < 0.13],
                          key=lambda n: n.get("vel", 0.8))
            drop = set(id(n) for n in offs[:int(len(offs) * abs(amount))])
            t["notes"] = [n for n in t["notes"] if id(n) not in drop]
            removed = len(drop)
        if added or removed or n0:
            changed["tracks"][t.get("name")] = {"notes": n0, "+16ths": added, "-thinned": removed}
    song.get("tracks") and [t["notes"].sort(key=lambda n: n["start"]) for t in song["tracks"] if t.get("notes")]
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("section"); ap.add_argument("amount", type=float)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    rep = intensify(song, a.section, a.amount)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
    verb = "harder" if a.amount > 0 else "softer"
    print(f"[intensify] '{a.section}' {verb} ({a.amount:+.1f}): "
          + ", ".join(f"{k}({v['notes']}n +{v['+16ths']}/-{v['-thinned']})" for k, v in rep["tracks"].items()))
    print("INTENSIFY_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
