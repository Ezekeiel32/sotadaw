#!/usr/bin/env python3
"""Wave 33: THE CAMPAIGN'S OWN LAWS — this week's battery-proven techniques
enter the graph (the knowledge IS the documentation; docstrings don't compile,
the KG does).

Every node's provenance = the battery that earned it (2026-07-05 firings 24-38),
plus literature grounding where the law has a name (parsimonious voice leading:
neo-Riemannian theory via MTO/OMT2).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, "
        "912-song grammar, flip verification chain) via curated:claude (wave33)")

TECHNIQUES = {
    "acapella_bridge": (
        "the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck "
        "cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) "
        "over the incoming deck and fades by bar 8; find the phrase by probing "
        "the final ~24 played bars for the loudest-voiced 8-bar window — a DJ "
        "cuts where the VOICE ends, not where the file does [battery: solo render "
        "-26dB voice exactly across the swap; voiceless tails fall back honestly]",
        0.7, ["house", "techno", "dnb", "hiphop"]),
    "structure_inheritance": (
        "a remix/companion inherits the SOURCE'S section skeleton: its sections "
        "become the arrangement form at their real durations — same bar count, "
        "same energy arc [battery: Foote on the RENDER, blind to the JSON, found "
        "5/6 joints within 3 bars of the source's]",
        0.75, ["hiphop", "house", "dnb"]),
    "parsimonious_retune": (
        "reharmonization moves each voice AS LITTLE AS POSSIBLE: chord tones map "
        "role-to-role (root->root, third->third quality-aware) taking the nearest "
        "octave; tensions keep contour via root delta — this is parsimonious "
        "voice leading (neo-Riemannian theory; OMT2 has the chapter) applied as "
        "an edit operation [battery: mean 3.0 semitones, re-vote reads the exact "
        "target]",
        0.8, ["rnb", "gospel", "citypop"]),
    "verse_position_law": (
        "pop physiology from 912 human structures: verses live EARLY and die by "
        "the final third (1221/773/185); bridges never open a song (11/701 first "
        "third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros "
        "420/421 final-third — place sections where the population puts them "
        "[Harmonix label grammar, MIT data, mined locally]",
        0.7, ["synthpop", "kpop", "rnb", "indie_rock"]),
    "chord_lane_vote": (
        "when you OWN the symbols, vote harmony from notes, never from audio: "
        "bar-wise duration x velocity weights, bass witnesses x2.5, b7 read for "
        "dominant color; muted transcription sketches still vote on imports "
        "[battery: 9/12 exact incl. 7s on 12-bar blues where the audio HMM "
        "scored 2/12; 4/4 on triads where audio heard nothing]",
        0.65, ["lofi", "boombap", "hiphop"]),
    "groove_transfer": (
        "a record's timing DNA (onset phase vs grid) extracts as a named groove "
        "and applies to NEW material at ~0.9 — on-grid notes move, off-grid feel "
        "is preserved; apply to hats/snare, keep kick straight [battery: 412/429 "
        "onsets learned from a real record; 80 notes moved on the flip]",
        0.75, ["boombap", "hiphop", "ukgarage"]),
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
    print(f"wave33 campaign laws: {added} techniques, {linked} links"
          + (f"; skipped: {sorted(set(skipped))}" if skipped else ""))
