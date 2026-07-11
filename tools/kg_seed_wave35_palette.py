#!/usr/bin/env python3
"""WAVE 35 — PRESET-RAIL PALETTES for flagship genres (CC4-I2, firing 117).

Eight genres already ride vst3 color voices (house/synthwave/electro/...); the
other flagships were Faust-only while 4,366 commercial-grade sounds idled.
This wave sets the COLOR voice on one recipe per flagship to the preset rail
(plugin-level, the established 'vst3:<name>' convention loop_gen + the engine
already resolve; preset-blob selection per genre = v2).

Idempotent: only fills voices that are NULL; re-running is a no-op.
Provenance: rail = library.json vst_presets (TAL 256 / Odin2 260 params-dict
sounds, verified preset_battery); mapping chosen by genre character —
Odin2 (darker, unison) for techno-family, TAL-NoiseMaker (brighter VA) for
the bounce/melodic family.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from kg import KG, esc

WAVE = [
    ("techno",          "techno_stab",    "vst3:Odin2"),
    ("melodic_techno",  None,             "vst3:Odin2"),
    ("dnb",             None,             "vst3:Odin2"),
    ("trap",            None,             "vst3:TAL-NoiseMaker"),
    ("phonk",           None,             "vst3:TAL-NoiseMaker"),
    ("deephouse",       None,             "vst3:TAL-NoiseMaker"),
]


def main():
    kg = KG()
    done = 0
    for genre, recipe, voice in WAVE:
        if recipe:
            q = (f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                 f"(r:SoundRecipe {{name:'{esc(recipe)}'}}) WHERE r.voice IS NULL "
                 f"SET r.voice='{esc(voice)}' RETURN r.name")
        else:   # first voiceless, non-drum recipe of the genre
            q = (f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->(r:SoundRecipe) "
                 f"WHERE r.voice IS NULL AND NOT r.name CONTAINS 'kick' "
                 f"AND NOT r.name CONTAINS 'drum' AND NOT r.name CONTAINS 'hat' "
                 f"WITH r LIMIT 1 SET r.voice='{esc(voice)}' RETURN r.name")
        rows = kg.q(q)
        if rows:
            print(f"  {genre:16} {rows[0][0]:20} -> {voice}")
            done += 1
        else:
            cur = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->(r:SoundRecipe) "
                       f"WHERE r.voice IS NOT NULL RETURN r.voice LIMIT 1")
            print(f"  {genre:16} already voiced: {cur[0][0] if cur else '??'}")
    print(f"wave35: {done} palettes set")




# ---- 35b (firing 118): the three flagships that NEEDED RECIPES, given recipes ----
# Grounding (own search, cited in stamp 118): the reese = detuned unison saws in
# phase-beat (dnb's signature; odd voice counts keep the low centered); melodic
# techno rides dark unison plucks; deep house stabs live in VA-organ territory.
# Odin2 (unison-native) carries the techno/dnb family; TAL-NoiseMaker (bright VA)
# carries the house family. Rail verified by preset_battery.
WAVE_B = [
    ("melodic_techno", "mt_dark_pluck",  "vst3:Odin2",
     "dark unison pluck color (Afterlife-lane); Odin2 unison-native"),
    ("dnb",            "dnb_reese_color","vst3:Odin2",
     "reese-family color: detuned unison saws, phase-beating (futureproof/toolroom refs)"),
    ("deephouse",      "dh_organ_stab",  "vst3:TAL-NoiseMaker",
     "VA organ-stab color (M1-organ lineage); TAL bright-VA lane"),
]

def main_b():
    kg = KG()
    prov = "wave35b 2026-07-06: preset-rail palettes; reese/pluck/stab grounding via own search (stamp 118); rail=preset_battery"
    for genre, rname, voice, desc in WAVE_B:
        kg.upsert("SoundRecipe", rname, prov, desc=desc, voice=voice)
        kg.link("Genre", genre, "CHARACTERIZED_BY", "SoundRecipe", rname)
        print(f"  {genre:16} +{rname:16} -> {voice}")
    print("wave35b: 3 recipes added")


if __name__ == "__main__":
    main()
    main_b()
