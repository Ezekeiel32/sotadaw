#!/usr/bin/env python3
"""Wave 36: CHORD DNA scale-out — 30 canon-unambiguous archetypes (f146).

Same grammar as wave25: grid["chords"] = [[bar, degree]] 1-based in the genre's
mode; one-chord vamps are LAW where the genre IS the vamp (techno/funk precedent).
Grounding: cumbia I-IV-V + bachata minor/V7 canon spot-checked by own search
(stamp f146 citations); Andalusian cadence, pop four-chord, jazz ii-V-I, the
J-pop royal road, 12-bar turnaround = textbook commons. Idempotent: skips
archetypes that already carry chords.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon "
        "own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons)")

C = {
    # 12-bar/turnaround + country/folk I-IV-V families
    "blues_shuffle":    [[0, 1], [1, 1], [2, 4], [3, 5]],   # 4-bar turnaround cycle
    "train_beat":       [[0, 1], [1, 4], [2, 1], [3, 5]],
    "ranchera_walk":    [[0, 1], [1, 4], [2, 5], [3, 1]],
    "punk_dbeat":       [[0, 1], [1, 4], [2, 5], [3, 5]],
    "calypso_bell":     [[0, 1], [1, 4], [2, 5], [3, 1]],
    "soca_power":       [[0, 1], [1, 4], [2, 5], [3, 4]],
    "highlife_bell":    [[0, 1], [1, 4], [2, 1], [3, 5]],
    "kompa_gong":       [[0, 1], [1, 4], [2, 5], [3, 4]],
    "cumbia_roll":      [[0, 1], [1, 4], [2, 5], [3, 1]],
    "bachata_bongo":    [[0, 1], [1, 4], [2, 1], [3, 5]],
    "tumbao_cascara":   [[0, 1], [1, 4], [2, 5], [3, 4]],   # montuno I-IV-V-IV
    # vamps that ARE the genre (one chord, by law)
    "motorik_drive":    [[0, 1]],
    "drone_minimal":    [[0, 1]],
    "minimal_skeleton": [[0, 1]],
    "gabber_four":      [[0, 1]],
    "machine_press":    [[0, 1]],
    "ebm_stomp":        [[0, 1]],
    "hardtechno_drive": [[0, 1]],
    "metal_chug":       [[0, 1]],
    "tamborzao":        [[0, 1]],
    # two-chord shuttles
    "one_drop_dub":     [[0, 1], [2, 7]],
    "proto_one_drop":   [[0, 1], [2, 7]],
    "skank_accents":    [[0, 1], [2, 7]],
    "baiao_zabumba":    [[0, 1], [2, 7]],                   # mixolydian I-bVII
    "habanera_spine":   [[0, 1], [2, 5]],
    "gfunk_bounce":     [[0, 1], [2, 4]],
    # named canonical four-chord shapes
    "rumba_palmas":     [[0, 1], [1, 7], [2, 6], [3, 5]],   # Andalusian cadence
    "pop_four":         [[0, 1], [1, 5], [2, 6], [3, 4]],   # I-V-vi-IV
    "jpop_drive":       [[0, 4], [1, 5], [2, 3], [3, 6]],   # the royal road
    "bossa_sway":       [[0, 2], [1, 5], [2, 1], [3, 6]],   # ii-V-I-vi
}

if __name__ == "__main__":
    kg = KG()
    done = skip = miss = 0
    for pname, prog in C.items():
        rows = kg.q(f"MATCH (p:PatternArchetype {{name: '{pname}'}}) RETURN p.grid")
        if not rows or not rows[0][0]:
            print(f"  {pname}: MISSING"); miss += 1; continue
        grid = json.loads(rows[0][0])
        if "chords" in grid:
            skip += 1; continue
        grid["chords"] = prog
        kg.upsert("PatternArchetype", pname, PROV, grid=json.dumps(grid))
        done += 1
    print(f"wave36: {done} seeded, {skip} already had, {miss} missing")
