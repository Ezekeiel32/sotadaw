#!/usr/bin/env python3
"""Taste wave 1 (§7.5, Chezy 'DO!' 2026-07-07): research-grounded FEEL + HARMONY
curation — only claims that are documented production practice, never guesses.

A) HAS_GROOVE: 7 new genre->groove links using the 6 REAL learned grooves.
   Deliberately NOT linked (left for real ears, not stretched provenance):
   amapiano (its log-drum shuffle is its own feel, not 2-step), soul/rnb
   (mostly straight backbeat; dilla-drag only in the neo lane), funk/boogie/
   disco (played straight-16 pocket, not MPC swing), g-funk (straight grid).

B) harmony_ext prop on 9 genres whose extended-chord practice is documented —
   consumed by skill_compiler (emits a Harmony hard-line) so the agent FEELS it.

Idempotent (MERGE semantics via kg.link / upsert). Provenance on every write.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = "curated:claude/2026-07-07 (taste wave 1 — documented feel+harmony practice)"

# genre -> (groove, the documented claim carried as provenance)
GROOVES = {
    "jazz":       ("jazz_swing", "swing subdivision IS jazz's defining feel (the root genre was unlinked while its subgenres were)"),
    "gospel":     ("jazz_swing", "gospel shuffle/12-8 triplet feel — standard gospel drumming practice"),
    "blues":      ("jazz_swing", "the blues shuffle = swung triplet subdivision, foundational to the form"),
    "neo_soul":   ("dilla",      "D'Angelo's Voodoo drag/drunk feel — THE documented dilla-feel record lineage"),
    "bassline":   ("ukg_shuffle", "bassline/niche = 4x4 UK garage descendant, shuffled hat grammar"),
    "uk_funky":   ("ukg_shuffle", "UK funky's shuffled, syncopated percussion sits in the UKG lineage"),
    "moombahton": ("dembow_lilt", "moombahton = dembow/reggaeton slowed to ~108 (Dave Nada origin), same lilt"),
}

# genre -> (harmony_ext text the skill emits, documented grounding)
HARMONY = {
    "jazz":      "7ths are the floor — voice 7th/9th/13th extensions; plain triads read as wrong",
    "neo_soul":  "7ths/9ths with added 2nds/4ths and cluster voicings (the Scott/Glasper keyboard grammar)",
    "gospel":    "7ths/9ths plus passing diminished chords between diatonic steps",
    "rnb":       "min7/maj7 and 9th voicings are the default color, not the exception",
    "soul":      "min7/maj7 voicings on keys and horn pads",
    "funk":      "dominant 9th vamps — the James Brown/Nile one-chord E9 signature",
    "house":     "min7/9th piano and organ stabs (the M1-piano lineage voicing)",
    "disco":     "maj7/min7 string and rhodes beds under straight-16 rhythm",
    "bossanova": "maj7/9 and altered dominants — the Jobim/Gilberto harmony floor",
}


def main():
    kg = KG()
    names = {r[0] for r in kg.q("MATCH (g:Genre) RETURN g.name")}
    grooves = {r[0] for r in kg.q("MATCH (gr:Groove) RETURN gr.name")}
    linked, skipped = 0, []
    for g, (grv, why) in GROOVES.items():
        if g not in names or grv not in grooves:
            skipped.append(g)
            continue
        kg.link("Genre", g, "HAS_GROOVE", "Groove", grv)
        linked += 1
        print(f"  groove: {g} -> {grv} ({why[:60]}...)")
    setp = 0
    for g, text in HARMONY.items():
        if g not in names:
            skipped.append(g)
            continue
        kg.q(f"MATCH (g:Genre {{name: '{esc(g)}'}}) "
             f"SET g.harmony_ext = '{esc(text)}', g.harmony_prov = '{esc(PROV)}'")
        setp += 1
        print(f"  harmony: {g} — {text[:60]}...")
    print(f"taste wave 1: {linked} groove links, {setp} harmony props"
          + (f", skipped (absent): {skipped}" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
