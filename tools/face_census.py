#!/usr/bin/env python3
"""FACE CENSUS — the face-doctrine guard (face-f5, 2026-07-06).

Every voice in instruments/ must expose >= MIN_ZONES tweakable zones beyond
freq/gain (gate is a button): a voice without hands has no face, no rack knobs,
no automatable params. The 24-voice enrichment campaign closed the census at
zero; this guard keeps it there. Exit 1 + the offender list on regression.

  tools/face_census.py            # check (CI-able)
  tools/face_census.py --list     # per-voice zone table
"""
import glob, re, sys

MIN_ZONES = 2
SKIP = {"master_limiter", "test_sine"}

def census():
    rows = []
    for f in sorted(glob.glob("instruments/*.dsp")):
        name = f.split("/")[-1][:-4]
        if name.startswith("fx_") or name in SKIP:
            continue
        zones = [z for z in re.findall(r'hslider\("([^"]+)"', open(f).read())
                 if z not in ("freq", "gain")]
        rows.append((name, zones))
    return rows

def main():
    rows = census()
    bad = [(n, z) for n, z in rows if len(z) < MIN_ZONES]
    if "--list" in sys.argv:
        for n, z in rows:
            print(f"{len(z):2d}  {n:16s} {', '.join(z)}")
        print(f"--- {len(rows)} voices")
    if bad:
        print(f"FACE CENSUS: {len(bad)} voice(s) below {MIN_ZONES} zones:")
        for n, z in bad:
            print(f"  {n}: {z or '(none)'}")
        return 1
    print(f"FACE CENSUS: ALL {len(rows)} VOICES HAVE HANDS (>= {MIN_ZONES} zones)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
