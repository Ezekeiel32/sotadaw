#!/usr/bin/env python3
"""KG curation wave 8 (2026-07-03): THE CONTINUUM + THE CURRENT — breakbeat
hardcore (the missing parent of jungle/happy hardcore/gabber's rave side),
big beat & IDM (the 90s electronica poles), the UK bass chain (speed garage
-> bassline, uk funky), and the RIGHT-NOW waves (3-step, corridos tumbados,
sexy drill). Idempotent (MERGE). 69 -> 79 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w8"
    NEW_TECH = {
     "big_beat_break": "big beat: a LOUD compressed funk break at 100-120 (half rave tempo) + acid 303 + rock-energy stabs; the break is the lead instrument — distort it, filter it, drop it out for the build",
     "idm_microedit": "IDM drum programming: no bar repeats 1:1 — retrigger/reverse/bitcrush/half-gate single hits per pass; melody = detuned melancholy pads drifting over the broken grid",
     "tribal_kicks": "uk funky: the drums are MELODIC — syncopated toms answer the kick (soca/broken-beat DNA), skippy snares, NOT four-on-floor; percussion carries the hook",
     "3step_pulse": "3-step: amapiano stripped to a 3-hit kick cell per bar (x..x..x.) with huge negative space; log drum answers the kick in the holes; keep everything else whisper-quiet",
     "requinto_trap": "corridos tumbados: requinto/nylon guitar arpeggios + BRASS BASS (tuba/trombone walking lines) + trap swagger; often 6/8 or 3/4 waltz feel — grid the guitars tight, let vocals lag",
     "sexy_drill_bounce": "sexy drill: airy chopped vocal/soul loops floating free, SPARSE sliding 808 landing behind the beat, rimshot-led halftime drums ~140 — seduction through space, not aggression",
     "hardcore_stomp": "happy hardcore: 165-180 four-floor stomp + offbeat bass stabs + pitched-up vocal hooks; rave-piano half-time breakdown, then slam back to double-time",
     "warped_bassline": "speed garage/bassline: the pitch-WARPED sub 'wow' (detuned reese, filter+pitch bend per note) under a 4x4 garage shuffle; organ stabs on the offbeat",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "breakbeat_hardcore": dict(bpm=(140,155), key="A minor", tech=[("amen_chops",.9),("hoover_stab",.85),("piano_house_stab",.8),("riser_throws",.6)], mix=(-10,-7,"low>lowmid>mid")),
     "big_beat":           dict(bpm=(100,120), key="E minor", tech=[("big_beat_break",.95),("acid_squelch_lead",.7),("gain_staged_saturation",.8),("filter_build",.6)], mix=(-9,-6,"low>lowmid>mid")),
     "idm":                dict(bpm=(80,160),  key="C minor", tech=[("idm_microedit",.95),("evolving_pads",.8),("fm_metallic_arps",.6),("send_reverb",.6)], mix=(-14,-9,"lowmid>mid>low")),
     "uk_funky":           dict(bpm=(128,132), key="F minor", tech=[("tribal_kicks",.95),("vocal_chops",.7),("offbeat_bass",.6),("call_response_melody",.6)], mix=(-10,-7,"low>lowmid>mid")),
     "3step":              dict(bpm=(110,116), key="D minor", tech=[("3step_pulse",.95),("log_drum_bass",.85),("evolving_pads",.7),("huge_space",.8)], mix=(-13,-9,"low>lowmid>mid")),
     "corridos_tumbados":  dict(bpm=(95,125),  key="E minor", tech=[("requinto_trap",.95),("call_response_melody",.7),("behind_beat_snare",.5)], mix=(-11,-8,"lowmid>low>mid")),
     "sexy_drill":         dict(bpm=(136,145), key="Bb minor",tech=[("sexy_drill_bounce",.95),("sliding_808",.8),("vocal_chops",.75),("half_time_140",.7)], mix=(-11,-7,"low>lowmid>mid")),
     "happy_hardcore":     dict(bpm=(165,180), key="F major", tech=[("hardcore_stomp",.95),("piano_house_stab",.75),("supersaw_pads",.7),("pitch_vox_hyper",.6)], mix=(-8,-5,"low>mid>lowmid")),
     "speed_garage":       dict(bpm=(130,136), key="G minor", tech=[("warped_bassline",.9),("groove_ukg_shuffle",.8),("four_on_floor",.7),("vocal_chops",.6)], mix=(-9,-6,"low>lowmid>mid")),
     "bassline":           dict(bpm=(135,142), key="F# minor",tech=[("warped_bassline",.95),("two_step_kick",.6),("vocal_chops",.7),("hat_rolls",.5)], mix=(-8,-6,"low>lowmid>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # the continuum: rave's family tree + the UK bass chain + current-wave parents
    for a, b in (("breakbeat_hardcore", "hiphop"), ("breakbeat_hardcore", "house"),
                 ("jungle", "breakbeat_hardcore"), ("happy_hardcore", "breakbeat_hardcore"),
                 ("gabber", "breakbeat_hardcore"), ("big_beat", "hiphop"), ("big_beat", "house"),
                 ("idm", "techno"), ("idm", "breakbeat_hardcore"),
                 ("uk_funky", "house"), ("uk_funky", "ukgarage"),
                 ("3step", "amapiano"), ("corridos_tumbados", "trap"),
                 ("sexy_drill", "drill"), ("speed_garage", "house"), ("speed_garage", "jungle"),
                 ("bassline", "speed_garage"), ("bassline", "ukgarage")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 8:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()
