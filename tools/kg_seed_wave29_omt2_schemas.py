#!/usr/bin/env python3
"""Wave 29: THE SCHEMA VOCABULARY — OMT2's named four-chord + blues schemas,
with the variation LAWS that generate progressions mechanically.

Source (fetched + read this firing): OMT2 "Four-Chord Schemas" and "Blues
Harmony" (Bryn Hughes & Megan Lavengood, Open Music Theory v2, CC BY-SA).
The chapters' core insight the graph lacked: I/IV/V/vi are pop's common STOCK —
a schema is the ORDER (wave 28's axis detector set-matches degrees; identity
lives in the cycle). Rotation and functional substitution are the variation
laws: 3 schemas x 4 rotations x substitutions = a progression FIELD, each
point provenance-cited. Blues refinements sharpen wave 27's coarse
twelve_bar_blues into playable variant laws.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open "
        "Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via "
        "curated:claude/2026-07-05 (wave29)")

TECHNIQUES = {
    # name: (desc, OMT2 area, weight, [genre links — linked only if genre exists])
    "doo_wop_schema": (
        "I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; "
        "variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi "
        "('Viva la Vida' enters the cycle on IV)",
        "Popular music: four-chord schemas", 0.75,
        ["soul", "rnb", "citypop", "synthpop"]),
    "singer_songwriter_schema": (
        "vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine "
        "since the mid-90s; relative-minor reading i-VI-III-VII is equally valid",
        "Popular music: four-chord schemas", 0.85,
        ["synthpop", "house", "indie_rock", "rnb", "trance"]),
    "tonal_ambiguity_dual_tonic": (
        "the singer/songwriter schema carries NO authentic cadence (only plagal IV-I "
        "or stepwise VII-i), so one loop reads as major AND relative minor at once "
        "(the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — "
        "write one progression, recolor it dark/bright per section via bass root "
        "emphasis + melody tones, zero modulation cost",
        "Popular music: four-chord schemas", 0.7,
        ["synthpop", "trance", "house", "rnb"]),
    "hopscotch_schema": (
        "IV-V-vi-I: the post-2010 pop schema (OMT2's newest named cycle); minor "
        "reading VI-VII-i-III; variation VI-V-i-III (V subs VII in minor)",
        "Popular music: four-chord schemas", 0.6,
        ["kpop", "future_bass", "synthpop"]),
    "schema_rotation": (
        "cyclical schemas keep their identity started ANYWHERE in the cycle "
        "(rotation) — one schema = four progressions; choose the rotation whose "
        "first chord is the section's mood anchor (IV-start = lift, vi-start = ache)",
        "Popular music: four-chord schemas (variation laws)", 0.65,
        ["synthpop", "house", "citypop"]),
    "functional_substitution_ii_IV": (
        "ii and IV share subdominant function and swap freely inside any schema "
        "(I-vi-ii-V == I-vi-IV-V, 'Hungry Heart') — voice-leading freshness with "
        "zero schema-identity cost; ii brings the stepwise bass, IV the open fifth",
        "Popular music: four-chord schemas (variation laws)", 0.55,
        ["citypop", "lofi", "rnb", "bossanova"]),
    "quick_change_blues": (
        "12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness "
        "installed at the very top of the form; the single most common blues alteration",
        "Popular music: blues harmony", 0.6,
        ["blues", "rock", "funk"]),
    "blues_turnaround": (
        "bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in "
        "the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain",
        "Popular music: blues harmony", 0.7,
        ["blues", "swing_bigband", "lofi", "rock"]),
    "sixteen_bar_blues": (
        "four 4-bar phrases — tonic stated twice, then subdominant, then dominant "
        "phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock",
        "Popular music: blues harmony", 0.45,
        ["blues", "rock"]),
    "minor_blues": (
        "i7/iv7 become minor sevenths, V STAYS dominant; the third phrase swaps "
        "V-IV-i for ii-V-i because major-V falling to minor-iv sounds anticlimactic "
        "— the sanctioned jazz handshake inside blues form",
        "Popular music: blues harmony", 0.7,
        ["blues", "soul", "lofi"]),
    "blues_dominant_color": (
        "the blues color laws in one node: ALL chords dominant sevenths and any of "
        "them can be tonic/subdominant/dominant in function; major and minor thirds "
        "coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not "
        "authentic — tonal-harmony truisms do not apply here",
        "Popular music: blues harmony", 0.75,
        ["blues", "funk", "rock", "gospel"]),
}

if __name__ == "__main__":
    kg = KG()
    added, linked, skipped = 0, 0, []
    for name, (desc, area, w, genres) in TECHNIQUES.items():
        kg.upsert("Technique", name, PROV, desc=f"{desc} [{area}]", weight=w)
        added += 1
        for g in genres:
            if kg.q(f"MATCH (g:Genre {{name: '{g}'}}) RETURN g.name"):
                kg.link("Genre", g, "USES_TECHNIQUE", "Technique", name, weight=w)
                linked += 1
            else:
                skipped.append(f"{g}->{name}")
    print(f"wave29 OMT2 schemas: {added} techniques upserted, {linked} genre links"
          + (f"; skipped absent genres: {sorted(set(s.split('->')[0] for s in skipped))}"
             if skipped else ""))
