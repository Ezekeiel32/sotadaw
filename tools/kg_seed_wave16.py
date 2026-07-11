#!/usr/bin/env python3
"""Wave 16: loop DNA — the world + live-band wave (76 -> 90 generate_loop coverage).

Samba's surdo weight on 2, Tony Allen's afrobeat ghosts, highlife's bell,
rock/indie/post-punk backbeats (motorik-driving vs pickup-loose), the blues
SHUFFLE (swing 0.66 — the deepest swing in the graph), country train, soul
pocket, rocksteady's proto-one-drop, citypop's slap-disco gloss, IDM's broken
grid, downtempo drag, vaporwave's slowed quarters.
Provenance: curated:claude/2026-07-04 + grid:curated (wave16 machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave16 machine-readable loop DNA)"

WAVE = {
    "samba": ("surdo_two", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 3, 6, 10, 13],
        "vel": {"kick": {"0": 0.55, "8": 1.0}, "snare": {"4": 0.4, "12": 0.45}}}),
    "afrobeat": ("allen_ghosts", {
        "bars": 1, "swing": 0.52, "bass_style": "roots",
        "kick": [0, 7], "snare": [2, 4, 10, 12],
        "hat": [0, 2, 4, 5, 8, 10, 12, 14],
        "vel": {"snare": {"2": 0.3, "10": 0.3, "4": 0.75, "12": 0.8}}}),
    "highlife": ("highlife_bell", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 3, 6, 8, 11, 14]}),
    "rock": ("rock_backbeat", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.95, "12": 1.0}}}),
    "post_punk": ("motorik_drive", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): 0.6 for i in range(0, 16, 2)}}}),
    "indie_rock": ("indie_loose", {
        "bars": 1, "swing": 0.51, "bass_style": "roots",
        "kick": [0, 6, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "blues": ("blues_shuffle", {
        "bars": 1, "swing_grid": "8th", "swing": 0.66, "bass_style": "walking",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): (0.6 if i % 4 == 0 else 0.35) for i in range(0, 16, 2)}}}),
    "country": ("train_beat", {
        "bars": 1, "swing_grid": "8th", "swing": 0.54, "bass_style": "walking",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): (0.55 if i % 4 == 2 else 0.4) for i in range(0, 16, 2)}}}),
    "soul": ("soul_pocket", {
        "bars": 1, "swing_grid": "8th", "swing": 0.55, "bass_style": "roots",
        "kick": [0, 6, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.85, "12": 0.9}}}),
    "rocksteady": ("proto_one_drop", {
        "bars": 1, "swing_grid": "8th", "swing": 0.54, "bass_style": "roots",
        "kick": [8], "snare": [8],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.5, "6": 0.5, "10": 0.5, "14": 0.5}}}),
    "citypop": ("citypop_gloss", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 8, 11], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.75 if i in (2, 6, 10, 14) else 0.3) for i in range(16)}}}),
    "idm": ("broken_grid", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 3, 10], "snare": [4, 7, 12, 14],
        "hat": [1, 5, 6, 9, 13],
        "vel": {"snare": {"7": 0.4, "14": 0.5}}}),
    "downtempo": ("down_drag", {
        "bars": 1, "swing_grid": "8th", "swing": 0.56, "bass_style": "sustained",
        "kick": [0, 9], "snare": [4, 12],
        "hat": [0, 4, 8, 12],
        "vel": {"hat": {"4": 0.4, "12": 0.4}}}),
    "vaporwave": ("slowed_quarters", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 4, 8, 12]}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave16)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:12} <- {pname}")
    print(f"wave16: {len(WAVE)} genres gained loop DNA")
