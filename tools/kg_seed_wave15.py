#!/usr/bin/env python3
"""Wave 15: loop DNA — the dance-floor wave (62 -> 76 generate_loop coverage).

Fourteen club lineages authored as grids: acid house's 909 shuffle, Chicago's
jack, deep house's shuffled hats, progressive's rolling pulse, minimal's
skeleton, dub techno's chords-in-the-holes echo pulse, grime's 8-bar cross
pattern, Memphis's lo-fi knock, ghettotech's 160 twitch, kuduro's carnival
kick cluster, gabber's distorted four, happy hardcore's bounce, breaks' funky
drummer lift, big beat's swagger.
Provenance: curated:claude/2026-07-04 + grid:curated (wave15 machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave15 machine-readable loop DNA)"

WAVE = {
    "acid_house": ("acid_shuffle", {
        "bars": 1, "swing": 0.54, "bass_style": "psy_rolling",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.75, "6": 0.75, "10": 0.75, "14": 0.75}}}),
    "chicago_house": ("chicago_jack", {
        "bars": 1, "swing": 0.53, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14],
        "vel": {"snare": {"4": 0.9, "12": 0.95}}}),
    "deephouse": ("deep_shuffle", {
        "bars": 1, "swing": 0.56, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 5, 6, 10, 13, 14],
        "vel": {"hat": {"5": 0.4, "13": 0.4}}}),
    "progressive_house": ("prog_roll", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.55 if i % 4 == 2 else 0.25) for i in range(16)}}}),
    "minimal_techno": ("minimal_skeleton", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [12],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.35, "6": 0.3, "10": 0.35, "14": 0.3}}}),
    "dub_techno": ("dubtech_pulse", {
        "bars": 1, "swing": 0.52, "bass_style": "roots",
        "kick": [0, 4, 8, 12], "snare": [],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.3, "6": 0.35, "10": 0.3, "14": 0.35}}}),
    "grime": ("grime_cross", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 6, 10], "snare": [4, 12],
        "hat": [0, 2, 8, 11, 14]}),
    "memphis_rap": ("memphis_knock", {
        "bars": 1, "swing": 0.52, "bass_style": "sliding",
        "kick": [0, 3, 8, 11], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.35, "6": 0.35, "10": 0.35, "14": 0.35}}}),
    "ghettotech": ("ghetto_twitch", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 4, 7, 8, 12], "snare": [4, 12],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"hat": {str(i): (0.5 if i % 2 else 0.3) for i in range(16)}}}),
    "kuduro": ("kuduro_carnival", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 3, 6, 8, 11, 14], "snare": [4, 12],
        "hat": [2, 6, 10, 14]}),
    "gabber": ("gabber_four", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 2, 4, 6, 8, 10, 12, 14], "snare": [4, 12],
        "hat": [1, 3, 5, 7, 9, 11, 13, 15],
        "vel": {"kick": {str(i): 1.0 for i in range(0, 16, 2)},
                "hat": {str(i): 0.3 for i in range(1, 16, 2)}}}),
    "happy_hardcore": ("happy_bounce", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.8, "6": 0.8, "10": 0.8, "14": 0.8}}}),
    "breaks": ("funky_lift", {
        "bars": 1, "swing": 0.54, "bass_style": "roots",
        "kick": [0, 10], "snare": [4, 7, 12, 15],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"7": 0.35, "15": 0.3}}}),
    "big_beat": ("bigbeat_swagger", {
        "bars": 1, "swing": 0.53, "bass_style": "sustained",
        "kick": [0, 3, 10], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 1.0, "12": 1.0}}}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave15)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:18} <- {pname}")
    print(f"wave15: {len(WAVE)} genres gained loop DNA")
