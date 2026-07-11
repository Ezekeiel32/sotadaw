#!/usr/bin/env python3
"""R7 TIME MACHINE — the song's history as data (the drawer's feed + the
agent's twin).

Every accept is already a git commit and every crashed take already leaves a
journal crumb; this merges both into ONE ordered timeline and can resurrect
any point as a PROPOSAL (never in-place — the proposal law: the base song
changes only on user accept).

  timeline.py list <song> [--limit N] [--json]
  timeline.py restore <song> <ref>      ref = commit hash | journal filename
      -> writes songs/_prop_<song>.json (+ .ghost.json) from that state

The listing is newest-first: [{when, kind: accept|take, ref, msg, tracks,
bars}]. `restore` is byte-faithful to the historical json.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout


def _song_stats(text):
    try:
        d = json.loads(text)
        return len(d.get("tracks", [])), d.get("lengthBars")
    except Exception:
        return None, None


def timeline(song, limit=40):
    rel = f"songs/{song}.json"
    rows = []
    log = _git("log", "--follow", "--format=%H\t%ct\t%s", "--", rel)
    for line in log.splitlines()[:limit]:
        h, ct, msg = line.split("\t", 2)
        rows.append({"when": int(ct), "kind": "accept", "ref": h[:12],
                     "msg": msg})
    jdir = os.path.join(ROOT, "songs", ".journal")
    if os.path.isdir(jdir):
        takes = []
        for f in os.listdir(jdir):
            # crumbs are <song>-<epoch_ms>.json
            if f.startswith(song + "-") and f.endswith(".json"):
                stamp = f[len(song) + 1:-5]
                if stamp.isdigit():
                    takes.append((int(stamp) // 1000, f))
        # the journal writes a crumb per edit tick — a working minute leaves
        # dozens seconds apart. One chip per minute (the latest), or the
        # drawer is all crumbs and no story.
        takes.sort()
        by_min = {}
        for when, f in takes:
            by_min[when // 60] = (when, f)
        for when, f in by_min.values():
            rows.append({"when": when, "kind": "take", "ref": f,
                         "msg": "journal take (crash net)"})
    rows.sort(key=lambda r: -r["when"])
    rows = rows[:limit]
    for r in rows:                                   # enrich with cheap stats
        text = _load(song, r)
        if text:
            r["tracks"], r["bars"] = _song_stats(text)
    return rows


def _load(song, row):
    if row["kind"] == "accept":
        out = subprocess.run(["git", "show", f"{row['ref']}:songs/{song}.json"],
                             cwd=ROOT, capture_output=True, text=True)
        return out.stdout if out.returncode == 0 else None
    p = os.path.join(ROOT, "songs", ".journal", row["ref"])
    return open(p).read() if os.path.exists(p) else None


def restore(song, ref):
    rows = timeline(song, limit=200)
    row = next((r for r in rows if r["ref"].startswith(ref) or r["ref"] == ref),
               None)
    if row is None:
        return f"no timeline entry '{ref}' for {song} " \
               f"(refs: {[r['ref'] for r in rows[:8]]})"
    text = _load(song, row)
    if not text:
        return f"could not load {row['ref']}"
    prop = os.path.join(ROOT, "songs", f"_prop_{song}.json")
    open(prop, "w").write(text)
    # the ghost copy lets the lanes stream the diff immediately on pickup
    open(prop.replace(".json", ".ghost.json"), "w").write(text)
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(row["when"]))
    return (f"PROPOSAL from {row['kind']} {row['ref']} ({when}) -> "
            f"songs/_prop_{song}.json — audition/accept in the deck; the base "
            f"is untouched until accept")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    cmd, song = sys.argv[1], sys.argv[2]
    if cmd == "list":
        rows = timeline(song, limit=int(next(
            (sys.argv[i + 1] for i, a in enumerate(sys.argv)
             if a == "--limit"), 40)))
        if "--json" in sys.argv:
            print(json.dumps(rows))
        else:
            for r in rows:
                when = time.strftime("%m-%d %H:%M", time.localtime(r["when"]))
                stats = (f"{r.get('tracks')}tr/{r.get('bars')}bars"
                         if r.get("tracks") is not None else "?")
                print(f"{when}  {r['kind']:6s} {r['ref']:<14} {stats:>12}  "
                      f"{r['msg'][:60]}")
        return 0
    if cmd == "restore" and len(sys.argv) >= 4:
        print(restore(song, sys.argv[3]))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
