#!/usr/bin/env python3
"""Wave 17: the swing-grid migration — 13 grids had SILENT NO-OP swing.

The bug class (found by wave 16's blues probe): engine swing shifts odd
subdivisions of the SWING GRID; the default grid is 16th, but these patterns
place every hit on even 16ths (8th-note feels) — so their authored swing
(0.51-0.62!) never moved a single note. ukgarage at 0.6 rendered dead
straight; 2-step's entire identity is that shuffle.

Fix: swing_grid "8th" on all 13 (their offbeat 8ths — steps 2,6,10,14 —
become the shifted subdivisions, which is exactly the musical intent).
Idempotent: reads each grid, adds the field, re-upserts.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave17 swing-grid migration; bug class from wave16 blues probe)"

FLAGGED = ["boombap_drums", "ukg_2step", "reggae_onedrop", "afrohouse_organic",
           "threestep_cell", "speedgarage_4x4", "bassline_niche", "one_drop_dub",
           "swing_ride_grid", "acid_shuffle", "chicago_jack", "dubtech_pulse",
           "indie_loose"]

if __name__ == "__main__":
    kg = KG()
    fixed = 0
    for pname in FLAGGED:
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {pname}: MISSING — skipped")
            continue
        grid = json.loads(rows[0][0])
        if grid.get("swing_grid") == "8th":
            print(f"  {pname}: already 8th")
            continue
        grid["swing_grid"] = "8th"
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        fixed += 1
        print(f"  {pname}: swing {grid.get('swing')} now rides the 8th grid")
    print(f"wave17: {fixed} grids migrated")
