#!/usr/bin/env python3
"""KG curation wave 7 (2026-07-03): THE ROOTS — the trunks the graph's branches
hang from: reggae (ska->rocksteady->reggae chain, one_drop's true home), blues
(rock's parent), jazz (fusion's parent), gospel (soul's parent, organ_soul's
home), hiphop (boombap/trap's parent culture), afrobeat (Fela — NOT afrobeats),
samba (baile funk's other parent), country. Fixes lineage direction for wave-6
nodes (dancehall also from reggae). Idempotent (MERGE). 59 -> 69 genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w7"
    NEW_TECH = {
     "skank_upstroke": "ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse",
     "twelve_bar_blues": "the 12-bar form is the LAW: I-I-I-I / IV-IV-I-I / V-IV-I-V(turnaround), shuffle triplet feel (swing ~0.66), melody answers itself every 2 bars",
     "blues_bends": "melody lives on the blue notes: b3, b5, b7 approached by bend/slide (pitch scoop 30-80ms) — never land ON the major 3rd while the band plays dominant chords",
     "swing_ride": "jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1",
     "jazz_comping": "piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th",
     "gospel_progression": "gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords",
     "train_beat": "country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills",
     "tony_allen_groove": "afrobeat drums: broken hi-hat/kick conversation that NEVER repeats 1:1 bar to bar, ghosted snare chatter; the band vamps ONE chord for minutes — tension from layers, not changes",
     "samba_batucada": "samba engine: surdo anchors beat 2 (not 1), caixa rides 16ths with accent displacement, tamborim carries the telecoteco cell — layered percussion IS the song",
     "break_looping": "hiphop's founding move: loop the break (the drum-solo bars), cut between two copies on the 1 — then rap over it; everything else (sampling, chopping, scratching) grew from this",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "reggae":    dict(bpm=(70,90),   key="A minor", tech=[("one_drop",.95),("skank_upstroke",.95),("offbeat_bass",.7),("send_reverb",.6),("call_response_melody",.6)], mix=(-14,-9,"low>lowmid>mid")),
     "ska":       dict(bpm=(120,145), key="C major", tech=[("skank_upstroke",.95),("walking_bass",.8),("horn_stabs",.85),("four_floor_disco",.5)], mix=(-13,-9,"lowmid>mid>low")),
     "rocksteady":dict(bpm=(80,100),  key="C major", tech=[("skank_upstroke",.9),("one_drop",.7),("walking_bass",.75),("call_response_melody",.6)], mix=(-14,-10,"low>lowmid>mid")),
     "blues":     dict(bpm=(60,120),  key="E major", tech=[("twelve_bar_blues",.95),("blues_bends",.9),("shuffle_swing",.8),("ghost_notes",.6)], mix=(-16,-11,"lowmid>mid>low")),
     "jazz":      dict(bpm=(80,220),  key="Bb major",tech=[("swing_ride",.95),("walking_bass",.9),("jazz_comping",.9),("m7_chords",.8)], mix=(-18,-12,"lowmid>mid>low")),
     "gospel":    dict(bpm=(60,110),  key="Ab major",tech=[("gospel_progression",.95),("m7_chords",.8),("behind_beat_snare",.7),("call_response_melody",.85)], mix=(-14,-9,"lowmid>low>mid")),
     "country":   dict(bpm=(90,130),  key="G major", tech=[("train_beat",.95),("walking_bass",.7),("twelve_bar_blues",.5),("tape_saturation",.5)], mix=(-14,-9,"lowmid>mid>low")),
     "afrobeat":  dict(bpm=(100,130), key="E minor", tech=[("tony_allen_groove",.95),("horn_stabs",.85),("call_response_melody",.8),("clave_23",.6),("journey_structure",.7)], mix=(-14,-9,"lowmid>low>mid")),
     "samba":     dict(bpm=(95,110),  key="D major", tech=[("samba_batucada",.95),("clave_23",.5),("call_response_melody",.7),("walking_bass",.5)], mix=(-13,-9,"lowmid>mid>low")),
     "hiphop":    dict(bpm=(85,100),  key="C minor", tech=[("break_looping",.95),("funk_break",.85),("behind_beat_snare",.7),("dusty_chain",.7),("ghost_notes",.6)], mix=(-12,-8,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # the trunk lineage: chains the branches were missing
    for a, b in (("rocksteady", "ska"), ("reggae", "rocksteady"), ("dub", "reggae"),
                 ("dancehall", "reggae"), ("rock", "blues"), ("jazz", "blues"),
                 ("soul", "gospel"), ("jazzfusion", "jazz"), ("bossanova", "samba"),
                 ("bossanova", "jazz"), ("baile_funk", "samba"), ("afrobeats", "afrobeat"),
                 ("afrobeats", "highlife"), ("boombap", "hiphop"), ("trap", "hiphop"),
                 ("hiphop", "funk"), ("hiphop", "soul"), ("country", "blues"),
                 ("gfunk", "hiphop"), ("triphop", "hiphop")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    # gospel is organ_soul's true home
    kg.link("Genre", "gospel", "CHARACTERIZED_BY", "SoundRecipe", "gospel_organ")
    print("wave 7:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()
