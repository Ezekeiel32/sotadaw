#!/usr/bin/env python3
"""Wave 24: leads + fills — the world/roots twelve (36 genres speak full sentences).

Reggae's skank organ bubble, dancehall's dark pluck riddim, afrobeats' log-ish
kalimba line, bossa's nylon melody (pluck), soul's rhodes phrase, gospel's
organ runs, ska's brass-stab offbeat hook, salsa's montuno cell (rhodes as
piano), merengue's accordion gallop, bachata's requinto pluck, country's
telecaster-ish pluck line, blues' call-phrase (guitar_grit).
Provenance: curated:claude/2026-07-04 (wave24 leads+fills; voices vs instruments/).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave24 leads+fills — world/roots)"

WAVE = {
    "reggae": ("reggae_onedrop",
        {"voice": "organ_soul", "octave": 5, "steps": [[2, 1, 1], [6, 3, 1], [10, 1, 1], [14, 5, 1]]},
        {"kick": [8], "snare": [8, 12, 14], "hat": [0, 2, 4, 6, 8, 10],
         "vel": {"snare": {"12": 0.5, "14": 0.7}}}),
    "dancehall": ("dancehall_riddim",
        {"voice": "pluck2", "octave": 5, "steps": [[0, 1, 1], [3, 1, 1], [6, 4, 1], [10, 3, 1], [14, 5, 1]]},
        {"kick": [0, 3, 6, 10], "snare": [12, 13, 14, 15], "hat": [0, 4, 8],
         "vel": {"snare": {"12": 0.5, "13": 0.6, "14": 0.75, "15": 0.9}}}),
    "afrobeats": ("afro_pocket",
        {"voice": "kalimba", "octave": 5, "steps": [[0, 1, 1], [3, 5, 1], [6, 4, 1], [8, 3, 1], [11, 5, 1], [14, 4, 1]]},
        {"kick": [0, 3, 8, 11], "snare": [4, 12, 14], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"14": 0.7}}}),
    "bossanova": ("bossa_sway",
        {"voice": "pluck", "octave": 5, "steps": [[0, 3, 2], [4, 5, 1], [7, 4, 2], [11, 1, 2], [14, 2, 1]]},
        {"kick": [0, 8], "snare": [4, 10, 14], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"10": 0.4, "14": 0.5}}}),
    "soul": ("soul_pocket",
        {"voice": "rhodes", "octave": 5, "steps": [[0, 1, 2], [4, 3, 1], [6, 5, 2], [12, 4, 3]]},
        {"kick": [0, 6, 8], "snare": [4, 11, 12, 14], "hat": [0, 2, 4, 6, 8, 10],
         "vel": {"snare": {"11": 0.4, "14": 0.85}}}),
    "gospel": ("gospel_shout",
        {"voice": "organ_soul", "octave": 5, "steps": [[0, 1, 1], [2, 2, 1], [4, 3, 1], [6, 4, 1], [8, 5, 2], [12, 8, 3]]},
        {"kick": [0, 4, 8, 12], "snare": [4, 10, 12, 14, 15], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"10": 0.5, "14": 0.85, "15": 1.0}}}),
    "ska": ("skank_accents",
        {"voice": "brass_stab", "octave": 4, "steps": [[2, 1, 1], [6, 1, 1], [10, 5, 1], [14, 5, 1]]},
        {"kick": [0, 8], "snare": [4, 12, 14, 15], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"14": 0.7, "15": 0.85}}}),
    "salsa": ("tumbao_cascara",
        {"voice": "rhodes", "octave": 5, "steps": [[0, 1, 1], [3, 3, 1], [6, 5, 1], [8, 8, 1], [11, 5, 1], [14, 3, 1]]},
        {"kick": [7, 15], "snare": [4, 6, 10, 12, 14], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"6": 0.5, "10": 0.6, "14": 0.8}}}),
    "merengue": ("tambora_gallop",
        {"voice": "accordion", "octave": 5, "steps": [[0, 1, 1], [2, 3, 1], [4, 5, 1], [6, 3, 1], [8, 1, 1], [10, 4, 1], [12, 5, 1], [14, 4, 1]]},
        {"kick": [0, 4, 8, 12], "snare": [2, 5, 6, 7, 10, 13, 14, 15], "hat": [0, 4, 8, 12],
         "vel": {"snare": {"7": 0.85, "15": 0.95, "2": 0.4, "5": 0.45}}}),
    "bachata": ("bachata_bongo",
        {"voice": "pluck", "octave": 5, "steps": [[0, 5, 1], [2, 4, 1], [4, 3, 1], [6, 2, 1], [8, 1, 2], [12, 5, 1], [14, 4, 1]]},
        {"kick": [0, 8], "snare": [4, 12, 14, 15], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"15": 1.0, "14": 0.7}}}),
    "country": ("train_beat",
        {"voice": "pluck", "octave": 5, "steps": [[0, 1, 1], [4, 3, 1], [6, 5, 1], [8, 6, 1], [10, 5, 1], [12, 1, 3]]},
        {"kick": [0, 8], "snare": [4, 10, 12, 14], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
         "vel": {"snare": {"10": 0.5, "14": 0.8}}}),
    "blues": ("blues_shuffle",
        {"voice": "guitar_grit", "octave": 4, "steps": [[0, 1, 2], [4, 4, 1], [6, 3, 1], [8, 1, 2], [12, 5, 2]]},
        {"kick": [0, 8], "snare": [4, 8, 10, 12, 14], "hat": [0, 2, 4, 6],
         "vel": {"snare": {"8": 0.5, "10": 0.6, "14": 0.9}}}),
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
    print(f"wave24: {done} genres deepened")
