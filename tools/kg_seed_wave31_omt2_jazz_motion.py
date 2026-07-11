#!/usr/bin/env python3
"""Wave 31: JAZZ MOTION LAWS — the OMT2 ii-V-I chapter read at source.

Source (fetched this firing, 2026-07-05): OMT2 "ii-V-I" chapter (Jazz section),
viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ (CC BY-SA). Extends wave
27's single ii_V_I_turnaround node into the operating laws: how the cell is
RECOGNIZED (quality signature), how far it BENDS (alteration tolerance), how it
TRAVELS (applied cells, unresolved ii-Vs), and the ROUTING TABLE (McClimon's
ii-V space on the circle of fifths, cited via OMT2).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, "
        "viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via "
        "curated:claude/2026-07-05 (wave31 jazz motion)")

TECHNIQUES = {
    "ii_V_quality_signature": (
        "the cell is IDENTIFIED by fifths root motion PLUS quality sequence: "
        "mi7-7-ma7 in major, half-dim7-7-mi7 in minor (V stays dominant-quality in "
        "BOTH modes) — so distinctive that an unresolved ii-V still reads as the "
        "schema; generators must keep the quality string even when reharmonizing",
        0.8, ["swing_bigband", "bossanova", "lofi", "citypop"]),
    "ii_V_alteration_tolerance": (
        "the schema survives alterations and stays recognizable: I-ma7 swaps for a "
        "6 chord ('Misty'), V goes augmented ('Prelude to a Kiss') or takes a "
        "lowered fifth ('A Night in Tunisia') — variation budget for generators: "
        "color the V freely, keep roots-by-fifth and the seventh intact",
        0.6, ["swing_bigband", "bossanova", "citypop"]),
    "applied_ii_V_cell": (
        "the WHOLE ii-V(-I) unit drops into foreign keys to tonicize any target "
        "(applied subdominant included — jazz extends applied chords beyond V); "
        "'Afternoon in Paris' chains cells through bVII then bVI before coming "
        "home; an unresolved ii-V alone still creates the pull — motion without "
        "commitment, the reharmonizer's passport",
        0.7, ["swing_bigband", "bossanova", "lofi"]),
    "ii_V_space_navigation": (
        "all possible ii-V cells arrange on the circle of fifths into one lattice "
        "(McClimon 2017 via OMT2): each key's I is preceded by its ii-V, and cells "
        "chain by fifth-steps or slide chromatically — the routing table for jazz "
        "motion; pick a distant target, walk cells to it, every hop sounds inevitable",
        0.55, ["swing_bigband", "bossanova"]),
}

if __name__ == "__main__":
    kg = KG()
    added, linked, skipped = 0, 0, []
    for name, (desc, w, genres) in TECHNIQUES.items():
        kg.upsert("Technique", name, PROV, desc=desc, weight=w)
        added += 1
        for g in genres:
            if kg.q(f"MATCH (g:Genre {{name: '{g}'}}) RETURN g.name"):
                kg.link("Genre", g, "USES_TECHNIQUE", "Technique", name, weight=w)
                linked += 1
            else:
                skipped.append(g)
    print(f"wave31 jazz motion: {added} techniques upserted, {linked} genre links"
          + (f"; skipped absent genres: {sorted(set(skipped))}" if skipped else ""))
