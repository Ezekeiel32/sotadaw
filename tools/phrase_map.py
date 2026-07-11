#!/usr/bin/env python3
"""THE PHRASE MAP (W123) — the mechanical half of lyric writing.

Lyrics are one word per melody note ({beat, text}); the hard part is
knowing EXACTLY how many words fit where. This prints, per section, the
note count and phrase shape (gaps > ~0.9 beat = phrase breaks) of a
melody track — the map W97/W112's lyrics were hand-counted against.

  phrase_map.py <song> [track]        # human table
  phrase_map.py <song> [track] --json # machine (write_lyrics feeds on it)

Repeated sections report a SHARED shape when identical (the hook sings
the same words every chorus — that sameness is the song).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def phrase_map(song, track_name="lead", gap=0.9):
    tr = next((t for t in song.get("tracks", [])
               if t.get("name") == track_name and t.get("notes")), None)
    if tr is None:
        return None
    notes = sorted(tr["notes"], key=lambda n: n["start"])
    secs = song.get("sections") or [{"name": "all", "startBar": 0}]
    bars = float(song.get("lengthBars", 0) or 0)
    out = []
    for i, x in enumerate(secs):
        b1 = secs[i + 1]["startBar"] if i + 1 < len(secs) else bars
        a, b = x["startBar"] * 4.0, b1 * 4.0
        ns = [n for n in notes if a <= n["start"] < b]
        if not ns:
            continue
        phr, cur = [], 1
        for p, q in zip(ns, ns[1:]):
            if q["start"] - (p["start"] + p.get("len", 0.5)) > gap:
                phr.append(cur)
                cur = 0
            cur += 1
        phr.append(cur)
        out.append({"section": x["name"], "startBeat": a, "notes": len(ns),
                    "phrases": phr,
                    "beats": [round(n["start"], 4) for n in ns]})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    try:
        from songname import resolve as _resolve  # the song-name law
        name = _resolve(args[0])
    except Exception:
        name = args[0]
    path = os.path.join(ROOT, "songs", f"{name}.json")
    if not os.path.exists(path):
        path = os.path.join(ROOT, "songs", f"{args[0]}.json")
    song = json.load(open(path))
    track = args[1] if len(args) > 1 else "lead"
    m = phrase_map(song, track)
    if m is None:
        print(f"no melody notes on '{track}'")
        return 1
    if "--json" in sys.argv:
        print(json.dumps(m, indent=1))
        return 0
    total = sum(x["notes"] for x in m)
    print(f"PHRASE MAP — '{track}' ({total} words needed total; one per note)")
    shapes = {}
    for x in m:
        key = tuple(x["phrases"])
        shapes.setdefault(key, []).append(x["section"])
        print(f"  {x['section']:12s} {x['notes']:3d} words  phrases {x['phrases']}")
    rep = [(list(k), v) for k, v in shapes.items() if len(v) > 1]
    for shape, names in rep:
        print(f"  SHARED SHAPE {shape}: {', '.join(names)} — the hook sings "
              "the SAME words on each (that sameness is the song)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
