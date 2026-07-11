#!/usr/bin/env python3
"""Wave 22: MELODY DNA — lead hooks for 12 flagships (loops get a voice on top).

Each lead is [[step16, scale_degree(1-based, 8=octave), len_in_16ths], ...]:
trap's dark minor bell taps, techno's hypnotic two-note cell, house's organ
stab riff, dnb's rave stab pair, boombap's dusty loop phrase, funk's single-
note clav jab (rhythm IS the melody), ukg's vocal-chop contour, amapiano's
log-melody answer, reggaeton's plucked hook, disco's octave string run,
jazz's enclosure lick, rock's pentatonic riff.
Provenance: curated:claude/2026-07-04 (wave22 melody DNA; degrees resolve in song key).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-04 (wave22 melody DNA — lead hooks in key)"

LEADS = {
    "trap": ("trap_drums", {"voice": "fmbell", "octave": 5,
        "steps": [[0, 1, 2], [6, 3, 1], [8, 1, 2], [14, 4, 1]]}),
    "techno": ("techno_grid", {"voice": "pluck2", "octave": 5,
        "steps": [[2, 1, 1], [6, 5, 1], [10, 1, 1], [14, 5, 1]]}),
    "house": ("house_grid", {"voice": "organ_soul", "octave": 5,
        "steps": [[2, 5, 1], [4, 3, 2], [10, 5, 1], [12, 8, 2]]}),
    "dnb": ("dnb_break", {"voice": "pluck2", "octave": 6,
        "steps": [[0, 1, 1], [2, 1, 1], [8, 5, 2], [11, 4, 1]]}),
    "boombap": ("boombap_drums", {"voice": "keys_dark", "octave": 5,
        "steps": [[0, 3, 2], [4, 1, 2], [10, 4, 2], [14, 5, 2]]}),
    "funk": ("the_one_ghosts", {"voice": "clav_funk", "octave": 5,
        "steps": [[0, 1, 1], [3, 1, 1], [7, 1, 1], [10, 8, 1], [11, 1, 1]]}),
    "ukgarage": ("ukg_2step", {"voice": "vox_pad", "octave": 5,
        "steps": [[2, 5, 2], [7, 4, 1], [10, 3, 2], [14, 1, 2]]}),
    "amapiano": ("ama_pocket", {"voice": "log_drum", "octave": 4,
        "steps": [[2, 1, 1], [5, 4, 1], [8, 5, 1], [13, 3, 1]]}),
    "reggaeton": ("dembow_grid", {"voice": "pluck2", "octave": 5,
        "steps": [[0, 5, 1], [3, 4, 1], [6, 3, 1], [8, 1, 2], [14, 5, 1]]}),
    "disco": ("disco_four", {"voice": "strings_disco", "octave": 5,
        "steps": [[0, 1, 2], [4, 8, 2], [8, 5, 2], [12, 8, 4]]}),
    "jazz": ("swing_ride_grid", {"voice": "rhodes", "octave": 5,
        "steps": [[0, 3, 1], [2, 2, 1], [4, 1, 2], [8, 5, 1], [10, 6, 1], [12, 5, 3]]}),
    "rock": ("rock_backbeat", {"voice": "guitar_grit", "octave": 4,
        "steps": [[0, 1, 2], [4, 4, 1], [6, 5, 2], [10, 4, 1], [12, 1, 3]]}),
}

if __name__ == "__main__":
    kg = KG()
    done = 0
    for genre, (pname, lead) in LEADS.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {genre}: {pname} MISSING — skipped")
            continue
        grid = json.loads(rows[0][0])
        grid["lead"] = lead
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
        print(f"  {genre:12} lead ({lead['voice']}) -> {pname}")
    print(f"wave22: {done} leads seeded")
