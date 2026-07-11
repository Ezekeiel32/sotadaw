#!/usr/bin/env python3
"""Wave 14: loop DNA for 12 iconic missing genres (50 -> 62 generate_loop coverage).

Each grid is authored from genre scholarship — the pattern IS the genre:
dembow's k-ch cross, disco's four-on-the-floor with open-hat offbeats, the
tamborzão kick cluster, dub's one drop (kick+snare TOGETHER on 3), salsa's
cascara over tumbao anticipation, jazz ride swing, electro's broken 808 kick,
g-funk's lazy bounce, Detroit's pulse, UK funky's snap, trip-hop's drag.
Provenance: curated:claude/2026-07-04 + grid:curated (machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave14 machine-readable loop DNA)"

WAVE = {
    "reggaeton": ("dembow_grid", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 4, 8, 12], "snare": [3, 6, 11, 14],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"3": 0.85, "6": 0.7, "11": 0.85, "14": 0.7}}}),
    "disco": ("disco_four", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {"2": 0.85, "6": 0.85, "10": 0.85, "14": 0.85,
                        "0": 0.35, "4": 0.35, "8": 0.35, "12": 0.35}}}),
    "miami_bass": ("mia_electro", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 7, 10], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.5 if i % 2 == 0 else 0.28) for i in range(16)}}}),
    "baile_funk": ("tamborzao", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 3, 6, 10], "snare": [12, 14],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "dub": ("one_drop_dub", {
        "bars": 1, "swing": 0.56, "bass_style": "roots",
        "kick": [8], "snare": [8],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.5, "6": 0.5, "10": 0.5, "14": 0.5}}}),
    "salsa": ("tumbao_cascara", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [7, 15], "snare": [4, 12],
        "hat": [0, 2, 3, 5, 7, 8, 10, 11, 13, 15]}),
    "jazz": ("swing_ride_grid", {
        "bars": 1, "swing": 0.62, "bass_style": "walking",
        "kick": [0], "snare": [6, 10],
        "hat": [0, 4, 6, 8, 12, 14],
        "vel": {"snare": {"6": 0.35, "10": 0.4}, "hat": {"4": 0.7, "12": 0.7}}}),
    "electro": ("electro_break", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 10], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.4, "6": 0.4, "10": 0.4, "14": 0.4}}}),
    "gfunk": ("gfunk_bounce", {
        "bars": 1, "swing": 0.54, "bass_style": "sustained",
        "kick": [0, 7, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "detroit_techno": ("detroit_pulse", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14]}),
    "uk_funky": ("funky_snap", {
        "bars": 1, "swing": 0.55, "bass_style": "roots",
        "kick": [0, 6, 10], "snare": [4, 13],
        "hat": [0, 2, 4, 5, 8, 10, 12, 14]}),
    "triphop": ("trip_drag", {
        "bars": 1, "swing": 0.58, "bass_style": "sustained",
        "kick": [0, 9], "snare": [4, 12],
        "hat": [0, 4, 8, 10, 12]}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave14)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:16} <- {pname} (kick {grid['kick']}, swing {grid['swing']}, bass {grid['bass_style']})")
    print(f"wave14: {len(WAVE)} genres gained loop DNA")
