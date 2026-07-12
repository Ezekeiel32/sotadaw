#!/usr/bin/env python3
"""Wave 50: THE CHOP TAKE (2026-07-12) — ledger dr23 (CRIT): "chopped-break
variation rate ~0: the break backbone repeats identically every bar." The
breaks family's snare IS the chop surface — it re-chops per bar (shift/
stutter-double/drop, seeded, bounded) while the 2&4 backbeat anchors stay
sacred. Opt-in per genre via the grid's chop_lanes field.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = "curated:claude/2026-07-12 (wave50 chop take: breaks-family snare re-chops; ledger dr23)"
GENRES = ("dnb", "jungle", "breakcore", "breaks", "breakbeat_hardcore", "big_beat")

if __name__ == "__main__":
    kg = KG()
    done = []
    for g in GENRES:
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(g)}'}})-[:CHARACTERIZED_BY]->"
                    "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
        if not rows:
            continue
        pid, grid = rows[0]
        d = json.loads(grid)
        d["chop_lanes"] = ["snare"]
        kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
             f"SET p.grid = '{esc(json.dumps(d))}', "
             f"p.provenance = p.provenance + ' | {esc(PROV)}'")
        done.append(g)
    print(f"wave50: chop_lanes on {done}")
