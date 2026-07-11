#!/usr/bin/env python3
"""KG curation wave 6 (2026-07-03): the SOUNDSYSTEM + MAINSTREAM wave — dub as the
root of remix culture (delay throws ARE proto-automation), dancehall as the riddim
bridge to dembow/reggaeton, R&B + new jack swing closing the funk/soul lineage into
the mainstream, and the four club economies missing from the map (tech house, afro
house, hard techno, future bass) plus the 808 keystone (miami bass) and 90s canon
(eurodance). Idempotent (MERGE). 49 -> 59 genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w6"
    NEW_TECH = {
     "one_drop": "reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole",
     "dub_delay_ride": "the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track",
     "riddim_bounce": "dancehall riddim: 3+3+2 kick placement under a halftime snare on 3 — the dembow ancestor; keep melody sparse minor pentatonic so the riddim carries",
     "finger_snap_beat": "modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars",
     "swingbeat_machine": "new jack swing: hard-quantized swung 16ths (SP-1200/MPC60 feel, swing ~0.58) + gated reverb snare + James Brown-lineage stab samples over R&B chords",
     "future_chord_pump": "future bass signature: supersaw CHORDS pitch-bent between voicings, volume pumped by a free-running LFO (not kick sidechain) — the chord itself wobbles; brightness follows the pump",
     "booty_808": "miami bass: the TR-808 kick IS the bassline — tuned kick call-response with sub drops, 130bpm 16th hats, electro claps; rap call-and-response on top",
     "piano_house_stab": "rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast",
     "afro_house_perc": "afro house engine: layered ORGANIC percussion loops (shaker+conga+wood) with one lead drum voice doing the call, deep sub swells underneath — percussion is the melody",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "dub":            dict(bpm=(65,90),   key="D minor", tech=[("one_drop",.95),("dub_delay_ride",.95),("offbeat_bass",.8),("send_reverb",.85),("echo_out_cut",.7)], mix=(-14,-9,"low>lowmid>mid")),
     "dancehall":      dict(bpm=(85,105),  key="B minor", tech=[("riddim_bounce",.95),("dembow_rhythm",.7),("call_response_melody",.7),("sparse_kick",.6)], mix=(-11,-7,"low>lowmid>mid")),
     "rnb":            dict(bpm=(65,95),   key="F minor", tech=[("finger_snap_beat",.9),("m7_chords",.85),("behind_beat_snare",.7),("sliding_808",.6),("send_reverb",.6)], mix=(-12,-8,"low>lowmid>mid")),
     "new_jack_swing": dict(bpm=(100,115), key="C minor", tech=[("swingbeat_machine",.95),("gated_reverb_snare",.85),("horn_stabs",.6),("m7_chords",.7),("swing_16th",.8)], mix=(-13,-9,"lowmid>low>mid")),
     "tech_house":     dict(bpm=(124,128), key="F minor", tech=[("rolling_offbeat_bass",.95),("four_on_floor",.9),("vocal_chops",.75),("pump_sidechain",.7),("filter_transition",.6)], mix=(-8,-6,"low>lowmid>mid")),
     "afro_house":     dict(bpm=(118,124), key="A minor", tech=[("afro_house_perc",.95),("four_on_floor",.8),("evolving_pads",.7),("call_response_melody",.65),("journey_structure",.6)], mix=(-11,-8,"low>lowmid>mid")),
     "hard_techno":    dict(bpm=(145,160), key="F minor", tech=[("rumble_kick",.95),("four_on_floor",.9),("hoover_stab",.6),("filter_build",.7),("brickwall_mastering",.8)], mix=(-7,-5,"low>mid>lowmid")),
     "future_bass":    dict(bpm=(140,160), key="D major", tech=[("future_chord_pump",.95),("vocal_chops",.85),("half_time_140",.8),("hat_rolls",.6),("supersaw_pads",.7)], mix=(-9,-6,"low>mid>lowmid")),
     "miami_bass":     dict(bpm=(125,135), key="A minor", tech=[("booty_808",.95),("electro_boogie",.7),("call_response_melody",.75),("hat_rolls",.7)], mix=(-11,-7,"low>lowmid>mid")),
     "eurodance":      dict(bpm=(130,140), key="A minor", tech=[("piano_house_stab",.9),("four_on_floor",.9),("supersaw_pads",.7),("riser_throws",.6),("offbeat_bass",.7)], mix=(-10,-7,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # lineage: soundsystem culture + the funk->mainstream chain + club economies
    for a, b in (("dancehall", "dub"), ("dembow", "dancehall"), ("reggaeton", "dancehall"),
                 ("dubstep", "dub"), ("triphop", "dub"), ("jungle", "dub"),
                 ("new_jack_swing", "funk"), ("new_jack_swing", "soul"), ("rnb", "new_jack_swing"),
                 ("baile_funk", "miami_bass"), ("tech_house", "house"), ("tech_house", "techno"),
                 ("afro_house", "deephouse"), ("afro_house", "afrobeats"),
                 ("hard_techno", "techno"), ("hard_techno", "gabber"),
                 ("future_bass", "trap"), ("future_bass", "dubstep"),
                 ("eurodance", "house"), ("hyperpop", "eurodance")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 6:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()
