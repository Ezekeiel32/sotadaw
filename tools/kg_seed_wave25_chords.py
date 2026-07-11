#!/usr/bin/env python3
"""Wave 25: CHORD DNA — progressions for 12 flagships (harmony moves at last).

Degrees are 1-based in the genre's mode. Funk and techno stay ONE-CHORD VAMPS
on purpose (that IS the genre); jazz gets ii-V-I-vi, gospel I-IV-I-V,
synthwave the i-VI-III-VII anthem, house i-VII-VI-VII, soul i-III-VI-VII.
Provenance: curated:claude/2026-07-04 (wave25 chord DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave25 chord DNA — the changes)"

CHORDS = {
    "house_grid": [[0, 1], [1, 7], [2, 6], [3, 7]],
    "trap_drums": [[0, 1], [2, 6]],
    "techno_grid": [[0, 1]],                      # the vamp IS techno
    "the_one_ghosts": [[0, 1]],                   # funk: ONE chord, by law
    "swing_ride_grid": [[0, 2], [1, 5], [2, 1], [3, 6]],   # ii-V-I-vi
    "gospel_shout": [[0, 1], [1, 4], [2, 1], [3, 5]],       # I-IV-I-V
    "soul_pocket": [[0, 1], [1, 3], [2, 6], [3, 7]],
    "synthwave_grid": [[0, 1], [1, 6], [2, 3], [3, 7]],     # the anthem
    "ukg_2step": [[0, 1], [1, 6], [2, 7], [3, 6]],
    "reggae_onedrop": [[0, 1], [2, 7]],
    "disco_four": [[0, 1], [1, 4], [2, 1], [3, 4]],
    "rock_backbeat": [[0, 1], [1, 6], [2, 7], [3, 1]],
}

if __name__ == "__main__":
    kg = KG()
    done = 0
    for pname, prog in CHORDS.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {pname}: MISSING"); continue
        grid = json.loads(rows[0][0])
        grid["chords"] = prog
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
        print(f"  {pname:18} chords {prog}")
    print(f"wave25: {done} progressions seeded")
