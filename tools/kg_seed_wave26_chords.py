#!/usr/bin/env python3
"""Wave 26: chord DNA for twelve more — harmony spreads (24 genres with changes).

Trance's uplifting i-VI-VII loop, dnb's dark two-chord, dubstep's i-VI heave,
ambient's slow i-IV breath, boombap's ii-V jazz loop, amapiano's i-VII-VI walk,
dembow's i-VI-VII-VI, phonk's static-then-VI, synthpop's I-V-vi-IV (the
axis!), italo's i-III-VII-VI, citypop's IVmaj-V-iii-vi (the toshiki loop!),
lofi's ii-V-I-IV drift.
Provenance: curated:claude/2026-07-04 (wave26 chord DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave26 chord DNA)"

CHORDS = {
    "trance_lift": [[0, 1], [1, 6], [2, 7], [3, 7]],
    "dnb_break": [[0, 1], [2, 6]],
    "dub_halftime": [[0, 1], [2, 6]],
    "ambient_flow": [[0, 1], [2, 4]],
    "boombap_drums": [[0, 2], [1, 5], [2, 1], [3, 1]],
    "ama_pocket": [[0, 1], [1, 7], [2, 6], [3, 7]],
    "dembow_grid": [[0, 1], [1, 6], [2, 7], [3, 6]],
    "phonk_drums": [[0, 1], [2, 6]],
    "synthpop_four": [[0, 1], [1, 5], [2, 6], [3, 4]],   # the axis progression
    "italo_gallop": [[0, 1], [1, 3], [2, 7], [3, 6]],
    "citypop_gloss": [[0, 4], [1, 5], [2, 3], [3, 6]],   # the toshiki loop
    "lofi_pocket": [[0, 2], [1, 5], [2, 1], [3, 4]],
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
        print(f"  {pname:16} {prog}")
    print(f"wave26: {done} progressions")
