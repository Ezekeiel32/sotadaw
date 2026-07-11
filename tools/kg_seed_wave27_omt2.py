#!/usr/bin/env python3
"""Wave 27: THE CLEAN THEORY LANE OPENS — OMT2-grounded technique nodes.

First curation wave from the LICENSE_LEDGER's 'owned/licensed/first-principles'
column: Open Music Theory v2 (open textbook) chapters become Technique nodes with
chapter-cited provenance. These are the THEORY BONES under the genre skills —
phrase models, harmony devices, rhythm laws — linked only to genres that exist.
Provenance law honored: every node cites its OMT2 area.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27)"

TECHNIQUES = {
    # name: (desc, OMT2 area, weight, [genre links])
    "sentence_phrase": ("the 2+2+4 sentence: presentation (idea x2) then continuation/drive to cadence — THE build shape; EDM risers are sentences in disguise",
                        "Form: phrase models", 0.6, ["synthpop", "trance", "house"]),
    "period_phrase": ("antecedent/consequent pair: question phrase (half cadence) answered by resolution — topline call that RESOLVES the second time",
                      "Form: phrase models", 0.6, ["citypop", "synthpop"]),
    "twelve_bar_blues": ("I-I-I-I / IV-IV-I-I / V-IV-I-I with dominant-quality color everywhere; turnaround bar 12 pulls back to the top",
                         "Popular music: blues harmony", 0.9, ["blues"]),
    "plagal_shuttle": ("I<->IV oscillation (the 'amen' motion) — harmonic warmth without dominant tension; loops forever without demanding a cadence",
                       "Popular music: harmonic schemas", 0.65, ["gospel", "indie_rock", "soul"]),
    "mode_mixture": ("borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker",
                     "Chromaticism: mode mixture", 0.7, ["citypop", "rnb", "soul"]),
    "secondary_dominant": ("V/x tonicization: any diatonic chord gets its own dominant for one beat of borrowed gravity — gospel/jazz motion fuel",
                           "Chromaticism: applied chords", 0.7, ["gospel", "swing_bigband", "bossa_nova"]),
    "ii_V_I_turnaround": ("the ii-V-I engine with shell voicings (3rds+7ths): jazz's gravitational cell; chain them around the cycle for motion",
                          "Jazz: harmony fundamentals", 0.85, ["swing_bigband", "bossa_nova", "lofi"]),
    "pedal_point": ("static bass under moving harmony — tension by refusal; the dominant pedal is the classic pre-drop device",
                    "Diatonic harmony: pedal/prolongation", 0.6, ["trance", "techno", "gospel"]),
    "hemiola_3_2": ("3:2 cross-rhythm — two bars of 3 heard as three bars of 2 (or within-bar 3-against-2); the lift beneath afro-latin grooves",
                    "Rhythm & meter: hemiola", 0.7, ["afrobeat", "salsa", "baile_funk"]),
    "call_and_response": ("antiphony: a phrase states, a second voice answers in the gap — the gap IS the invitation (our choir ad-lib lane implements this)",
                          "Popular music: texture & form", 0.8, ["gospel", "funk", "afrobeat", "blues"]),
    "aaba_form": ("32-bar AABA: statement, restatement, bridge ('the middle eight'), return — the standard's skeleton",
                  "Form: popular song forms", 0.7, ["swing_bigband", "citypop"]),
    "picardy_third": ("minor movement ends on the parallel MAJOR tonic — the sunrise ending; cheap to play, expensive-sounding",
                      "Chromaticism: closing devices", 0.4, ["gospel"]),
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
    print(f"wave27 OMT2: {added} theory techniques upserted, {linked} genre links"
          + (f"; skipped absent genres: {sorted(set(s.split('->')[0] for s in skipped))}" if skipped else ""))
