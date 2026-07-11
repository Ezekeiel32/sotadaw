#!/usr/bin/env python3
"""Wave 39: CHORD DNA — the last three (f150). 129/129.

Grounding (own search, f150): afro house = minor i-VII-VI-VII (the cited Am-G-F-G
tension-release canon; 3step shares the pool with more space); latin trap =
i-iv-VII-III (the cited La Noche de Anoche shape). Wave25 grammar; idempotent.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-06 (wave39 final three; afrohouse Am-G-F-G + reggaeton i-iv-VII-III cited f150)"

C = {
    "afrohouse_organic": [[0, 1], [1, 7], [2, 6], [3, 7]],
    "threestep_cell":    [[0, 1], [1, 7], [2, 6], [3, 7]],
    "latintrap_lilt":    [[0, 1], [1, 4], [2, 7], [3, 3]],
}

if __name__ == "__main__":
    kg = KG()
    for pname, prog in C.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        grid = json.loads(rows[0][0])
        if "chords" not in grid:
            grid["chords"] = prog
            kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
            print(f"  {pname}: {prog}")
    print("wave39: the map is FULL")
