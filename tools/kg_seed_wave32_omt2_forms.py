#!/usr/bin/env python3
"""Wave 32 (shipped after 33 — the ledger knows): OMT2 form-family laws.

Source read at source 2026-07-05: OMT2 'AABA Form and Strophic Form' chapter
(CC BY-SA). Completes the OMT2 arc (waves 27/29/31): the FORM FAMILIES beyond
wave 27's phrase models — what makes a song strophic vs AABA, why bridges
exist, and what never counts toward form identity.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) "
        "via curated:claude/2026-07-05 (wave32 form families)")

TECHNIQUES = {
    "strophic_form": (
        "AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry "
        "'School Day'); the home form of blues, early hip hop, early rock'n'roll "
        "— verse-chorus displaced it after ~1970. Instrumental passes over the "
        "same pattern (solos) are still strophes",
        0.65, ["blues", "boombap", "rock"]),
    "refrain_hook": (
        "a recurring lyric+melodic motive INSIDE the strophe — usually carrying "
        "the TITLE — is the refrain: the hook mechanism of strophic songs before "
        "choruses existed ('Faded Love'); write it once, let every strophe land it",
        0.6, ["blues", "rock", "soul"]),
    "bridge_contrast_law": (
        "AABA's B section exists to DEPART (new harmony, new melodic register), "
        "which is what makes the final A's return feel amplified — write the "
        "bridge as contrast, never as variation; 32-bar proportions = 8 bars per "
        "section in the Golden-Age prototype",
        0.7, ["citypop", "swing_bigband", "soul"]),
    "auxiliary_sections_law": (
        "intros/outros/interludes/codas are AUXILIARY: they never count toward a "
        "form's identity (a strophic song with an intro is still AAA) — judge "
        "form by the MAIN-section pattern only; our labeler/arranger semantics "
        "follow this",
        0.55, ["synthpop", "house"]),
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
    print(f"wave32 form families: {added} techniques, {linked} links"
          + (f"; skipped: {sorted(set(skipped))}" if skipped else ""))
