#!/usr/bin/env python3
"""PATTERN DNA WAVE 2 (2026-07-03): loop-generator coverage 29 -> 50 genres.
Creates PatternArchetype nodes WITH executable grids for the wave-6..11 genres
that never had one (reggae's one-drop, metal's chug, big band's swung ride,
the club economies, the current waves). Same lane conventions as
kg_seed_patterns.py. Idempotent (MERGE)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

# genre -> (archetype_name, desc, grid)
G2 = {
 "reggae": ("reggae_onedrop", "one drop: beat 1 EMPTY, kick+snare together on 3, hat 8ths",
   {"bars": 1, "swing": 0.52, "bass_style": "roots",
    "kick": [8], "snare": [8], "hat": [0, 2, 4, 6, 8, 10, 12, 14], "ghost": [14]}),
 "dancehall": ("dancehall_riddim", "3+3+2 riddim kicks under a beat-3 snare",
   {"bars": 1, "swing": 0.5, "bass_style": "roots",
    "kick": [0, 6, 12], "snare": [8], "hat": [0, 2, 4, 6, 8, 10, 12, 14], "rim": [3, 11]}),
 "metal": ("metal_chug", "8th-note chug kicks locked to guitars, backbeat, ride wash",
   {"bars": 1, "swing": 0.5, "bass_style": "sustained",
    "kick": [0, 2, 4, 6, 8, 10, 12, 14], "snare": [4, 12],
    "ride": [0, 2, 4, 6, 8, 10, 12, 14]}),
 "punk": ("punk_dbeat", "d-beat gallop, relentless 8th hats",
   {"bars": 1, "swing": 0.5, "bass_style": "roots",
    "kick": [0, 6, 8, 14], "snare": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
 "tech_house": ("techhouse_roll", "4-floor + rolling offbeat, shuffled 16ths",
   {"bars": 1, "swing": 0.54, "bass_style": "offbeat",
    "kick": [0, 4, 8, 12], "clap": [4, 12], "openhat": [2, 6, 10, 14],
    "hat": [1, 3, 5, 7, 9, 11, 13, 15]}),
 "afro_house": ("afrohouse_organic", "4-floor under organic rim/shaker conversation",
   {"bars": 2, "swing": 0.53, "bass_style": "offbeat",
    "kick": [0, 4, 8, 12, 16, 20, 24, 28], "rim": [3, 10, 19, 26, 30],
    "hat": list(range(0, 32, 2)), "ghost": [14, 30]}),
 "hard_techno": ("hardtechno_drive", "relentless 4-floor + industrial off-hats",
   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
    "kick": [0, 4, 8, 12], "openhat": [2, 6, 10, 14], "hat": list(range(16)),
    "vel": {"hat": {str(i): 0.35 for i in range(1, 16, 2)}}}),
 "future_bass": ("futurebass_half", "halftime bounce, roll into the 3",
   {"bars": 2, "swing": 0.5, "bass_style": "sustained",
    "kick": [0, 10, 16, 26], "snare": [8, 24], "hat": [0, 4, 6, 12, 14, 15, 16, 20, 22, 28, 30, 31]}),
 "eurodance": ("eurodance_stomp", "4-floor stomp, offbeat opens, clap 2&4",
   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
    "kick": [0, 4, 8, 12], "clap": [4, 12], "openhat": [2, 6, 10, 14]}),
 "hiphop": ("hiphop_break", "the looped break: kick 1 & the and-of-2, backbeat",
   {"bars": 1, "swing": 0.56, "bass_style": "roots",
    "kick": [0, 7, 10], "snare": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
 "rnb": ("rnb_snap", "halftime snap: space is the pocket",
   {"bars": 2, "swing": 0.52, "bass_style": "sliding",
    "kick": [0, 7, 20, 26], "snare": [8, 24], "hat": [0, 4, 8, 12, 16, 20, 24, 28],
    "vel": {"hat": {str(i): 0.3 for i in range(0, 32, 4)}}}),
 "new_jack_swing": ("njs_swingbeat", "swung machine 16ths + gated backbeat",
   {"bars": 1, "swing": 0.58, "bass_style": "roots",
    "kick": [0, 6, 8, 14], "snare": [4, 12], "hat": list(range(16)),
    "vel": {"hat": {str(i): (0.5 if i % 4 == 0 else 0.3) for i in range(16)}}}),
 "swing_bigband": ("bigband_ride", "swung ride + feathered kick + cross-stick 2&4",
   {"bars": 1, "swing": 0.64, "swing_grid": "8th", "bass_style": "walking",
    "ride": [0, 2, 4, 6, 8, 10, 12, 14], "rim": [4, 12],
    "kick": [0, 8], "vel": {"kick": {"0": 0.3, "8": 0.3}}}),
 "pop": ("pop_four", "clean four + clap, straight 8th hats",
   {"bars": 1, "swing": 0.5, "bass_style": "roots",
    "kick": [0, 4, 8, 12], "clap": [4, 12], "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
 "sexy_drill": ("sexydrill_bounce", "displaced drill kicks under rim-led halftime",
   {"bars": 2, "swing": 0.5, "bass_style": "sliding",
    "kick": [0, 6, 11, 16, 22, 25], "rim": [8, 24], "ghost": [15, 17],
    "hat": [0, 4, 8, 12, 16, 20, 24, 28]}),
 "3step": ("threestep_cell", "the 3-hit cell with even more space than amapiano",
   {"bars": 1, "swing": 0.52, "bass_style": "log",
    "kick": [0, 6, 12], "hat": [2, 6, 10, 14],
    "vel": {"hat": {"2": 0.3, "6": 0.3, "10": 0.3, "14": 0.3}}}),
 "speed_garage": ("speedgarage_4x4", "4x4 garage shuffle, skippy ghosts",
   {"bars": 1, "swing": 0.58, "bass_style": "sliding",
    "kick": [0, 4, 8, 12], "snare": [4, 12], "hat": [2, 6, 10, 14], "ghost": [7, 15]}),
 "bassline": ("bassline_niche", "4x4 with the warped-sub bounce",
   {"bars": 1, "swing": 0.56, "bass_style": "sliding",
    "kick": [0, 4, 8, 12], "snare": [4, 12], "hat": [2, 6, 10, 14], "ghost": [11]}),
 "french_house": ("frenchhouse_pump", "filtered 4-floor, pumped 16th hats",
   {"bars": 1, "swing": 0.5, "bass_style": "offbeat",
    "kick": [0, 4, 8, 12], "openhat": [2, 6, 10, 14], "hat": list(range(16)),
    "vel": {"hat": {str(i): (0.55 if i % 4 == 2 else 0.3) for i in range(16)}}}),
 "latin_trap": ("latintrap_lilt", "dembow lean under trap slide",
   {"bars": 1, "swing": 0.52, "bass_style": "sliding",
    "kick": [0, 7, 10], "snare": [8], "rim": [3, 11], "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
 "orchestral_cinematic": ("cinematic_pulse", "timpani anchors + a hit every 4 bars",
   {"bars": 2, "swing": 0.5, "bass_style": "sustained",
    "kick": [0, 16, 24], "vel": {"kick": {"0": 0.9, "16": 0.7, "24": 0.95}}}),
 "boombap": None,   # already covered in wave 1 patterns — listed for the audit trail
}

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-patterns-w2 (executable loop DNA)"
    n = 0
    for genre, spec in G2.items():
        if spec is None:
            continue
        name, desc, grid = spec
        kg.upsert("PatternArchetype", name, prov, desc=desc, grid=json.dumps(grid))
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", name)
        n += 1
    total = kg.q("MATCH (g:Genre)-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                 "WHERE p.grid IS NOT NULL RETURN count(DISTINCT g)")[0][0]
    print(f"pattern DNA wave 2: +{n} archetypes; {total} genres now loop-generatable")

if __name__ == "__main__":
    seed()
