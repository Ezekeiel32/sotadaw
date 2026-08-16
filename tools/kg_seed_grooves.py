#!/usr/bin/env python3
"""THE GROOVE ATLAS (2026-07-09): genre -> groove for the whole catalog.

Grooves are the identity organ — 12 genres swung from note 1 while 190 played
quantized-straight. This wave maps every executable genre to a curated groove
archetype (tools/groove.py GROOVES = the profile truth; this file = the edge
truth). ADDITIVE-ONLY: genres that already carry a HAS_GROOVE edge keep their
curation (boombap's dual dilla/boombap_56, amapiano's own measured log).

NONE-mapped genres are silence ON PURPOSE (machine-precision, rubato, or
non-4/4 idioms a 16-slot template would falsify): ambient, berlin_school
(sequencer precision IS the aesthetic), flamenco/maloya/sega (compas / ternary
meters), breakcore/dariacore (deliberate mangle), minimal_techno, black metal.

Idempotent; provenance on every node. Run: .venv/bin/python tools/kg_seed_grooves.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG
import groove as groove_mod

# genre -> groove archetype. Musical grounding per family, one line each:
#   house family 56% shuffle · trap = the grid itself · drill's slippery 3rd-16th
#   funk leans forward w/ ghosts · reggae lags behind · afro anticipates the a's
#   latin drives a hair ahead · dnb rolls tight · techno/EBM = warehouse pulse
#   phonk/memphis/doom drag · rock/motorik pushes · jersey/NOLA/NJS hard swing
#   disco 53% lilt · blues 66% shuffle
ATLAS = {
    # --- house / garage / disco lineage ---
    "house": "house_shuffle", "deephouse": "house_shuffle",
    "chicago_house": "house_shuffle", "tech_house": "house_shuffle",
    "french_house": "house_shuffle", "acid_house": "house_shuffle",
    "detroit_techno": "house_shuffle",     # the Metroplex hat lean — Detroit swings
    "kwaito": "house_shuffle", "ghettotech": "house_shuffle",
    "disco": "disco_roll", "italo_disco": "disco_roll", "boogie": "disco_roll",
    "citypop": "disco_roll", "future_funk": "disco_roll", "balearic": "disco_roll",
    "grime": "ukg_shuffle",                # UKG descendant — the hats still skip
    "bassline": "ukg_shuffle",
    # --- trap / drill / plugg grid ---
    "trap": "trap_grid", "latin_trap": "trap_grid", "crunk": "trap_grid",
    "rage": "trap_grid", "plugg": "trap_grid", "pluggnb": "trap_grid",
    "hyperpop": "trap_grid", "digicore": "trap_grid", "sigilkore": "trap_grid",
    "future_bass": "trap_grid", "hardwave": "trap_grid", "wave": "trap_grid",
    "kpop": "trap_grid", "footwork": "trap_grid", "automotivo": "trap_grid",
    "drill": "drill_slip", "sexy_drill": "drill_slip",
    # --- funk / soul lineage ---
    "funk": "funk_pocket", "gfunk": "funk_pocket", "soul": "funk_pocket",
    "afrobeat": "funk_pocket",             # Tony Allen's broken-funk 16ths
    "jazzfusion": "funk_pocket", "breaks": "funk_pocket", "big_beat": "funk_pocket",
    "motown": "rock_drive",                # the pushed tambourine 4s
    # --- reggae / dub lean ---
    "reggae": "reggae_lean", "rocksteady": "reggae_lean", "dub": "reggae_lean",
    # --- afro / caribbean anticipation ---
    "afrobeats": "afro_lilt", "afroswing": "afro_lilt", "afro_house": "afro_lilt",
    "highlife": "afro_lilt", "soukous": "afro_lilt", "ndombolo": "afro_lilt",
    "juju": "afro_lilt", "fuji": "afro_lilt", "benga": "afro_lilt",
    "chimurenga": "afro_lilt", "mbaqanga": "afro_lilt", "kuduro": "afro_lilt",
    "coupe_decale": "afro_lilt", "champeta": "afro_lilt", "zouk": "afro_lilt",
    "3step": "amapiano_log",               # the SA 3-step rides the log lilt
    # --- latin forward drive ---
    "salsa": "latin_drive", "samba": "latin_drive", "cumbia": "latin_drive",
    "merengue": "latin_drive", "bachata": "latin_drive", "forro": "latin_drive",
    "calypso": "latin_drive", "soca": "latin_drive", "kompa": "latin_drive",
    "baile_funk": "dembow_lilt",           # tamborzao is dembow-family
    # --- jungle / dnb roll ---
    "dnb": "dnb_roll", "jungle": "dnb_roll", "neurofunk": "dnb_roll",
    "breakbeat_hardcore": "dnb_roll",
    # --- machine pulse (techno and its children) ---
    "techno": "techno_drive", "hard_techno": "techno_drive",
    "melodic_techno": "techno_drive", "dub_techno": "techno_drive",
    "trance": "techno_drive", "progressive_house": "techno_drive",
    "bigroom": "techno_drive", "hardstyle": "techno_drive",
    "gabber": "techno_drive", "happy_hardcore": "techno_drive",
    "eurodance": "techno_drive", "eurobeat": "techno_drive",
    "nightcore": "techno_drive", "hi_nrg": "techno_drive",
    "industrial": "techno_drive", "ebm": "techno_drive",
    "electro": "techno_drive", "miami_bass": "techno_drive",
    "freestyle": "techno_drive", "singeli": "techno_drive",
    "synthpop": "techno_drive", "synthwave": "techno_drive",
    "darksynth": "techno_drive",
    # --- the drag (halftime / memphis / doom) ---
    "phonk": "halftime_drag", "driftphonk": "halftime_drag",
    "memphis_rap": "halftime_drag", "dubstep": "halftime_drag",
    # lineage children born generating 2026-07-17 (kg_seed_lineage_archetypes
    # to fixpoint gave the whole 808 tree its ancestors' grids) — considered
    # HERE with the lineage feel until each gets its own curation:
    "memphis_phonk": "halftime_drag", "chicago_drill": "trap_grid",
    "driftphonk": "halftime_drag", "brazilian_phonk": "halftime_drag",
    "house_phonk": "halftime_drag",
    "uk_drill": "trap_grid", "ny_drill": "trap_grid",
    "sample_drill": "trap_grid", "afro_drill": "trap_grid",
    "vaporwave": "halftime_drag", "witch_house": "halftime_drag",
    "doom_metal": "halftime_drag", "stoner_rock": "halftime_drag",
    "downtempo": "dilla",                  # the lazy drag family
    # W126 (Chezy's genres): psybient leans its sparse hats like dub —
    # the heartbeat pulse breathes late; psychill drags with the
    # downtempo family (the drift IS a lazy pocket)
    "psybient": "reggae_lean",
    "psychill": "dilla",
    "rnb": "bounce_swing",                 # new-jack lineage swung 16ths
    # --- the push (rock engine) ---
    "rock": "rock_drive", "punk": "rock_drive", "post_punk": "rock_drive",
    "grunge": "rock_drive", "indie_rock": "rock_drive", "surf_rock": "rock_drive",
    "metal": "rock_drive", "metalcore": "rock_drive", "midwest_emo": "rock_drive",
    "krautrock": "rock_drive",             # motorik = insistent hair-ahead 8ths
    "country": "rock_drive", "bluegrass": "rock_drive",
    # --- hard 16th swing (jersey / NOLA / NJS) ---
    "jerseyclub": "bounce_swing", "jersey_drill": "bounce_swing",
    "baltimore_club": "bounce_swing", "bounce": "bounce_swing",
    "new_jack_swing": "bounce_swing",
    # --- shuffle / swing ---
    "blues": "shuffle_blues",              # additive no-op if jazz_swing edge stays
    "doo_wop": "shuffle_blues", "bhangra": "shuffle_blues",   # the chaal gallop
    "swing_bigband": "jazz_swing",
}

# Explicit NONE (documented reason > silent gap). Not seeded; listed so the
# battery can prove every executable genre was CONSIDERED, not missed.
STRAIGHT_ON_PURPOSE = {
    "ambient", "drone", "berlin_school", "dungeon_synth", "orchestral_cinematic",
    "post_rock", "post_metal", "shoegaze", "idm", "glitchcore", "breakcore",
    "dariacore", "minimal_techno", "black_metal", "death_metal", "djent",
    "math_rock", "jpop", "pop", "chillwave",
    # gqom LEFT this set 2026-07-12 (wave49): dr28's genre marker + the hat-
    # slot truth (gqom hats live ON the triplet thirds) outweigh the earlier
    # straight call — gqom_triplet pulls e/a slots toward 1/3 positions while
    # the broken KICK CELL stays exact (the atlas anchor law).
    # non-4/4 or non-grid idioms a 16-slot 4/4 template would falsify:
    "flamenco", "maloya", "sega", "gnawa", "celtic", "klezmer", "tango",
    "fado", "morna", "rebetiko", "qawwali", "carnatic", "hindustani",
    "khaleeji", "dabke", "chaabi", "rai", "arabesk", "balkan_brass",
    "mariachi", "corridos_tumbados", "bollywood_filmi", "dangdut", "luk_thung",
    "mor_lam", "bossanova", "ska", "gamelan", "free_jazz",
    # already-curated genres keep their existing edges (additive-only law):
    "boombap", "hiphop", "lofi", "triphop", "neo_soul", "amapiano",
    "ukgarage", "speed_garage", "future_garage", "uk_funky", "psytrance",
    "goa", "dembow", "reggaeton", "dancehall", "moombahton", "jazz", "bebop",
    "hard_bop", "modal_jazz", "spiritual_jazz", "ethio_jazz", "gospel",
}


def seed(verbose=True):
    kg = KG()
    store = groove_mod.store()             # merges the new GROOVES into grooves.json
    missing = sorted({g for g in ATLAS.values() if g not in store})
    if missing:
        raise SystemExit(f"ATLAS names grooves not in the store: {missing}")
    have = {r[0] for r in kg.q("MATCH (g:Genre)-[:HAS_GROOVE]->(:Groove) RETURN DISTINCT g.name")}
    added, kept = 0, 0
    for gname in sorted(set(ATLAS.values())):
        kg.upsert("Groove", gname, store[gname]["prov"])
    for genre, gname in sorted(ATLAS.items()):
        if genre in have:
            kept += 1                      # additive-only: existing curation wins
            continue
        kg.link("Genre", genre, "HAS_GROOVE", "Groove", gname)
        added += 1
    total = kg.q("MATCH (g:Genre)-[:HAS_GROOVE]->(:Groove) RETURN count(DISTINCT g)")[0][0]
    if verbose:
        print(f"GROOVE ATLAS: +{added} genres linked ({kept} kept existing curation), "
              f"{total} genres now carry a groove")
    return added, kept, total


if __name__ == "__main__":
    seed()
