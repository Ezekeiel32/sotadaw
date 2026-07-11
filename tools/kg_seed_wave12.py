#!/usr/bin/env python3
"""KG curation wave 12 (2026-07-03): THE SOURCES + THE TRANSFORMS — the regional
club sources the tree owed (memphis rap = phonk's actual parent, baltimore club
= jersey's, NOLA bounce, crunk, ghettotech) and the transform cultures users ask
for by name (vaporwave, chillwave, witch house, nightcore, breaks).
Idempotent (MERGE). 110 -> 120 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w12"
    NEW_TECH = {
     "triggerman_bounce": "NOLA bounce: the Triggerman cell (bells + claps) looped relentlessly ~100bpm, call-and-response party shouts, dance-command vocals — the loop IS the song",
     "crunk_shout": "crunk: shouted GROUP vocals as the hook, minimal minor synth stabs (2-3 notes), halftime 808 slam at 75-85 — aggression as energy, space as tension",
     "bmore_break": "baltimore club: the Sing-Sing/Think break stuttering under a x.x.xx.x kick cell at ~130, chopped one-word vocal shots — raw, unquantized-feeling, relentless",
     "ghettotech_talk": "ghettotech: miami-bass vocal chants at detroit speed (~150), 808 toms, jittery 16th machine programming — booty electro at techno velocity",
     "vapor_slow": "vaporwave: slow the source 20-40% and pitch it down 3-5 semitones, drench in reverb+chorus, let the loop hypnotize — tape warble and imperfection ARE the aesthetic",
     "chillwave_haze": "chillwave: washed-out synth loops under heavy chorus/tape wobble, falsetto-height melodies, drums soft and set back — memory as a production style",
     "witch_drag": "witch house: chopped-and-screwed DRAG — halftime 60-70 feel, pitched-down vocals, hi-hats crawling in triplets, occult drones underneath",
     "nightcore_lift": "nightcore: pitch+tempo the whole piece UP 15-25% — vocals go bright, energy goes sugar; the TRANSFORM is the genre (warp: lower sourceBpm relative to song bpm)",
     "breaks_floor": "breaks: the broken-beat 4/4 alternative — chunky break at 128-135, big bass stabs, DJ-tool arrangement (16-bar phrases, mixable intro/outro)",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "memphis_rap":     dict(bpm=(66,80),   key="F minor", tech=[("memphis_chant",.95),("dusty_chain",.85),("behind_beat_snare",.7),("sliding_808",.6)], mix=(-12,-8,"low>lowmid>mid")),
     "crunk":           dict(bpm=(72,85),   key="C minor", tech=[("crunk_shout",.95),("sliding_808",.8),("hat_rolls",.6),("call_response_melody",.6)], mix=(-10,-7,"low>lowmid>mid")),
     "bounce":          dict(bpm=(95,105),  key="A minor", tech=[("triggerman_bounce",.95),("call_response_melody",.8),("hat_rolls",.5)], mix=(-11,-8,"low>lowmid>mid")),
     "baltimore_club":  dict(bpm=(125,135), key="G minor", tech=[("bmore_break",.95),("vocal_chops",.8),("four_on_floor",.5)], mix=(-10,-7,"low>lowmid>mid")),
     "ghettotech":      dict(bpm=(145,155), key="C minor", tech=[("ghettotech_talk",.95),("electro_boogie",.7),("four_on_floor",.6),("hat_rolls",.6)], mix=(-10,-7,"low>lowmid>mid")),
     "vaporwave":       dict(bpm=(60,85),   key="E major", tech=[("vapor_slow",.95),("send_reverb",.8),("tape_saturation",.7),("huge_space",.6)], mix=(-16,-11,"lowmid>low>mid")),
     "chillwave":       dict(bpm=(95,115),  key="A major", tech=[("chillwave_haze",.95),("evolving_pads",.7),("behind_beat_snare",.6),("tape_saturation",.6)], mix=(-14,-10,"lowmid>low>mid")),
     "witch_house":     dict(bpm=(60,75),   key="C minor", tech=[("witch_drag",.95),("sliding_808",.6),("huge_space",.8),("send_reverb",.7)], mix=(-13,-9,"low>lowmid>mid")),
     "nightcore":       dict(bpm=(160,180), key="F major", tech=[("nightcore_lift",.95),("four_on_floor",.7),("supersaw_pads",.6),("topline_first",.7)], mix=(-8,-5,"lowmid>low>mid")),
     "breaks":          dict(bpm=(128,135), key="F minor", tech=[("breaks_floor",.95),("breakbeat_chop",.7),("reese_bass",.6),("filter_build",.6)], mix=(-10,-7,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # the owed lineage: phonk's and jersey's actual parents, the transform chains
    for a, b in (("phonk", "memphis_rap"), ("memphis_rap", "hiphop"),
                 ("crunk", "memphis_rap"), ("crunk", "miami_bass"),
                 ("bounce", "hiphop"), ("bounce", "miami_bass"),
                 ("jerseyclub", "baltimore_club"), ("baltimore_club", "house"),
                 ("baltimore_club", "miami_bass"), ("ghettotech", "detroit_techno"),
                 ("ghettotech", "miami_bass"), ("vaporwave", "citypop"),
                 ("vaporwave", "synthpop"), ("chillwave", "synthpop"),
                 ("chillwave", "balearic"), ("witch_house", "memphis_rap"),
                 ("hardwave", "witch_house"), ("nightcore", "eurodance"),
                 ("nightcore", "happy_hardcore"), ("hyperpop", "nightcore"),
                 ("breaks", "breakbeat_hardcore"), ("breaks", "big_beat")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 12:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()


def seed_mallet_voices():
    """Mallet + vox voices (2026-07-03, first JIT-speed minting sprint): marimba,
    kalimba, vox_pad — battery-verified incl. attack-character checks (struck/
    plucked identity lives in the first 80ms, not the body centroid)."""
    kg = KG()
    prov = "curated:claude/2026-07-03-mallet-voices (f0/centroid/tail/attack battery-verified)"
    R = {
     "mallet_marimba": ("marimba", "faust marimba: struck bar (fundamental + ~4x shine partial + thump), no sustain — kuduro/cinematic/ambient mallets; fast low-vel repeats = rolls", ["kuduro", "orchestral_cinematic", "ambient", "afrobeat"]),
     "tine_kalimba": ("kalimba", "faust kalimba: plucked tine (near-sine + inharmonic sparkle + thumb click) — lofi/afro signature; arpeggiate gently, let notes ring", ["lofi", "afrobeats", "highlife", "chillwave"]),
     "choir_ah_pad": ("vox_pad", "faust vox_pad: designed choir-ah (saws through 700/1050 formants, slow bloom) — gospel swells, trance pads, cinematic beds; the sampled choir kit is the REAL thing, this is the designed color to layer with it", ["gospel", "trance", "orchestral_cinematic"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("mallet/vox recipes seeded")

if __name__ == "__main__" and "--voices" in sys.argv:
    seed_mallet_voices()
