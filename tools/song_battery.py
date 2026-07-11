#!/usr/bin/env python3
"""song_battery.py — the repo's songs as a regression net.

  song_battery.py [--filter NAME] [--clip-tolerance N]

Renders every committed song (songs/*.json, skipping _underscore scratch and
_prop_ proposals), asserts:
  PARSE    song loads
  RENDER   m1 ok=1 and the wav is non-trivial
  CLEAN    clipped samples <= tolerance (default 0)
Prints a scoreboard, exits nonzero on any failure — run after SongLoader/
engine/schema changes. The preset battery covers the vst3 rail; this covers
the SONGS.
"""
import argparse, glob, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")


def main(flt, tol):
    songs = []
    for p in sorted(glob.glob(os.path.join(ROOT, "songs", "*.json"))):
        b = os.path.basename(p)
        if b.startswith("_") or b.startswith("."):
            continue
        if flt and flt not in b:
            continue
        songs.append(p)
    wav = os.path.join(ROOT, "songs", "_battery_song.wav")
    fails = []
    for p in songs:
        name = os.path.basename(p)[:-5]
        try:
            json.load(open(p))
        except Exception as e:
            fails.append((name, f"PARSE: {e}"))
            print(f"  {name:28} PARSE FAIL")
            continue
        r = subprocess.run([M1, "render", p, wav], capture_output=True, text=True, timeout=600)
        if "ok=1" not in r.stdout + r.stderr or not os.path.exists(wav) or os.path.getsize(wav) < 50000:
            fails.append((name, "RENDER"))
            print(f"  {name:28} RENDER FAIL")
            continue
        try:
            a = json.loads(subprocess.run([PY, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                                          capture_output=True, text=True, timeout=180).stdout)
            cl = int(a.get("clipped_samples", 0))
        except Exception:
            cl = -1
        if cl > tol or cl < 0:
            fails.append((name, f"CLIP: {cl}"))
            print(f"  {name:28} ok render, CLIPPED {cl}")
        else:
            print(f"  {name:28} OK  (clip {cl})")
    if os.path.exists(wav):
        os.remove(wav)
    print(f"song battery: {len(songs) - len(fails)}/{len(songs)} clean"
          + (f" — FAILURES: {[f[0] for f in fails]}" if fails else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default=None)
    ap.add_argument("--clip-tolerance", type=int, default=0)
    a = ap.parse_args()
    main(a.filter, a.clip_tolerance)
