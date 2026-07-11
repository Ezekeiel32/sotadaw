#!/usr/bin/env python3
"""Wave 18: loop DNA — hard / festival / latin+zouk (90 -> 104 generate_loop coverage).

EBM's sequencer stomp, industrial's machine press, hardwave's halftime weight,
future garage's ghosted 2-step drift, chillwave's washed backbeat, bigroom's
festival four, Baltimore club's 8-count kick cell, bounce's triggerman lean,
crunk's slow 808 menace, breakbeat hardcore's driven breaks, merengue's tambora
gallop, bachata's requinto-era bongo grid, tango's habanera spine, zouk's
carnival machine.
Provenance: curated:claude/2026-07-04 + grid:curated (wave18 machine-readable loop DNA).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 + grid:curated (wave18 machine-readable loop DNA)"

WAVE = {
    "ebm": ("ebm_stomp", {
        "bars": 1, "swing": 0.5, "bass_style": "psy_rolling",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [2, 6, 10, 14],
        "vel": {"hat": {"2": 0.7, "6": 0.7, "10": 0.7, "14": 0.7}}}),
    "industrial": ("machine_press", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 4, 8, 12], "snare": [4, 10, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"10": 0.5, "4": 0.9, "12": 1.0}}}),
    "hardwave": ("hardwave_halftime", {
        "bars": 1, "swing": 0.5, "bass_style": "sustained",
        "kick": [0, 10], "snare": [8],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"8": 1.0}}}),
    "future_garage": ("fg_drift", {
        "bars": 1, "swing_grid": "8th", "swing": 0.57, "bass_style": "sustained",
        "kick": [0, 10], "snare": [4, 12],
        "hat": [2, 6, 7, 10, 14],
        "vel": {"hat": {"7": 0.3, "2": 0.45, "14": 0.4}, "snare": {"4": 0.55, "12": 0.6}}}),
    "chillwave": ("washed_backbeat", {
        "bars": 1, "swing_grid": "8th", "swing": 0.55, "bass_style": "sustained",
        "kick": [0, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"4": 0.5, "12": 0.55}, "hat": {str(i): 0.35 for i in range(0, 16, 2)}}}),
    "bigroom": ("festival_four", {
        "bars": 1, "swing": 0.5, "bass_style": "offbeat",
        "kick": [0, 4, 8, 12], "snare": [],
        "hat": [2, 6, 10, 14],
        "vel": {"kick": {str(i): 1.0 for i in (0, 4, 8, 12)}}}),
    "baltimore_club": ("bmore_cell", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 3, 6, 8, 11, 14], "snare": [4, 12],
        "hat": [2, 6, 10, 14]}),
    "bounce": ("triggerman_lean", {
        "bars": 1, "swing": 0.52, "bass_style": "sliding",
        "kick": [0, 3, 7, 8, 11], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14]}),
    "crunk": ("crunk_menace", {
        "bars": 1, "swing": 0.5, "bass_style": "sliding",
        "kick": [0, 7, 8], "snare": [4, 12],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"hat": {str(i): (0.5 if i % 4 == 0 else 0.3) for i in range(0, 16, 2)}}}),
    "breakbeat_hardcore": ("hardcore_breaks", {
        "bars": 1, "swing": 0.52, "bass_style": "sliding",
        "kick": [0, 10], "snare": [4, 7, 12, 15],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"7": 0.4, "15": 0.35}}}),
    "merengue": ("tambora_gallop", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 4, 8, 12], "snare": [2, 6, 7, 10, 14, 15],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"2": 0.4, "6": 0.4, "7": 0.75, "10": 0.4, "14": 0.4, "15": 0.8}}}),
    "bachata": ("bachata_bongo", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 8], "snare": [4, 12, 15],
        "hat": [0, 2, 4, 6, 8, 10, 12, 14],
        "vel": {"snare": {"15": 0.9, "4": 0.5, "12": 0.5}}}),
    "tango": ("habanera_spine", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 3, 8, 12], "snare": [8],
        "hat": [0, 4, 8, 12],
        "vel": {"kick": {"0": 1.0, "3": 0.6, "8": 0.8, "12": 0.7}}}),
    "zouk": ("zouk_machine", {
        "bars": 1, "swing": 0.5, "bass_style": "roots",
        "kick": [0, 4, 8, 12], "snare": [4, 12],
        "hat": [0, 3, 4, 7, 8, 11, 12, 15],
        "vel": {"hat": {"3": 0.6, "7": 0.6, "11": 0.6, "15": 0.6}}}),
}

if __name__ == "__main__":
    kg = KG()
    for genre, (pname, grid) in WAVE.items():
        kg.upsert("PatternArchetype", pname, PROV,
                  grid=json.dumps(grid), desc=f"{genre} loop DNA (wave18)")
        kg.link("Genre", genre, "CHARACTERIZED_BY", "PatternArchetype", pname)
        print(f"  {genre:20} <- {pname}")
    print(f"wave18: {len(WAVE)} genres gained loop DNA")
