#!/usr/bin/env python3
"""Melodic zone enrichment (2026-07-03): six core melodic voices grew designed
zones (inits == old constants; defaults preserved within float-ULP, verified by
sample comparison + directional probes — see W18g ledger). Idempotent (MERGE)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-melodic-zones (ULP-identical defaults + directional probes)"
    R = {
     "organ_soul_zones": ("organ_soul",
        "organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: "
        "16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + "
        "speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); "
        "ballad = sparkle 0.4 + speed 0.8.", ["gospel", "soul", "funk", "rnb", "blues"]),
     "clav_funk_zones": ("clav_funk",
        "clav_funk knobs: duty 0.1-0.45 (pulse width - hollowness of the bark), snap 0-1.5, "
        "decay 0.1-1s, tone 2000-12000 (resonant LP). Wah-clav = automate tone with the "
        "groove; darker funk comp = tone 4000.", ["funk", "disco", "gfunk"]),
     "rhodes_zones": ("rhodes",
        "rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright "
        "attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; "
        "gospel chords = sustain 0.5 + decay 2.", ["lofi", "rnb", "soul", "jazz", "neo_soul"]),
     "keys_dark_zones": ("keys_dark",
        "keys_dark knobs: cutoff 200-3000 + sweep 0-6000 (filter env range), sub 0-1 "
        "(octave-down weight), detune/vibrato 0-0.02. Trap bell-keys = cutoff 1500 sub 0.8; "
        "automate cutoff for section builds.", ["trap", "drill", "phonk", "hardwave"]),
     "pluck_zones": ("pluck",
        "pluck knobs: decay 0.05-2s (squared env - snappy), color 1-12 (pitch-tracking LP "
        "multiple: 2 = dark koto, 10 = open). Dance plucks = color 6-8 decay 0.3; automate "
        "color rising into a drop.", ["trance", "progressive_house", "future_bass", "eurodance"]),
     "pad_motion_zones": ("pad_motion",
        "pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth "
        "0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = "
        "motion 0.6 + drift 0.3; automate depth for evolving intros.", ["ambient", "trance", "synthwave", "dub_techno"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("melodic-zone recipes seeded:", ", ".join(R))

if __name__ == "__main__":
    seed()
