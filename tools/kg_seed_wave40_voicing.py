#!/usr/bin/env python3
"""Wave 40: GENRE VOICING REGISTER — style + range per flagship family (f151).

The M1 kernel speaks smooth/triad/open/drop2 with lo/hi; until now every genre
voiced identically (smooth 48-70). Canon: trap/drill color lives DARK AND LOW,
gospel/jazz spread WIDE (drop2 = the church/big-band left hand), pop/citypop
sits HIGH AND OPEN, folk families stay plain triads, reggae bubbles mid.
Stored as Genre.voicing JSON {style, lo, hi}; cache exports it; loop_gen obeys.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-06 (wave40 voicing register; family canon per stamp f151)"

V = {
    # dark & low
    **{g: {"style": "smooth", "lo": 41, "hi": 57} for g in
       ("trap", "drill", "phonk", "driftphonk", "memphis", "latin_trap", "sexydrill")},
    # church / jazz spread
    **{g: {"style": "drop2", "lo": 50, "hi": 74} for g in
       ("gospel", "soul", "rnb", "neosoul")},
    **{g: {"style": "drop2", "lo": 52, "hi": 76} for g in
       ("jazz", "bigband", "bossanova", "fusion")},
    # stab / pocket mids
    **{g: {"style": "smooth", "lo": 48, "hi": 66} for g in
       ("house", "deephouse", "chicago_house", "ukgarage", "speed_garage")},
    **{g: {"style": "smooth", "lo": 45, "hi": 60} for g in
       ("techno", "dnb", "neurofunk", "detroit_techno")},
    # bright & open
    **{g: {"style": "open", "lo": 55, "hi": 79} for g in
       ("citypop", "jpop", "pop", "synthpop", "hyperpop")},
    **{g: {"style": "open", "lo": 50, "hi": 72} for g in
       ("synthwave", "melodic_techno", "progressive_house")},
    **{g: {"style": "open", "lo": 52, "hi": 76} for g in
       ("hardstyle", "eurodance", "happyhardcore", "ambient", "chillwave")},
    # folk triads + organ bubble
    **{g: {"style": "triad", "lo": 52, "hi": 72} for g in
       ("cumbia", "salsa", "merengue", "bachata", "calypso", "highlife")},
    **{g: {"style": "smooth", "lo": 50, "hi": 64} for g in
       ("reggae", "dub", "dancehall")},
    **{g: {"style": "smooth", "lo": 50, "hi": 70} for g in
       ("afro_house", "amapiano", "3step", "afrobeats")},
}

if __name__ == "__main__":
    kg = KG()
    done = 0
    for g, v in V.items():
        if kg.q(f"MATCH (g:Genre {{name:'{g}'}}) RETURN g.name"):
            kg.upsert("Genre", g, PROV, voicing=json.dumps(v))
            done += 1
    print(f"wave40: {done} genres carry a voicing register")
