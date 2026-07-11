#!/usr/bin/env python3
"""KG curation wave 4 (2026-07-03): +10 genres toward the 100-genre horizon.
grime, reggaeton, baile_funk, neurofunk, melodic_techno, deephouse, triphop,
gabber, electro, citypop — each with bpm/key props, weighted technique edges
(6 new techniques), a MixTarget, and lineage where real. Idempotent (MERGE)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03"
    NEW_TECH = {
     "eski_square_bass": "grime's eskibeat DNA: raw square-wave bass stabs (Pulse-style), icy and hollow — 140bpm, space between hits is the aggression",
     "tamborzao": "baile funk's tamborzao drum bed: syncopated 808/tom pattern under 130bpm MC chants — kick-tom dialogue, minimal melody",
     "hoover_stab": "the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs",
     "gabber_kick": "overdriven 909 kick: distorted till the tail becomes the bassline (single saturated kick = kick+bass in one), 150-190bpm",
     "electro_boogie": "Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor",
     "maj7_gloss": "citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    WAVE = {
     "grime":          dict(bpm=(138,142), key="C minor", parent="ukgarage",
                            tech=[("eski_square_bass",.95),("half_time_140",.8),("ghost_snare_drill",.5),("call_response_melody",.6),("brickwall_mastering",.7)],
                            mix=(-11,-7,"low>mid>lowmid")),
     "reggaeton":      dict(bpm=(88,98), key="A minor", parent=None,
                            tech=[("dembow_rhythm",.95),("perreo_bass",.85),("groove_dembow_lilt",.8),("vocal_chops",.5),("brickwall_mastering",.6)],
                            mix=(-10,-6,"low>lowmid>mid")),
     "baile_funk":     dict(bpm=(125,135), key="F minor", parent=None,
                            tech=[("tamborzao",.95),("memphis_chant",.5),("sparse_kick",.6),("vocal_chops",.7),("brickwall_mastering",.6)],
                            mix=(-9,-6,"low>mid>lowmid")),
     "neurofunk":      dict(bpm=(170,176), key="F# minor", parent="dnb",
                            tech=[("reese_bass",.95),("amen_chops",.6),("layered_kick",.7),("curve_shaped_automation",.6),("pump_sidechain",.5)],
                            mix=(-10,-6,"low>mid>lowmid")),
     "melodic_techno": dict(bpm=(120,124), key="A minor", parent="techno",
                            tech=[("arp_8th",.9),("evolving_pads",.85),("pump_sidechain",.8),("curve_shaped_automation",.7),("journey_structure",.7)],
                            mix=(-12,-8,"low>lowmid>mid")),
     "deephouse":      dict(bpm=(118,124), key="E minor", parent="house",
                            tech=[("chopped_chords",.9),("m7_chords",.85),("four_on_floor",.9),("shuffle_swing",.7),("send_reverb",.6)],
                            mix=(-13,-8,"low>lowmid>mid")),
     "triphop":        dict(bpm=(80,95), key="D minor", parent=None,
                            tech=[("dusty_chain",.9),("m7_chords",.7),("behind_beat_snare",.8),("groove_dilla",.7),("tape_saturation",.7)],
                            mix=(-14,-9,"low>lowmid>mid")),
     "gabber":         dict(bpm=(150,190), key="A minor", parent=None,
                            tech=[("gabber_kick",.95),("hoover_stab",.85),("four_on_floor",.8),("loudness_recovery",.6),("brickwall_mastering",.8)],
                            mix=(-8,-5,"low>mid>lowmid")),
     "electro":        dict(bpm=(125,135), key="C minor", parent=None,
                            tech=[("electro_boogie",.95),("808_glide",.6),("vocal_chops",.4),("cowbell_lead",.5),("neon_bass",.6)],
                            mix=(-11,-7,"low>mid>lowmid")),
     "citypop":        dict(bpm=(100,115), key="Ab major", parent=None,
                            tech=[("maj7_gloss",.95),("offbeat_bass",.6),("dotted8_delay",.6),("gated_reverb_snare",.5),("tape_saturation",.5)],
                            mix=(-14,-9,"lowmid>low>mid")),
    }
    for g, spec in WAVE.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        if spec["parent"]:
            kg.link("Genre", g, "SUBGENRE_OF", "Genre", spec["parent"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    print("wave 4 seeded:",
          kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()
