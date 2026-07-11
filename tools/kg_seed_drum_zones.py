#!/usr/bin/env python3
"""Drum zone enrichment (2026-07-03): the core kit grew control zones — faces get
knobs, agents get automatable params. Inits equal the old constants, so every
existing song renders BIT-IDENTICAL (verified by md5 on eval_funk + probe song);
each knob's effect verified directionally (tail dB / centroid probes).
Idempotent (MERGE)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-drum-zones (byte-identical defaults + directional probes verified)"
    R = {
     "kick_punch_zones": ("kick_punch",
        "kick_punch now has knobs (source.params or automate): punch 0-1.5 (click level), "
        "drop 0-8 (pitch-env depth), decay 0.05-1.2s (body), tail 0-1, drive 0.2-4 (pre-tanh). "
        "Defaults = the classic sound. Longer decay 0.6-0.9 = room-shaking house kick; "
        "drive 2+ = distorted techno.", ["house", "techno", "hard_techno", "gabber"]),
     "kick_808_zones": ("kick_808",
        "kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 "
        "(tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for "
        "verse/drop contrast.", ["trap", "drill", "phonk", "memphis_rap"]),
     "snare_zones": ("snare",
        "snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch "
        "scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; "
        "tone 0.7 + decay 1.5 = fat lo-fi snare.", ["trap", "boombap", "lofi"]),
     "hat_zones": ("hat",
        "hat knobs: decay 0.01-0.6 (0.05 closed default; 0.25-0.4 = OPEN HAT — same voice, "
        "one knob), tone 4k-16k (bp centre), sizzle 0.5-8 (Q). Automate decay for open/closed "
        "patterns on ONE track.", ["house", "ukgarage", "disco", "techno"]),
     "clap_909_zones": ("clap_909",
        "clap_909 knobs: decay 0.08-0.8s (main burst), tone 600-4000 (bp centre), spread "
        "0.3-2.5 (pre-burst roll tightness). tone 2800 = brighter electro clap; spread 2 = "
        "loose human clap.", ["house", "electro", "italo_disco"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("drum-zone recipes seeded:", ", ".join(R))

if __name__ == "__main__":
    seed()
