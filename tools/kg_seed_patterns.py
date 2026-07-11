#!/usr/bin/env python3
"""PATTERN DNA (2026-07-03): machine-readable grids for all 29 PatternArchetypes —
the knowledge layer of THE LOOP GENERATOR. Each grid: 16th-note step indices
(0-15 per bar; 2-bar patterns use 0-31), optional per-step velocity maps, a
bass_style, and swing. Curated per genre (the prose descs were already there;
this makes them executable). Idempotent (MERGE sets the grid property)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

# lanes: kick / snare / clap / rim / hat / openhat / ride / ghost (low-vel snare)
# bass_style: offbeat | roots | sliding | psy_rolling | sustained | log | none
G = {
 "trap_drums":    {"bars": 2, "swing": 0.5, "bass_style": "sliding",
                   "kick": [0, 7, 10, 16, 21, 26], "snare": [8, 24], "ghost": [15, 30],
                   "hat": list(range(0, 32, 2)) + [11, 27],
                   "vel": {"hat": {"11": 0.4, "27": 0.4}}},
 "drill_drums":   {"bars": 2, "swing": 0.5, "bass_style": "sliding",
                   "kick": [0, 6, 11, 16, 22, 25], "snare": [8, 24], "ghost": [15, 17],
                   "hat": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]},
 "boombap_drums": {"bars": 1, "swing": 0.58, "bass_style": "roots",
                   "kick": [0, 10], "snare": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14]},
 "house_grid":    {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12], "clap": [4, 12], "openhat": [2, 6, 10, 14],
                   "hat": [1, 3, 5, 7, 9, 11, 13, 15]},
 "techno_grid":   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12], "clap": [4, 12],
                   "hat": list(range(16)), "vel": {"hat": {"0": 0.5, "4": 0.5, "8": 0.5, "12": 0.5}}},
 "dnb_break":     {"bars": 1, "swing": 0.5, "bass_style": "sustained",
                   "kick": [0, 10], "snare": [4, 12], "ride": [0, 2, 4, 6, 8, 10, 12, 14],
                   "ghost": [7, 15]},
 "jungle_break":  {"bars": 2, "swing": 0.5, "bass_style": "sustained",
                   "kick": [0, 10, 16, 26], "snare": [4, 12, 20, 23, 28], "ghost": [7, 15, 18, 31],
                   "ride": list(range(0, 32, 2))},
 "ukg_2step":     {"bars": 1, "swing": 0.6, "bass_style": "offbeat",
                   "kick": [0, 10], "snare": [4, 12], "hat": [2, 6, 8, 14], "ghost": [7, 15]},
 "ama_pocket":    {"bars": 1, "swing": 0.52, "bass_style": "log",
                   "kick": [0, 6, 12], "hat": list(range(16)),
                   "vel": {"hat": {str(i): (0.38 if i % 2 == 0 else 0.3) for i in range(16)}}},
 "afro_pocket":   {"bars": 1, "swing": 0.54, "bass_style": "roots",
                   "kick": [0, 3, 8, 11], "rim": [4, 12], "hat": list(range(0, 16, 2)),
                   "ghost": [14]},
 "dembow_grid":   {"bars": 1, "swing": 0.5, "bass_style": "roots",
                   "kick": [0, 4, 8, 12], "rim": [3, 11], "snare": [7, 15],
                   "hat": [0, 2, 4, 6, 8, 10, 12, 14]},
 "phonk_drums":   {"bars": 2, "swing": 0.5, "bass_style": "sliding",
                   "kick": [0, 7, 10, 16, 23, 26], "snare": [8, 24],
                   "ride": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
                   "ghost": [13, 29]},
 "drift_pocket":  {"bars": 1, "swing": 0.5, "bass_style": "sliding",
                   "kick": [0, 7, 10], "snare": [8],
                   "ride": [0, 2, 4, 6, 8, 10, 12, 14]},
 "lofi_pocket":   {"bars": 1, "swing": 0.56, "bass_style": "roots",
                   "kick": [0, 9], "snare": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14],
                   "vel": {"hat": {str(i): 0.35 for i in range(0, 16, 2)}}},
 "hyper_burst":   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12, 14, 15], "clap": [4, 12], "hat": list(range(0, 16, 2))},
 "jersey_kicks":  {"bars": 1, "swing": 0.5, "bass_style": "roots",
                   "kick": [0, 3, 6, 8, 11], "clap": [4, 12], "hat": [2, 10, 14]},
 "footwork_cells": {"bars": 2, "swing": 0.5, "bass_style": "roots",
                   "kick": [0, 5, 10, 16, 21, 26], "snare": [12, 28], "ghost": [14, 30],
                   "hat": [0, 4, 8, 12, 16, 20, 24, 28]},
 "gqom_dark":     {"bars": 2, "swing": 0.5, "bass_style": "log",
                   "kick": [0, 6, 8, 16, 22, 24], "ghost": [13, 29],
                   "hat": [2, 10, 18, 26]},
 "cumbia_roll":   {"bars": 1, "swing": 0.5, "bass_style": "roots",
                   "kick": [0, 8], "snare": [4, 12], "ghost": [14, 15],
                   "hat": list(range(16)),
                   "vel": {"hat": {str(i): (0.5 if i % 4 == 0 else 0.3) for i in range(16)}}},
 "bossa_sway":    {"bars": 2, "swing": 0.5, "bass_style": "roots",
                   "kick": [0, 8, 16, 24], "rim": [0, 6, 12, 20, 24],
                   "hat": list(range(0, 32, 2))},
 "moomba_pocket": {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12], "snare": [3, 7, 11, 15], "openhat": [2, 10]},
 "psy_fullon":    {"bars": 1, "swing": 0.5, "bass_style": "psy_rolling",
                   "kick": [0, 4, 8, 12], "openhat": [2, 6, 10, 14],
                   "hat": [1, 3, 5, 7, 9, 11, 13, 15]},
 "goa_layers":    {"bars": 1, "swing": 0.5, "bass_style": "psy_rolling",
                   "kick": [0, 4, 8, 12], "openhat": [2, 6, 10, 14], "hat": list(range(16))},
 "trance_lift":   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12], "clap": [4, 12], "openhat": [2, 6, 10, 14]},
 "hard_pocket":   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 4, 8, 12], "snare": [4, 12], "hat": [2, 6, 10, 14]},
 "synthwave_grid": {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
                   "kick": [0, 8], "snare": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14]},
 "dub_halftime":  {"bars": 2, "swing": 0.5, "bass_style": "sustained",
                   "kick": [0, 16, 22], "snare": [8, 24], "hat": [2, 6, 10, 14, 18, 26, 30],
                   "ghost": [15, 31]},
 "breakcore_chaos": {"bars": 2, "swing": 0.5, "bass_style": "sustained",
                   "kick": [0, 10, 16, 22, 27], "snare": [4, 7, 12, 18, 20, 25, 29, 31],
                   "ride": list(range(0, 32, 2))},
 "ambient_flow":  {"bars": 2, "swing": 0.5, "bass_style": "sustained",
                   "kick": [0], "hat": [8, 24], "vel": {"hat": {"8": 0.2, "24": 0.2}}},
}

def seed():
    kg = KG()
    prov_suffix = " + grid:curated:claude/2026-07-03 (machine-readable loop DNA)"
    n = 0
    for name, grid in G.items():
        cur = kg.q(f"MATCH (p:PatternArchetype {{name: '{name}'}}) RETURN p.provenance")
        if not cur:
            print(f"  SKIP {name}: no such archetype")
            continue
        prov = (cur[0][0] or "") if cur[0] else ""
        if "grid:curated" not in prov:
            prov = prov + prov_suffix
        kg.upsert("PatternArchetype", name, prov, grid=json.dumps(grid))
        n += 1
    print(f"pattern DNA: {n}/29 archetypes now carry executable grids")

if __name__ == "__main__":
    seed()
