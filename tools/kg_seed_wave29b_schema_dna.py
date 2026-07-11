#!/usr/bin/env python3
"""Wave 29b: SCHEMAS BECOME PLAYABLE DNA — wave 29's vocabulary lands as chord
grids on the four chordless archetypes of schema-linked genres, so loop_gen
actually PLAYS the OMT2 progressions (wave 26 format: chords=[[bar,degree]]).

  rnb_snap        <- doo-wop I-vi-IV-V          [[0,1],[1,6],[2,4],[3,5]]
  indie_loose     <- singer/songwriter vi-IV-I-V [[0,6],[1,4],[2,1],[3,5]]
  kpop_hybrid     <- hopscotch IV-V-vi-I         [[0,4],[1,5],[2,6],[3,1]]
  futurebass_half <- hopscotch IV-V-vi-I         [[0,4],[1,5],[2,6],[3,1]]

Only patches archetypes whose grid LACKS chords (wave-26 assignments stay
untouched); provenance appended, wave-29 chapter citation carried.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("OMT2 'Four-Chord Schemas' degrees -> archetype chord DNA via "
        "curated:claude/2026-07-05 (wave29b)")

ASSIGN = {
    "rnb_snap":        ("doo_wop_schema",           [[0, 1], [1, 6], [2, 4], [3, 5]]),
    "indie_loose":     ("singer_songwriter_schema", [[0, 6], [1, 4], [2, 1], [3, 5]]),
    "kpop_hybrid":     ("hopscotch_schema",         [[0, 4], [1, 5], [2, 6], [3, 1]]),
    "futurebass_half": ("hopscotch_schema",         [[0, 4], [1, 5], [2, 6], [3, 1]]),
}

if __name__ == "__main__":
    kg = KG()
    patched, skipped = 0, []
    for arch, (schema, chords) in ASSIGN.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{arch}'}}) RETURN p.grid")
        if not rows:
            skipped.append(f"{arch} (absent)")
            continue
        try:
            grid = json.loads(rows[0][0]) if rows[0][0] else {}
        except Exception:
            grid = {}
        if grid.get("chords"):
            skipped.append(f"{arch} (already has chords — untouched)")
            continue
        grid["chords"] = chords
        grid["chords_schema"] = schema
        kg.upsert("PatternArchetype", arch, PROV, grid=json.dumps(grid))
        patched += 1
    print(f"wave29b schema DNA: {patched} archetypes given playable chords"
          + (f"; skipped: {skipped}" if skipped else ""))
