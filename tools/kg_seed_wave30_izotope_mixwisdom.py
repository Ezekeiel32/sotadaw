#!/usr/bin/env python3
"""Wave 30: THE MIX-WISDOM LANE — iZotope Learn articles read at source, curated
into fix-grammar Technique nodes.

Sources (fetched at source this firing, 2026-07-05):
  [MASK] izotope.com/en/learn/what-is-frequency-masking.html
  [EQ16] izotope.com/en/learn/16-common-eq-mistakes-mixing-engineers-make
  [PARA] izotope.com/en/learn/parallel-compression-mistakes.html
  [VOX]  izotope.com/en/learn/mixing-vocals-how-to-create-space-for-vox (search-verified)

The lane's point: stem_callouts already FINDS collisions (per-section pairs);
these nodes are the FIX GRAMMAR — what move, at what precision, with what
numbers. Genre edges only where the move is idiomatic; all names pre-verified
against the graph (wave-29 lesson).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / "
        "parallel-compression-mistakes / mixing-vocals-space), read at source, "
        "via curated:claude/2026-07-05 (wave30 mix-wisdom)")

TECHNIQUES = {
    "complementary_eq_unmask": (
        "two voices collide in one band (kick/bass is the classic): BOOST that band "
        "slightly in the priority voice and CUT the same band in the other — one "
        "collision, two opposite small moves; stem_callouts finds the pair, this is "
        "the fix [MASK]",
        0.8, ["house", "trap", "techno", "dnb"]),
    "unmask_escalation_ladder": (
        "unmask in escalating precision, stop at the first rung that works: 1) static "
        "complementary EQ; 2) wideband sidechain duck (whole voice, when trigger "
        "plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the "
        "trigger hits) — never pay more transparency than the collision costs [MASK]",
        0.75, ["house", "trap", "phonk", "amapiano"]),
    "sidechain_unmask_bass": (
        "sustained bass masks a percussive kick because the ear locks onto the "
        "constant voice — duck the bass only when the kick hits and both survive; "
        "the FX-side complement to rolling_offbeat_bass (where the ARRANGEMENT is "
        "the sidechain: bass written in the kick's holes needs no ducking) [MASK]",
        0.75, ["house", "trance", "synthpop"]),
    "mud_zone_200_400": (
        "most instruments carry energy at 200-400 Hz, so masking concentrates there "
        "(the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on "
        "every track: pick one or two donor tracks to give the space; scooping "
        "everything (per-track smiley EQ) hollows the mix in context [EQ16]",
        0.8, ["lofi", "rock", "funk", "soul", "hiphop"]),
    "trust_innate_brightness": (
        "don't buy top-end per track: a slight Baxandall high shelf on ONE important "
        "bus, leave the rest alone — material is usually brighter than fear suggests; "
        "per-track brightening stacks into harshness [EQ16]",
        0.5, ["citypop", "ambient"]),
    "parallel_thwack_attack": (
        "on the parallel crush bus the ATTACK chooses the transient's character: "
        "25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap "
        "— then blend under the dry until it's felt not heard [PARA]",
        0.7, ["trap", "phonk", "boombap"]),
    "parallel_density_vs_emphasis": (
        "two parallel-comp intents, two clocks: fast attack + slow release fills "
        "DENSITY under the dry transients; moderate attack + short release EMPHASIZES "
        "the transients — decide which the dry bus lacks before touching the knobs "
        "[PARA]",
        0.65, ["hiphop", "dnb", "boombap"]),
    "parallel_detail_pump": (
        "high ratio + fast attack AND release, blended low under dry: the original "
        "transients stay in charge while low-level detail and tone pump upward — "
        "dynamic-range control that never squashes the hit [PARA]",
        0.6, ["funk", "soul", "rock"]),
    "vocal_space_static_cut": (
        "make room for a vocal with a STATIC 1-2 dB cut on the instrumental at the "
        "conflict band — start tiny, in context; the instrumental barely changes "
        "solo'd but the vocal seats [VOX]",
        0.6, ["rnb", "synthpop", "citypop"]),
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
    print(f"wave30 mix-wisdom: {added} techniques upserted, {linked} genre links"
          + (f"; skipped absent genres: {sorted(set(skipped))}" if skipped else ""))
