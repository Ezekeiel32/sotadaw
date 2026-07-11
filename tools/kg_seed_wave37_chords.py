#!/usr/bin/env python3
"""Wave 37: CHORD DNA — the hip-hop/bass/club family (f147).

Canon grounding (own search, stamp f147): drill = i-VI (Cm->Ab the cited pair),
dark-trap i-VI-iv-V, 2-3 looping chords; riddim/dembow = two-chord minor
shuttles; filtered/club/neuro lanes = STATIC by form (vamp law, not laziness).
Idempotent; wave25 grammar ([[bar, 1-based degree]] in genre mode).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147)"

C = {
    "drill_drums":      [[0, 1], [2, 6]],
    "sexydrill_bounce": [[0, 1], [1, 6], [2, 4], [3, 5]],
    "memphis_knock":    [[0, 1], [2, 4]],
    "crunk_menace":     [[0, 1], [2, 6]],
    "triggerman_lean":  [[0, 1], [2, 7]],
    "hiphop_break":     [[0, 1], [2, 4]],
    "grime_cross":      [[0, 1], [2, 6]],
    "jungle_break":     [[0, 1], [2, 4]],
    "dancehall_riddim": [[0, 1], [2, 7]],
    "moomba_pocket":    [[0, 1], [1, 6], [2, 7], [3, 6]],
    "drift_pocket":     [[0, 1], [2, 4]],
    "witch_halftime":   [[0, 1], [2, 4]],
    "chicago_jack":     [[0, 1], [2, 7]],
    "deep_shuffle":     [[0, 1], [2, 4]],
    "detroit_pulse":    [[0, 1], [2, 6]],
    "speedgarage_4x4":  [[0, 1], [2, 4]],
    "bassline_niche":   [[0, 1], [2, 4]],
    # static-by-form (vamp law): filtered disco loops, chopped club cells, neuro riffs
    "frenchhouse_pump": [[0, 1]],
    "reese_carrier":    [[0, 1]],
    "footwork_cells":   [[0, 1]],
    "ghetto_twitch":    [[0, 1]],
    "techhouse_roll":   [[0, 1]],
}

if __name__ == "__main__":
    kg = KG()
    done = skip = miss = 0
    for pname, prog in C.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {pname}: MISSING"); miss += 1; continue
        grid = json.loads(rows[0][0])
        if "chords" in grid:
            skip += 1; continue
        grid["chords"] = prog
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
    print(f"wave37: {done} seeded, {skip} already had, {miss} missing")
