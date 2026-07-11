#!/usr/bin/env python3
"""KG curation wave 10 (2026-07-03): THE HUNDRED — the pillars that complete the
first hundred: french house (filter disco), italo, industrial, future garage
(Burial's ghost 2-step), big band swing, progressive house, jpop, latin trap,
cinematic orchestral (the media-composer ask), drone, downtempo.
Idempotent (MERGE). 89 -> 100 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w10"
    NEW_TECH = {
     "filter_disco_loop": "french house: loop 2-4 bars of disco (or self-sampled equivalent) and RIDE a lowpass over 8-16 bars with sidechain pump — the filter ride IS the arrangement",
     "italo_arp": "italo disco: octave-jump bass 8ths + bright polysynth arps + gated snare at 115-125; romantic minor melodies sung earnestly — drama over cool",
     "machine_percussion": "industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read",
     "haunted_2step": "future garage: 2-step shuffle with the ghosts turned up — pitch-shifted vocal wisps, sub SWELLS (not hits), vinyl crackle as glue, empty space as the lead",
     "bigband_shout": "big band: the SHOUT chorus — full horn soli in block harmony over walking bass + swing ride; sections converse (saxes call, brass answer), dynamics terraced not gradual",
     "prog_layer_build": "progressive house: additive 16-32 bar builds (one element per 8), rolling offbeat bass, ONE breakdown to near-silence mid-track, then the full arrangement drop",
     "jpop_modulation": "jpop: dense borrowed-from-jazz chord motion under a bright topline, and the LAST-CHORUS KEY CHANGE (+1 semitone) — earnestness is the aesthetic",
     "latin_trap_bounce": "latin trap: dembow lilt underneath trap 808 slides and hats — the drums swing like reggaeton but hit like trap; melodic minor toplines",
     "trailer_build": "cinematic: ostinato strings (8th cells) + brass swells + a percussion HIT every 4 bars, riser into tutti-plus-choir; silence right before the biggest hit",
     "drone_tension": "drone: one sustained cluster evolving by slow filter/detune/partial motion — no rhythm, no bar lines; FORM IS DURATION; motion so slow it is felt not heard",
     "headnod_slow": "downtempo: 85-100bpm dusty break with the snare a hair late, warm round sub, long pads — triphop's beach-side sibling; nothing louder than relaxed",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "french_house":       dict(bpm=(118,126), key="A minor", tech=[("filter_disco_loop",.95),("pump_sidechain",.9),("four_floor_disco",.7),("tape_saturation",.6)], mix=(-9,-6,"low>lowmid>mid")),
     "italo_disco":        dict(bpm=(115,125), key="C minor", tech=[("italo_arp",.95),("gated_reverb_snare",.8),("offbeat_bass",.7),("supersaw_pads",.5)], mix=(-11,-8,"low>lowmid>mid")),
     "industrial":         dict(bpm=(120,145), key="D minor", tech=[("machine_percussion",.95),("gain_staged_saturation",.9),("layered_snare",.6),("filter_build",.5)], mix=(-10,-7,"lowmid>low>mid")),
     "future_garage":      dict(bpm=(130,140), key="F minor", tech=[("haunted_2step",.95),("groove_ukg_shuffle",.7),("send_reverb",.8),("huge_space",.8),("reese_bass",.5)], mix=(-14,-10,"low>lowmid>mid")),
     "swing_bigband":      dict(bpm=(120,220), key="Bb major",tech=[("bigband_shout",.95),("swing_ride",.9),("walking_bass",.9),("horn_stabs",.7),("call_response_melody",.8)], mix=(-16,-11,"lowmid>mid>low")),
     "progressive_house":  dict(bpm=(122,128), key="A minor", tech=[("prog_layer_build",.95),("rolling_offbeat_bass",.8),("evolving_pads",.7),("riser_throws",.7),("journey_structure",.8)], mix=(-9,-7,"low>lowmid>mid")),
     "jpop":               dict(bpm=(120,160), key="E major", tech=[("jpop_modulation",.9),("topline_first",.85),("m7_chords",.7),("prechorus_lift",.7)], mix=(-8,-6,"lowmid>low>mid")),
     "latin_trap":         dict(bpm=(88,100),  key="C# minor",tech=[("latin_trap_bounce",.95),("sliding_808",.85),("dembow_rhythm",.7),("hat_rolls",.7)], mix=(-10,-7,"low>lowmid>mid")),
     "orchestral_cinematic": dict(bpm=(80,140), key="D minor", tech=[("trailer_build",.9),("evolving_pads",.6),("huge_space",.8),("journey_structure",.7)], mix=(-16,-10,"lowmid>low>mid")),
     "drone":              dict(bpm=(60,60),   key="C minor", tech=[("drone_tension",.95),("evolving_pads",.8),("huge_space",.7),("send_reverb",.6)], mix=(-20,-12,"lowmid>low>mid")),
     "downtempo":          dict(bpm=(85,100),  key="G minor", tech=[("headnod_slow",.95),("behind_beat_snare",.7),("dusty_chain",.7),("m7_chords",.5)], mix=(-14,-10,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    for a, b in (("french_house", "disco"), ("french_house", "house"), ("italo_disco", "disco"),
                 ("industrial", "punk"), ("industrial", "techno"),
                 ("future_garage", "ukgarage"), ("future_garage", "dubstep"),
                 ("swing_bigband", "jazz"), ("progressive_house", "house"), ("progressive_house", "trance"),
                 ("jpop", "pop"), ("jpop", "citypop"), ("latin_trap", "trap"), ("latin_trap", "reggaeton"),
                 ("drone", "ambient"), ("downtempo", "triphop"), ("downtempo", "dub")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 10:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()


def seed_rhythm_section_voices():
    """Rhythm-section voices (2026-07-03): guitar_grit / log_drum / timpani —
    the palette gaps THE HUNDRED exposed (7 guitar genres, the amapiano scene,
    cinematic). Run AFTER the f0/centroid/tail battery passes."""
    kg = KG()
    prov = "curated:claude/2026-07-03-rhythm-voices (f0/centroid/tail battery-verified)"
    R = {
     "grit_guitar": ("guitar_grit", "faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release", ["rock", "metal", "punk", "indie_rock", "shoegaze", "blues", "country", "big_beat"]),
     "piano_log_drum": ("log_drum", "faust log_drum: THE amapiano bass — woody pitch-drop knock over a round sub tail; sequence it as the bassline answering the kick in the holes", ["amapiano", "3step", "gqom"]),
     "cine_timpani": ("timpani", "faust timpani: tuned orchestral drum, strike pitch-drop + mallet noise, long boom; fast low-vel repeats = rolls under trailer builds", ["orchestral_cinematic"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("rhythm-section voice recipes seeded")

if __name__ == "__main__" and "--voices" in sys.argv:
    seed_rhythm_section_voices()


def seed_section_voices():
    """Section voices (2026-07-03): sax_section + cine_brass — the horn/orchestral
    gaps left after the rhythm section. Run AFTER the battery passes."""
    kg = KG()
    prov = "curated:claude/2026-07-03-section-voices (f0/centroid/tail battery-verified)"
    R = {
     "sax_soli": ("sax_section", "faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)", ["swing_bigband", "jazz", "merengue", "ska", "soul"]),
     "trailer_brass": ("cine_brass", "faust cine_brass: dark detuned saw wall + octave double, filter blooms SLOWER than amp (crescendo lives in the filter; `swell` 0..1) — hold whole notes for trailer swells; brass_stab stays the funk stab", ["orchestral_cinematic"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("section-voice recipes seeded")

if __name__ == "__main__" and "--section-voices" in sys.argv:
    seed_section_voices()
