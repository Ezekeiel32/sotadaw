#!/usr/bin/env python3
"""Wave 52: THE BREATH FLOORS (2026-07-12, ledger 162 'loudness tail').
The W41 breath guard reads MixTarget.lra_floor but EVERY target carried
None — so every genre ran the universal 3.2 LU default. Right for club
music; a lie for the dynamics-defined cultures (the W40 verdict pass
measured gospel squashed 4.2 -> 3.0 LU by a lift the guard waved through).

Floors are STOP-LIFTING lines, not targets: set ~1-2 LU under the culture's
typical published LRA so honest takes still lift and squashy lifts stop.
Club/pop/trap genres stay UNSET on purpose (3.2 default = correct).

Provenance: published loudness practice (EBU R128 LRA surveys; streaming-
era mastering guides) — same evidence class as the E12 psr_floor seed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = "curated:claude/2026-07-12 (wave52 breath floors: ledger 162 loudness tail)"

LRA_FLOORS = {
    # concert / cinematic
    "orchestral_cinematic": 7.0,
    # jazz family
    "jazz": 6.0, "modal_jazz": 6.0, "bebop": 6.0, "hard_bop": 6.0,
    "free_jazz": 6.0, "spiritual_jazz": 6.0, "ethio_jazz": 5.5, "jazzfusion": 5.0,
    # acoustic song cultures
    "bossanova": 5.5, "fado": 5.5, "morna": 5.5, "flamenco": 5.5,
    "tango": 5.5, "bluegrass": 5.0, "country": 4.5, "celtic": 5.0,
    "rebetiko": 5.0, "klezmer": 5.0, "mariachi": 5.0, "blues": 5.0,
    # eastern classical
    "carnatic": 6.5, "hindustani": 6.5, "qawwali": 6.0, "gamelan": 6.0,
    # ambient family
    "ambient": 6.0, "drone": 5.0, "psybient": 5.0, "psychill": 4.5,
    "berlin_school": 5.0, "dungeon_synth": 5.0, "krautrock": 4.5,
    # swing / soul era
    "swing_bigband": 5.0, "doo_wop": 4.5, "motown": 4.0, "soul": 4.0,
    "gospel": 4.5, "neo_soul": 4.0,
    # downtempo
    "downtempo": 4.0, "triphop": 4.0, "chillwave": 4.0, "balearic": 4.0,
    # rock dynamics (quiet-loud cultures)
    "post_rock": 5.0, "math_rock": 4.5, "midwest_emo": 4.5,
    "shoegaze": 4.0, "grunge": 4.0, "indie_rock": 4.0, "surf_rock": 4.0,
    "stoner_rock": 4.0, "post_punk": 4.0, "rock": 4.0,
    # jamaica (the drop IS the music)
    "dub": 4.5, "rocksteady": 4.5, "reggae": 4.0, "ska": 4.0,
}

if __name__ == "__main__":
    kg = KG()
    done, miss = [], []
    for g, floor in LRA_FLOORS.items():
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(g)}'}})-[:TARGETS]->(m:MixTarget) "
                    "RETURN id(m), m.lra_floor")
        if not rows:
            miss.append(g)
            continue
        mid, cur = rows[0]
        kg.q(f"MATCH (m:MixTarget) WHERE id(m) = {int(mid)} "
             f"SET m.lra_floor = {float(floor)}, "
             f"m.provenance = m.provenance + ' | {esc(PROV)}'")
        done.append(f"{g}={floor}")
    print(f"wave52: {len(done)} breath floors seeded")
    print("  " + " ".join(done))
    if miss:
        print(f"  MISSING TARGETS: {miss}")
