#!/usr/bin/env python3
"""Wave 23: leads + fills for twelve more (the electronic depth wave).

Synthwave's driving supersaw arp, dubstep's sparse bell over the wobble,
drill's dark piano slide, phonk's cowbell melody (fmbell), psytrance's 303
accents, hardstyle's anthem saw, footwork's vox stabs, gqom's dark keys,
lofi's jazzy rhodes, cumbia's ACCORDION line, hardwave's huge saw chords,
g-funk's high whistle. Each with its turnaround fill.
Provenance: curated:claude/2026-07-04 (wave23 leads+fills; voices checked vs instruments/).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave23 leads+fills)"

# genre -> (archetype, lead, fill)
WAVE = {
    "synthwave": ("synthwave_grid",
        {"voice": "supersaw_fat", "octave": 5, "steps": [[0, 1, 1], [2, 1, 1], [4, 5, 1], [6, 5, 1], [8, 3, 1], [10, 3, 1], [12, 4, 1], [14, 4, 1]]},
        {"kick": [0, 4, 8, 12], "snare": [8, 10, 12, 14, 15], "hat": [2, 6],
         "vel": {"snare": {"8": 0.5, "10": 0.6, "12": 0.75, "14": 0.9, "15": 1.0}}}),
    "dubstep": ("dub_halftime",
        {"voice": "fmbell", "octave": 5, "steps": [[0, 1, 2], [10, 4, 2]]},
        {"kick": [0, 6], "snare": [8, 11, 14], "hat": [0, 4, 10],
         "vel": {"snare": {"11": 0.6, "14": 0.8}}}),
    "drill": ("drill_drums",
        {"voice": "keys_dark", "octave": 5, "steps": [[0, 1, 2], [5, 3, 1], [8, 1, 2], [13, 2, 1]]},
        {"kick": [0, 8], "snare": [4, 10, 12, 14], "hat": [0, 2, 3, 5, 6, 8, 9, 11],
         "vel": {"snare": {"10": 0.5, "14": 0.9}}}),
    "phonk": ("phonk_drums",
        {"voice": "fmbell", "octave": 5, "steps": [[0, 1, 1], [3, 3, 1], [6, 4, 1], [8, 5, 1], [11, 4, 1], [14, 3, 1]]},
        {"kick": [0, 7], "snare": [4, 12, 13, 14, 15], "hat": [0, 2, 4, 6],
         "vel": {"snare": {"13": 0.6, "14": 0.8, "15": 1.0}}}),
    "psytrance": ("psy_fullon",
        {"voice": "acid303", "octave": 4, "steps": [[2, 1, 1], [6, 1, 1], [10, 8, 1], [14, 1, 1]]},
        {"kick": [0, 4, 8, 12], "snare": [8, 10, 12, 13, 14, 15], "hat": [2, 6],
         "vel": {"snare": {"8": 0.4, "10": 0.5, "12": 0.65, "13": 0.75, "14": 0.85, "15": 1.0}}}),
    "hardstyle": ("hard_pocket",
        {"voice": "supersaw", "octave": 5, "steps": [[0, 1, 2], [8, 5, 2], [12, 4, 2]]},
        {"kick": [0, 2, 4, 6, 8, 10, 12, 14], "snare": [14], "hat": [],
         "vel": {"kick": {str(i): 0.9 for i in range(0, 16, 2)}, "snare": {"14": 1.0}}}),
    "footwork": ("footwork_cells",
        {"voice": "vox_pad", "octave": 5, "steps": [[0, 1, 1], [5, 5, 1], [10, 3, 1]]},
        {"kick": [0, 3, 6, 10, 13], "snare": [12, 13, 14, 15], "hat": [0, 4, 8],
         "vel": {"snare": {"12": 0.5, "13": 0.6, "14": 0.75, "15": 0.9}}}),
    "gqom": ("gqom_dark",
        {"voice": "keys_dark", "octave": 4, "steps": [[0, 1, 2], [11, 4, 2]]},
        {"kick": [0, 3, 8, 10, 12, 14], "snare": [], "hat": [2, 6, 10],
         "vel": {"kick": {"12": 0.85, "14": 0.95}}}),
    "lofi": ("lofi_pocket",
        {"voice": "rhodes", "octave": 5, "steps": [[0, 3, 2], [4, 5, 1], [7, 4, 2], [12, 1, 3]]},
        {"kick": [0, 7, 10], "snare": [4, 14], "hat": [0, 2, 4, 6, 8, 10],
         "vel": {"snare": {"14": 0.55}}}),
    "cumbia": ("cumbia_roll",
        {"voice": "accordion", "octave": 5, "steps": [[0, 1, 1], [2, 3, 1], [4, 5, 2], [8, 4, 1], [10, 3, 1], [12, 1, 2]]},
        {"kick": [0, 8], "snare": [4, 10, 12, 14], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"10": 0.5, "14": 0.8}}}),
    "hardwave": ("hardwave_halftime",
        {"voice": "supersaw_fat", "octave": 4, "steps": [[0, 1, 4], [8, 6, 4]]},
        {"kick": [0, 10], "snare": [8, 12, 14], "hat": [0, 4],
         "vel": {"snare": {"12": 0.7, "14": 0.9}}}),
    "gfunk": ("gfunk_bounce",
        {"voice": "pluck2", "octave": 6, "steps": [[0, 5, 2], [6, 4, 1], [8, 3, 2], [14, 5, 1]]},
        {"kick": [0, 7], "snare": [4, 12, 14], "hat": [0, 2, 4, 6, 8, 10],
         "vel": {"snare": {"14": 0.7}}}),
}

if __name__ == "__main__":
    kg = KG()
    done = 0
    for genre, (pname, lead, fill) in WAVE.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {genre}: {pname} MISSING — skipped")
            continue
        grid = json.loads(rows[0][0])
        grid["lead"] = lead
        grid["fill"] = fill
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
        print(f"  {genre:12} lead({lead['voice']}) + fill -> {pname}")
    print(f"wave23: {done} genres deepened")
