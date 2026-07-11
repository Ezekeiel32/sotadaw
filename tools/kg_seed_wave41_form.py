#!/usr/bin/env python3
"""Wave 41: FORM FAMILY per genre (f155) — which arrangement grammar each genre speaks.

Families: club (DJ-intro 16 + mixable outro 16, cited f155: intros are multiples
of 16 with incremental layering; outros are where DJs mix out), song (verse/
chorus land), pop (Harmonix-sampled human grammar), loop (the compact default).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-06 (wave41 form families; DJ-intro 16/32 + outro convention cited f155)"

FAM = {}
for g in ("house", "deephouse", "techno", "melodic_techno", "detroit_techno", "chicago_house",
          "acid_house", "afro_house", "trance", "psytrance", "goa", "progressive_house",
          "techhouse", "dnb", "neurofunk", "ukgarage", "speed_garage", "bassline", "dubstep",
          "hardstyle", "hardtechno", "bigroom", "eurodance", "amapiano", "3step", "afrobeats",
          "minimal", "dub_techno", "breaks", "electro"):
    FAM[g] = "club"
for g in ("gospel", "soul", "rnb", "neosoul", "country", "blues", "rock", "indie_rock",
          "funk", "disco", "reggae", "citypop", "bossanova", "jazz", "salsa", "cumbia",
          "bachata", "merengue", "highlife", "calypso"):
    FAM[g] = "song"
for g in ("pop", "synthpop", "jpop", "kpop", "hyperpop", "chillwave", "synthwave", "indie_pop"):
    FAM[g] = "pop"

if __name__ == "__main__":
    kg = KG()
    done = 0
    for g, fam in FAM.items():
        if kg.q(f"MATCH (g:Genre {{name:'{g}'}}) RETURN g.name"):
            kg.upsert("Genre", g, PROV, form_family=fam)
            done += 1
    print(f"wave41: {done} genres carry a form family")
