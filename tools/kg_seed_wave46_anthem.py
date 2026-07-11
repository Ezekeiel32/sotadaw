#!/usr/bin/env python3
"""Wave 46: THE ANTHEM WAVE (2026-07-12) — the LEAD FAMINE (worldclass ledger
crit dr03/dr25/dr29): melody-DEFINED genres birthed with zero topline. A
trance take without the supersaw anthem is not trance; metal without the riff
is a drum demo. Each cell below is the genre's signature RHYTHM skeleton in
[step16, scale_degree, len16] grammar — the hook engine (W14) supplies pitch
intent (anchors/climax/cadence) and the take-variation walk on top, and the
KEY law (dna_battery) holds every note diatonic.

  trance        dotted-8th anthem on 1-5-6 (the uplift cell), supersaw_fat
  prog_house    the sparser pulse anthem, supersaw
  eurodance     the octave piano-saw riff, supersaw
  future_bass   syncopated chord-top jumps (the vocal-chop contour), supersaw
  bigroom       festival octave stabs, supersaw_fat
  synthpop      the DX7 motif, ep_bright
  metal         the low riff (root-4-5 with b7 turn), highgain_guitar, oct 3
  punk          straight-8 power drive on 1-4-5, fuzz_guitar
  shoegaze      the washed whole-note line, clean_chime_guitar
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave46 anthem: lead famine — 9 melody-"
        "defined genres birthed hookless; ledger dr03/dr25/dr29)")

LEADS = {
    "trance": {"voice": "supersaw_fat", "octave": 5,
               "steps": [[0, 1, 3], [3, 5, 3], [6, 6, 3], [9, 5, 3], [12, 8, 2], [14, 5, 2]]},
    "progressive_house": {"voice": "supersaw", "octave": 5,
                          "steps": [[0, 3, 4], [6, 5, 2], [8, 6, 4], [14, 5, 2]]},
    "eurodance": {"voice": "supersaw", "octave": 5,
                  "steps": [[0, 8, 2], [2, 5, 2], [4, 6, 2], [6, 5, 2],
                            [8, 8, 2], [10, 5, 2], [12, 4, 2], [14, 5, 2]]},
    "future_bass": {"voice": "supersaw", "octave": 5,
                    "steps": [[0, 3, 2], [3, 5, 1], [4, 8, 4], [10, 6, 2], [12, 5, 4]]},
    "bigroom": {"voice": "supersaw_fat", "octave": 5,
                "steps": [[0, 1, 2], [4, 8, 2], [8, 1, 2], [12, 8, 2]]},
    "synthpop": {"voice": "ep_bright", "octave": 5,
                 "steps": [[0, 5, 2], [2, 3, 2], [4, 1, 4], [8, 5, 2], [10, 6, 2], [12, 5, 4]]},
    "metal": {"voice": "highgain_guitar", "octave": 3,
              "steps": [[0, 1, 2], [3, 1, 1], [4, 4, 2], [6, 1, 1],
                        [8, 5, 2], [11, 4, 1], [12, 1, 2], [14, 7, 1]]},
    "punk": {"voice": "fuzz_guitar", "octave": 4,
             "steps": [[0, 1, 2], [2, 1, 2], [4, 4, 2], [6, 4, 2],
                       [8, 5, 2], [10, 5, 2], [12, 4, 2], [14, 4, 2]]},
    "shoegaze": {"voice": "clean_chime_guitar", "octave": 5,
                 "steps": [[0, 5, 4], [4, 3, 4], [8, 4, 4], [12, 1, 4]]},
}

if __name__ == "__main__":
    kg = KG()
    done, miss = [], []
    for g, lead in LEADS.items():
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(g)}'}})-[:CHARACTERIZED_BY]->"
                    "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
        if not rows:
            miss.append(g)
            continue
        pid, grid = rows[0]
        d = json.loads(grid)
        if (d.get("lead") or {}).get("steps"):
            done.append(f"{g} (already has a hook — untouched)")
            continue
        d["lead"] = lead
        kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
             f"SET p.grid = '{esc(json.dumps(d))}', "
             f"p.provenance = p.provenance + ' | {esc(PROV)}'")
        done.append(f"{g}: {lead['voice']} oct{lead['octave']} x{len(lead['steps'])} steps")
    print(f"wave46: {len(done)} anthems\n  " + "\n  ".join(done)
          + (f"\n  MISSING: {miss}" if miss else ""))
