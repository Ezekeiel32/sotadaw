#!/usr/bin/env python3
"""KG curation wave 5 (2026-07-03): the FOUNDATIONS — the genres hip-hop/house/
edm sample FROM (funk/soul/disco breaks feed THE CHOP), plus latin/african/
caribbean pillars and two modern heavies. Idempotent (MERGE)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w5"
    NEW_TECH = {
     "funk_break": "the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it",
     "walking_bass": "bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1",
     "horn_stabs": "tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)",
     "four_floor_disco": "disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria",
     "montuno": "salsa piano montuno: syncopated arpeggiated vamp locking the 2-3 or 3-2 clave; never on the downbeat grid",
     "clave_23": "the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it",
     "highlife_guitar": "interlocking palm-wine guitar lines (2-finger arpeggios) over a gentle 4/4 — bright, clean, no distortion",
     "kompa_gouyad": "kompa's slow-wind groove ~90bpm: tight kick+conga pocket, guitar skank on the offbeat, bass melodic not subby",
     "power_chords": "rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density",
     "festival_drop": "big-room drop: pitched kick + offbeat FM/saw stab in unison, white-noise risers 8 bars before, HALF the elements you think you need",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "funk":     dict(bpm=(95,115), key="E minor", tech=[("funk_break",.95),("walking_bass",.85),("horn_stabs",.8),("ghost_notes",.85),("tape_saturation",.6)], mix=(-14,-9,"low>lowmid>mid")),
     "soul":     dict(bpm=(70,95), key="C major", tech=[("walking_bass",.8),("m7_chords",.85),("behind_beat_snare",.75),("horn_stabs",.6),("send_reverb",.6)], mix=(-16,-10,"lowmid>low>mid")),
     "disco":    dict(bpm=(110,125), key="A minor", tech=[("four_floor_disco",.95),("walking_bass",.7),("horn_stabs",.65),("offbeat_bass",.8),("tape_saturation",.5)], mix=(-13,-8,"low>lowmid>mid")),
     "rock":     dict(bpm=(110,150), key="E minor", tech=[("power_chords",.95),("layered_snare",.7),("gain_staged_saturation",.7),("huge_space",.5)], mix=(-12,-8,"lowmid>low>mid")),
     "salsa":    dict(bpm=(160,200), key="C major", tech=[("clave_23",.95),("montuno",.9),("horn_stabs",.8),("walking_bass",.6)], mix=(-14,-9,"lowmid>mid>low")),
     "highlife": dict(bpm=(100,120), key="G major", tech=[("highlife_guitar",.95),("clave_23",.6),("horn_stabs",.6),("call_response_melody",.7)], mix=(-15,-10,"lowmid>mid>low")),
     "kompa":    dict(bpm=(85,95), key="F major", tech=[("kompa_gouyad",.95),("call_response_melody",.6),("send_reverb",.5)], mix=(-14,-9,"low>lowmid>mid")),
     "bigroom":  dict(bpm=(126,130), key="F minor", tech=[("festival_drop",.95),("riser_throws",.85),("pump_sidechain",.8),("supersaw_pads",.7),("brickwall_mastering",.8)], mix=(-9,-6,"low>mid>lowmid")),
     "jazzfusion": dict(bpm=(100,140), key="D minor", tech=[("m7_chords",.85),("walking_bass",.8),("ghost_notes",.7),("chopped_chords",.5)], mix=(-16,-11,"lowmid>mid>low")),
     "gfunk":    dict(bpm=(88,96), key="C minor", tech=[("funk_break",.7),("sliding_808",.6),("neon_bass",.75),("m7_chords",.6),("behind_beat_snare",.7)], mix=(-12,-8,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # lineage that matters for sampling workflows
    for a, b in (("gfunk", "funk"), ("disco", "funk"), ("boombap", "funk"), ("boombap", "soul"),
                 ("house", "disco"), ("bigroom", "house")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation="curated:claude/2026-07-03-w5")
    print("wave 5:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()


def seed_foundation_voices():
    """Foundation-voice SoundRecipes (2026-07-03): the 4 battery-verified faust
    voices minted for wave 5 — brass_stab, clav_funk, organ_soul, strings_disco."""
    kg = KG()
    prov = "curated:claude/2026-07-03-foundation-voices (f0/centroid/tail battery-verified)"
    R = {
     "brass_section": ("brass_stab", "faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses", ["funk", "soul", "disco", "salsa", "highlife"]),
     "clav_comp": ("clav_funk", "faust clav_funk: narrow pulse + snap transient, fast decay — 16th staccato comping with ghost velocities (0.2-0.4)", ["funk", "gfunk"]),
     "gospel_organ": ("organ_soul", "faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns", ["soul", "funk", "jazzfusion"]),
     "solina_strings": ("strings_disco", "faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses", ["disco", "soul", "citypop"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("foundation-voice recipes seeded")

if __name__ == "__main__" and "--voices" in sys.argv:
    seed_foundation_voices()
