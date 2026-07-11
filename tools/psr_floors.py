#!/usr/bin/env python3
"""THE PSR FLOOR — one source of truth (docs/THE_PHYSICS.md E6, SPEC S12/V68).

The "don't over-squash it" number: how much dynamic punch must survive after a
streaming platform turns the track down to -14 LUFS. Per-genre, and resolved
PER SONG with graph intelligence:

    song  -> genre (meta.genre | genre | inferred)
          -> KG MixTarget.psr_floor            (the seeded, Chezy-tunable value)
          -> KG parent floor via SUBGENRE_OF   (a subgenre inherits its parent)
          -> published-practice seed table     (this file — the ONLY copy)
          -> default 6.0

This is the SINGLE home for the seed numbers. `kg_seed_physics.py` WRITES them
into the graph FROM here; `dynamics_ears.py` READS the graph THROUGH here. No
second table exists anywhere (the D6 no-spaghetti law).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Published-practice seed (MeterPlugs PSR guidance + streaming-normalized dynamics
# discourse). D3 PENDING Chezy: crate-measured floors may replace these; a KG value
# always wins at read time, so replacement needs zero code change here.
#
# THE FLOORS ARE FAMILY-TIER PRIORS, not individually-measured numbers — the physics
# is: heavily-limited electronic sits low (4.5-6), produced pop/urban mid (6-6.5),
# band/roots higher (7-8.5), live-acoustic + jazz + orchestral highest (8.5-12),
# because real transients + un-squashed dynamics carry more crest. Longest-substring
# wins, so a specific genre key overrides its family anchor. Before 2026-07-11 only
# 22 keys existed and 143 of 204 graph genres resolved to None — the universal
# loudness pass then pushed them toward the loudness ceiling with NO crest brake
# (recovery_step skips its budget guard on a None floor). The table now spans the
# whole taxonomy so every genre lands under a genre-appropriate punch guard.
SEED_PSR_FLOORS = {
    # -- compressed electronic: heavy limiting is the aesthetic, low crest --
    "phonk": 5.0, "trap": 5.0, "drill": 5.0, "edm": 5.0, "dubstep": 5.0,
    "gabber": 4.5, "breakcore": 4.5, "hardcore": 5.0, "hardstyle": 5.0,
    "hardwave": 5.0, "singeli": 5.0, "rage": 5.0, "glitchcore": 5.0,
    "sigilkore": 5.0, "dariacore": 5.0, "breakbeat_hardcore": 5.0,
    "happy_hardcore": 5.0, "techno": 5.5, "dnb": 5.5, "industrial": 5.5,
    "ebm": 5.5, "gqom": 5.5, "jungle": 5.5, "footwork": 5.5,
    "psytrance": 5.5, "bigroom": 5.5, "jerseyclub": 5.5, "ghettotech": 5.5,
    "baltimore_club": 5.5, "miami_bass": 5.5, "dembow": 5.5, "bassline": 5.5,
    "plugg": 5.5, "digicore": 5.5, "nightcore": 5.5, "automotivo": 5.5,
    # -- club/house/trance/disco: four-on-the-floor, moderate crest --
    "house": 6.0, "trance": 6.0, "goa": 6.0, "electro": 6.0, "kuduro": 6.0,
    "moombahton": 6.0, "future_bass": 6.0, "eurodance": 6.0, "eurobeat": 6.0,
    "hi_nrg": 6.0, "darksynth": 6.0, "afro_house": 6.0, "freestyle": 6.0,
    "big_beat": 6.0, "breaks": 6.0, "3step": 6.0, "garage": 6.0,
    "disco": 6.5, "italo_disco": 6.5, "synthwave": 6.5, "wave": 6.5,
    "kwaito": 6.5, "coupe_decale": 6.5,
    # -- pop / urban / produced vocal: mid crest --
    "hiphop": 6.0, "hip_hop": 6.0, "pop": 6.0, "memphis": 6.0, "crunk": 6.0,
    "bounce": 6.0, "grime": 6.0, "boombap": 7.0, "boogie": 7.0,
    "dancehall": 6.5, "reggaeton": 6.5, "afroswing": 6.5, "rnb": 6.5,
    "new_jack_swing": 6.5,
    # -- band: rock / metal / punk (loud, but real transients keep crest) --
    "rock": 7.0, "indie": 7.0, "punk": 7.0, "emo": 7.0, "ska": 7.0,
    "grunge": 7.0, "metal": 6.0, "djent": 6.0, "metalcore": 6.0,
    "shoegaze": 7.5, "vaporwave": 7.0, "chillwave": 7.5, "lofi": 7.5,
    "triphop": 7.5, "idm": 7.5,
    # -- roots / soul / funk / reggae --
    "funk": 7.0, "reggae": 7.0, "dub": 7.5, "soul": 7.5, "motown": 7.5,
    "doo_wop": 8.0, "gospel": 8.0, "blues": 8.5, "country": 8.0,
    "bluegrass": 8.5, "celtic": 8.5,
    # -- latin / brazilian / caribbean (live percussion) --
    "salsa": 8.0, "merengue": 7.5, "bachata": 7.5, "cumbia": 7.5,
    "champeta": 7.0, "soca": 7.0, "zouk": 7.0, "kompa": 7.0, "calypso": 7.5,
    "mariachi": 8.5, "corridos_tumbados": 8.0, "bossa": 8.0, "samba": 8.0,
    "forro": 8.0, "tango": 8.5, "fado": 9.0, "flamenco": 8.5,
    "rebetiko": 8.5, "morna": 8.5,
    # -- african / diaspora (live, dynamic) --
    "afrobeat": 7.0, "highlife": 7.5, "soukous": 7.0, "ndombolo": 7.0,
    "juju": 7.5, "fuji": 7.5, "benga": 7.5, "chimurenga": 7.5,
    "mbaqanga": 7.5, "sega": 7.0, "maloya": 8.0, "gnawa": 8.5, "chaabi": 8.0,
    "rai": 7.0, "dabke": 7.0, "khaleeji": 7.5, "arabesk": 7.5, "gamelan": 9.0,
    "dangdut": 7.0, "amapiano": 7.0, "balearic": 7.5,
    # -- south asian / raga (very dynamic acoustic) --
    "carnatic": 10.0, "hindustani": 10.0, "qawwali": 9.5, "bhangra": 7.0,
    "bollywood_filmi": 7.5, "luk_thung": 7.5, "mor_lam": 7.5,
    # -- jazz / big-band / klezmer (live horns, high crest) --
    "jazz": 9.0, "bebop": 9.0, "bop": 9.0, "swing_bigband": 8.5,
    "bigband": 8.5, "klezmer": 8.5, "balkan_brass": 8.5,
    # -- ambient / drone / downtempo (spacious, wide dynamics) --
    "ambient": 10.0, "drone": 10.0, "downtempo": 8.5, "dungeon_synth": 9.0,
    "berlin_school": 9.0, "psybient": 9.5, "psychill": 9.0,
    # -- orchestral / cinematic / classical (the widest crest) --
    "classical": 12.0, "orchestral": 11.0, "cinematic": 11.0,
}
DEFAULT_FLOOR = 6.0
SEED_SRC = "seed:published-practice/D3-pending"


def seed_floor(genre):
    """Longest-substring match against the seed table (None if no match)."""
    g = (genre or "").lower().replace(" ", "_")
    best = None
    for key, v in SEED_PSR_FLOORS.items():
        if key in g and (best is None or len(key) > best[0]):
            best = (len(key), v)
    return best[1] if best else None


def _kg():
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import kg as kgmod
        return kgmod, kgmod.KG()
    except Exception:
        return None, None


def floor_for_genre(genre, kg=None):
    """(floor, source). Graph-intelligent: direct floor -> parent (SUBGENRE_OF)
    inheritance -> seed -> default. `kg` may be a live KG() to reuse a connection."""
    g = (genre or "").lower().replace(" ", "_")
    kgmod = None
    if g:
        try:
            if kg is None:
                kgmod, kg = _kg()
            else:
                import kg as kgmod
            if kg is not None:
                # 1. direct: genre -> TARGETS -> MixTarget.psr_floor
                rows = kg.q("MATCH (gg:Genre {name: '%s'})-[:TARGETS]->(m:MixTarget) "
                            "WHERE m.psr_floor IS NOT NULL "
                            "RETURN m.psr_floor, m.psr_floor_source" % kgmod.esc(g))
                if not rows:
                    rows = kg.q("MATCH (m:MixTarget {name: '%s_mix'}) "
                                "WHERE m.psr_floor IS NOT NULL "
                                "RETURN m.psr_floor, m.psr_floor_source" % kgmod.esc(g))
                if rows:
                    return float(rows[0][0]), (rows[0][1] or "kg")
                # 2. inheritance: subgenre -> parent's floor
                rows = kg.q("MATCH (gg:Genre {name: '%s'})-[:SUBGENRE_OF]->(p:Genre)"
                            "-[:TARGETS]->(m:MixTarget) WHERE m.psr_floor IS NOT NULL "
                            "RETURN m.psr_floor, p.name" % kgmod.esc(g))
                if rows:
                    return float(rows[0][0]), f"kg:inherited<-{rows[0][1]}"
        except Exception:
            pass
    v = seed_floor(g)
    if v is not None:
        return v, SEED_SRC
    return DEFAULT_FLOOR, "seed-default/D3-pending"


def resolve_genre(song):
    """A song dict -> its genre string. meta.genre | genre | genre_pref | ''."""
    if not isinstance(song, dict):
        return ""
    meta = song.get("meta") or {}
    return (song.get("genre") or meta.get("genre") or meta.get("genre_pref")
            or song.get("genre_pref") or "").strip()


def floor_for_song(song, kg=None):
    """(floor, source, genre) — the per-song intelligent resolve (E6)."""
    g = resolve_genre(song)
    floor, src = floor_for_genre(g, kg)
    return floor, src, g


if __name__ == "__main__":
    import json
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        song = json.load(open(sys.argv[1]))
        print(json.dumps(dict(zip(("floor", "source", "genre"),
                                  floor_for_song(song))), indent=1))
    else:
        g = sys.argv[1] if len(sys.argv) > 1 else "funk"
        f, s = floor_for_genre(g)
        print(json.dumps({"genre": g, "floor": f, "source": s}, indent=1))
