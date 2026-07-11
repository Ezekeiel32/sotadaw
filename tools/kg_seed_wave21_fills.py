#!/usr/bin/env python3
"""Wave 21: FILLS — the turnaround bar for 12 flagship genres (loops learn to breathe).

Each fill replaces the pattern on bar 4 (and the loop's final bar): trap's
snare roll into the one, techno's tom run, house's clap build, dnb's amen
chop-up, boombap's stutter, funk's ghost flurry, ukg's skip snare, amapiano's
log-drum answer, reggaeton's dembow break, disco's crash build, jazz's round
turnaround, rock's tom fill. Same JSON shape as the main grid, under "fill".
Provenance: curated:claude/2026-07-04 (wave21 fills — loop_gen stamps bar 4).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave21 fills — loop_gen stamps bar-4 turnarounds)"

# genre -> (archetype name from earlier waves, fill dict)
FILLS = {
    "trap": ("trap_drums", {
        "kick": [0, 8], "snare": [4, 8, 10, 12, 13, 14, 15],
        "hat": [0, 2, 4, 6],
        "vel": {"snare": {"8": 0.5, "10": 0.6, "12": 0.75, "13": 0.8, "14": 0.9, "15": 1.0}}}),
    "techno": ("techno_grid", {
        "kick": [0, 4, 8, 12], "snare": [10, 11, 12, 13, 14, 15],
        "hat": [2, 6],
        "vel": {"snare": {"10": 0.4, "11": 0.45, "12": 0.55, "13": 0.65, "14": 0.8, "15": 0.95}}}),
    "house": ("house_grid", {
        "kick": [0, 4, 8, 12], "snare": [8, 10, 12, 14, 15],
        "hat": [2, 6, 10, 14],
        "vel": {"snare": {"8": 0.5, "10": 0.6, "12": 0.7, "14": 0.85, "15": 1.0}}}),
    "dnb": ("dnb_break", {
        "kick": [0, 6, 11], "snare": [4, 7, 9, 12, 14, 15],
        "hat": [0, 2, 4, 6, 8, 10],
        "vel": {"snare": {"7": 0.5, "9": 0.55, "14": 0.8, "15": 0.95}}}),
    "boombap": ("boombap_drums", {
        "kick": [0, 3, 8], "snare": [4, 11, 12, 14],
        "hat": [0, 2, 4, 6, 8, 10],
        "vel": {"snare": {"11": 0.5, "14": 0.85}}}),
    "funk": ("the_one_ghosts", {
        "kick": [0, 10], "snare": [2, 4, 6, 7, 9, 11, 12, 13, 14, 15],
        "hat": [0, 4, 8],
        "vel": {"snare": {"2": 0.3, "6": 0.35, "7": 0.4, "9": 0.4, "11": 0.5,
                          "13": 0.6, "14": 0.8, "15": 1.0, "4": 0.85, "12": 0.9}}}),
    "ukgarage": ("ukg_2step", {
        "kick": [0, 10], "snare": [4, 7, 11, 13, 14],
        "hat": [0, 2, 6, 8],
        "vel": {"snare": {"7": 0.5, "11": 0.55, "13": 0.7, "14": 0.9}}}),
    "amapiano": ("ama_pocket", {
        "kick": [0, 6], "snare": [8, 11, 13, 14, 15],
        "hat": [0, 2, 4, 6],
        "vel": {"snare": {"8": 0.5, "11": 0.6, "13": 0.7, "14": 0.8, "15": 0.9}}}),
    "reggaeton": ("dembow_grid", {
        "kick": [0, 4, 8], "snare": [3, 6, 10, 12, 14, 15],
        "hat": [0, 2, 4, 6, 8],
        "vel": {"snare": {"10": 0.6, "12": 0.7, "14": 0.85, "15": 1.0}}}),
    "disco": ("disco_four", {
        "kick": [0, 4, 8, 12], "snare": [4, 8, 12, 14, 15],
        "hat": [0, 1, 2, 3, 4, 5, 6, 7],
        "vel": {"snare": {"8": 0.6, "14": 0.85, "15": 1.0}}}),
    "jazz": ("swing_ride_grid", {
        "kick": [0, 11], "snare": [4, 6, 9, 12, 14],
        "hat": [0, 4, 8],
        "vel": {"snare": {"6": 0.4, "9": 0.5, "12": 0.7, "14": 0.85}}}),
    "rock": ("rock_backbeat", {
        "kick": [0, 8], "snare": [4, 8, 10, 12, 14],
        "hat": [0, 2, 4, 6],
        "vel": {"snare": {"8": 0.6, "10": 0.7, "12": 0.85, "14": 1.0}}}),
}

if __name__ == "__main__":
    kg = KG()
    done = 0
    for genre, (pname, fill) in FILLS.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {genre}: archetype {pname} MISSING — skipped")
            continue
        grid = json.loads(rows[0][0])
        grid["fill"] = fill
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
        print(f"  {genre:12} fill -> {pname}")
    print(f"wave21: {done} fills seeded")
