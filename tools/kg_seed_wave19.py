#!/usr/bin/env python3
"""Wave 19: loop DNA — the majors that slipped through (104 -> 118 coverage).

Funk's ghost-note One, gospel shout, ska's offbeat skank accents, soca power
kick, synthpop's solid four, italo's octave gallop, shoegaze wash, melodic
techno's sparse clap, neurofunk's reese carrier, fusion's 16th pocket, kpop's
trap-pop hybrid, jpop drive, nightcore's sped four, witch house halftime.
Provenance: curated:claude/2026-07-04 + grid:curated (wave19 machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave19 machine-readable loop DNA)"

WAVE = {
    "funk": ("the_one_ghosts", {
        "bars": 1, "swing": 0.53, "bass_style": "roots",
        "kick": [0, 3, 10], "snare": [2, 4, 7, 11, 12, 14],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"snare": {"2": 0.3, "7": 0.3, "11": 0.28, "14": 0.32, "4": 0.9, "12": 0.95},
                "hat": {str(i): (0.5 if i % 4 == 0 else 0.3) for i in range(16)}}}),
    "gospel": ("gospel_shout", {
        "bars": 1, "swing_grid": "8th", "swing": 0.54, "bass_style": "walking",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.9, "12": 1.0}}}),
    "ska": ("skank_accents", {
        "bars": 1, "swing_grid": "8th", "swing": 0.52, "bass_style": "walking",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.8, "6": 0.8, "10": 0.8, "14": 0.8,
                        "0": 0.3, "4": 0.3, "8": 0.3, "12": 0.3}}}),
    "soca": ("soca_power", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 4, 7, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "synthpop": ("synthpop_four", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {"2": 0.55, "6": 0.55, "10": 0.55, "14": 0.55}}}),
    "italo_disco": ("italo_gallop", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.85, "6": 0.85, "10": 0.85, "14": 0.85}}}),
    "shoegaze": ("gaze_wash", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 8, 10], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): 0.3 for i in range(0, 16, 2)}}}),
    "melodic_techno": ("melodic_sparse", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 4, 8, 12], "snare": [12],
        "hat": [2, 6, 10, 14],
        "vel": {"snare": {"12": 0.55}, "hat": {"2": 0.4, "6": 0.35, "10": 0.4, "14": 0.35}}}),
    "neurofunk": ("reese_carrier", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 10], "snare": [4, 12],
        "hat": [0, 2, 3, 6, 8, 10, 11, 14],
        "vel": {"hat": {"3": 0.4, "11": 0.4}}}),
    "jazzfusion": ("fusion_sixteen", {
        "bars": 1, "swing": 0.54, "bass_style": "roots",
        "kick": [0, 6, 10, 13], "snare": [4, 7, 12, 15],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "vel": {"snare": {"7": 0.3, "15": 0.3, "4": 0.85, "12": 0.9},
                "hat": {str(i): (0.45 if i % 2 == 0 else 0.28) for i in range(16)}}}),
    "kpop": ("kpop_hybrid", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 7, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 13, 14, 15],
        "vel": {"hat": {"13": 0.4, "15": 0.4}}}),
    "jpop": ("jpop_drive", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 8, 11], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "nightcore": ("nightcore_sped", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14, 15]}),
    "witch_house": ("witch_halftime", {
        "bars": 1, "swing": 0.54, "bass_style": "sliding",
        "kick": [0, 10], "snare": [8],
        "hat": [0, 4, 8, 12, 14],
        "vel": {"hat": {"14": 0.4}}}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave19)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:16} <- {pname}")
    print(f"wave19: {len(WAVE)} genres gained loop DNA")
