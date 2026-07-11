#!/usr/bin/env python3
"""Wave 20: loop DNA — the world/ceremonial twelve. THE MAP COMPLETES (118 -> 131/131).

Balearic's lazy four, calypso's 3-3-2 bell, the celtic reel lilt, corridos'
tuba sway, DRONE (the minimal grid: one kick, nothing else — the sustained
bass and pad ARE the piece), rumba flamenca palmas, forro's baiao zabumba
(kick 0+7 dotted), gnawa's krakeb shuffle (swing 0.66 — trance by iron
castanets), klezmer freylekh bounce, kompa's gong cell, mariachi ranchera
(tololoche walks), singeli's 180bpm sprint.
Provenance: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete)"

WAVE = {
    "balearic": ("balearic_lazy", {
        "bars": 1, "swing_grid": "8th", "swing": 0.53, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.5, "12": 0.55}, "hat": {str(i): 0.35 for i in range(0, 16, 2)}}}),
    "calypso": ("calypso_bell", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 3, 6, 8, 11, 14]}),
    "celtic": ("reel_lilt", {
        "bars": 1, "swing_grid": "8th", "swing": 0.55, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.45, "12": 0.5},
                "hat": {"0": 0.7, "8": 0.7, "4": 0.5, "12": 0.5}}}),
    "corridos_tumbados": ("tuba_sway", {
        "bars": 1, "swing_grid": "8th", "swing": 0.54, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 4, 8, 12],
        "vel": {"snare": {"4": 0.4, "12": 0.45}}}),
    "drone": ("drone_minimal", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0], "snare": [],
        "hat": []}),
    "flamenco": ("rumba_palmas", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 7, 12, 15],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"7": 0.55, "15": 0.6, "4": 0.8, "12": 0.85},
                "hat": {str(i): 0.3 for i in range(0, 16, 2)}}}),
    "forro": ("baiao_zabumba", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 7], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.4 if i % 2 == 0 else 0.25) for i in range(16)},
                "kick": {"0": 1.0, "7": 0.7}}}),
    "gnawa": ("krakeb_shuffle", {
        "bars": 1, "swing_grid": "8th", "swing": 0.66, "bass_style": "roots",
        "kick": [0, 8], "snare": [],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): (0.7 if i % 4 == 0 else 0.5) for i in range(0, 16, 2)}}}),
    "klezmer": ("freylekh_bounce", {
        "bars": 1, "swing_grid": "8th", "swing": 0.54, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.7, "6": 0.7, "10": 0.7, "14": 0.7,
                        "0": 0.35, "4": 0.35, "8": 0.35, "12": 0.35}}}),
    "kompa": ("kompa_gong", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 3, 4, 7, 8, 11, 12, 15],
        "vel": {"kick": {str(i): 0.6 for i in (0, 4, 8, 12)},
                "snare": {"4": 0.5, "12": 0.5}}}),
    "mariachi": ("ranchera_walk", {
        "bars": 1, "swing": 0.5, "bass_style": "walking",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.75, "6": 0.75, "10": 0.75, "14": 0.75}}}),
    "singeli": ("singeli_sprint", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 4, 8, 12], "snare": [4, 12, 14],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.5 if i % 2 else 0.35) for i in range(16)},
                "snare": {"14": 0.6}}}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave20)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:20} <- {pname}")
    print(f"wave20: {len(WAVE)} genres — THE MAP COMPLETES")
