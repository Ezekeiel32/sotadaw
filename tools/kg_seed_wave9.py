#!/usr/bin/env python3
"""KG curation wave 9 (2026-07-03): THE MAINSTREAM + THE WORLD — pop (the
biggest genre on earth was somehow missing) and kpop's section-morphing
production, the rock family (metal/punk/indie/shoegaze), latin dance floors
(bachata/merengue), and the african current (kuduro, singeli — Tanzania's
180-300bpm wave). Idempotent (MERGE). 79 -> 89 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w9"
    NEW_TECH = {
     "topline_first": "pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses",
     "prechorus_lift": "the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1",
     "section_morph": "kpop production: SECTIONS CHANGE GENRE — trap verse, house chorus, R&B bridge; the whiplash is the aesthetic. Keep key or tempo as the single thread so it reads as one song",
     "palm_mute_chug": "metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither",
     "dbeat_energy": "punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30",
     "jangle_strum": "indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed",
     "wall_of_blur": "shoegaze: stack fuzz + reverse-reverb + pitch-glide guitar layers until individual notes blur into a WALL; vocals mixed INTO the wall (a texture, not a lead), tempos slow",
     "bachata_requinto": "bachata: requinto lead arpeggios answer the vocal line, guira drives 16ths, bongo rolls into every 4th beat, bass syncopates 1-and-3-and — romance at 120-135",
     "merengue_drive": "merengue: tambora roll-slap pattern + guira SIXTEENTH sprint at 130-160 2/4 feel, saxophone jaleo riffs in unison octaves — relentless forward drive, no half-time ever",
     "kuduro_batida": "kuduro: raw 4/4 batida at 125-140 from chopped vocal shouts, sawtooth stabs and carnival whistles; percussion loops hard-panned, energy over polish",
     "singeli_sprint": "singeli: 180-300bpm frantic loop music — pitched-up taarab/bongo samples looped tight, MC shouts riding on top; the SPEED is the genre; keep the loop 1-2 bars max",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "pop":        dict(bpm=(100,122), key="C major", tech=[("topline_first",.95),("prechorus_lift",.9),("pump_sidechain",.6),("vocal_chops",.6),("brickwall_mastering",.7)], mix=(-9,-6,"low>lowmid>mid")),
     "kpop":       dict(bpm=(100,140), key="Ab major",tech=[("section_morph",.95),("topline_first",.85),("prechorus_lift",.8),("supersaw_pads",.6),("brickwall_mastering",.8)], mix=(-7,-5,"low>mid>lowmid")),
     "metal":      dict(bpm=(90,200),  key="E minor", tech=[("palm_mute_chug",.95),("power_chords",.8),("layered_snare",.75),("gain_staged_saturation",.8)], mix=(-10,-7,"lowmid>low>mid")),
     "punk":       dict(bpm=(160,190), key="A major", tech=[("dbeat_energy",.95),("power_chords",.9),("gain_staged_saturation",.7)], mix=(-11,-8,"lowmid>mid>low")),
     "indie_rock": dict(bpm=(110,145), key="G major", tech=[("jangle_strum",.9),("power_chords",.6),("huge_space",.6),("tape_saturation",.6)], mix=(-13,-9,"lowmid>mid>low")),
     "shoegaze":   dict(bpm=(80,120),  key="D major", tech=[("wall_of_blur",.95),("huge_space",.8),("send_reverb",.8),("evolving_pads",.6)], mix=(-13,-9,"lowmid>mid>low")),
     "bachata":    dict(bpm=(120,135), key="A minor", tech=[("bachata_requinto",.95),("call_response_melody",.7),("ghost_notes",.5)], mix=(-13,-9,"lowmid>low>mid")),
     "merengue":   dict(bpm=(130,160), key="F major", tech=[("merengue_drive",.95),("horn_stabs",.8),("call_response_melody",.7)], mix=(-12,-8,"lowmid>mid>low")),
     "kuduro":     dict(bpm=(125,140), key="F minor", tech=[("kuduro_batida",.95),("vocal_chops",.8),("hat_rolls",.6),("call_response_melody",.6)], mix=(-9,-6,"low>lowmid>mid")),
     "singeli":    dict(bpm=(180,300), key="C minor", tech=[("singeli_sprint",.95),("vocal_chops",.7),("sparse_kick",.4)], mix=(-10,-7,"lowmid>mid>low")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    for a, b in (("kpop", "pop"), ("kpop", "rnb"), ("pop", "disco"), ("pop", "rnb"),
                 ("metal", "rock"), ("punk", "rock"), ("indie_rock", "rock"),
                 ("shoegaze", "indie_rock"), ("shoegaze", "punk"),
                 ("kuduro", "house"), ("hyperpop", "pop")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 9:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()
