#!/usr/bin/env python3
"""Wave 48: THE WOBBLE (2026-07-12) — ledger dr29: "the wobble/growl bass —
the defining sound of the entire family — is a static drone." The truth was
a taste bug: wobble.dsp (built-in LFO, rate/base/depth/res zones) existed
while dubstep shipped on STATIC reese. The voice takes the lane it was
named for; the sync law in loop_gen locks its LFO to the take's tempo.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = "curated:claude/2026-07-12 (wave48 wobble: the LFO voice takes the dubstep lane; ledger dr29)"

if __name__ == "__main__":
    kg = KG()
    rows = kg.q("MATCH (g:Genre {name:'dubstep'})-[:CHARACTERIZED_BY]->"
                "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
    pid, grid = rows[0]
    d = json.loads(grid)
    d["bass_voice"] = "wobble"
    d["wobble_cpb"] = 2.0          # the classic 1/8 wobble
    kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
         f"SET p.grid = '{esc(json.dumps(d))}', "
         f"p.provenance = p.provenance + ' | {esc(PROV)}'")
    print("wave48: dubstep bass -> wobble (LFO voice, tempo-synced 1/8)")
