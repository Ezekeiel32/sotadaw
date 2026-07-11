#!/usr/bin/env python3
"""KG curation wave 13 (2026-07-03): THE WORLD TRADITIONS — curated AFTER their
signature voices landed (accordion, steel_pan — the wave-5 lesson: palette
first, then the genres that need it). Carnival (soca/calypso), the antilles
(zouk), brazil's forró, and the deep traditions (flamenco/tango/klezmer/
celtic/gnawa/mariachi). Idempotent (MERGE). 120 -> 130 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w13"
    NEW_TECH = {
     "soca_engine": "power soca: 4-floor at 155-165 + the IRON section (brake-drum/cowbell straight 8ths), steel pan riffs, jab-jab chant hooks — carnival velocity, no half-time anywhere",
     "calypso_lilt": "calypso: lilting boom-chick at 100-120, steel pan + brass ANSWER the vocal line, storytelling verse structure — wit over aggression",
     "zouk_beat": "zouk: compas-derived machine beat ~95-110 (tight kick cell + rimshot pattern), glossy synth chords, romance pacing — the pocket is polite but insistent",
     "forro_gallop": "forró: zabumba boom on the 1 + slap on the and, triangle sizzling straight 8ths, ACCORDION leads the melody — 2/4 gallop at 90-110",
     "flamenco_compas": "flamenco: the 12-beat compás with accents on 3-6-8-10-12 (bulería feel), palmas hand-clap layers, phrygian around E — nylon strums played AS percussion",
     "tango_marcato": "tango: marcato in 4 — dry stabbing strings/piano on EVERY beat, bandoneon-style sighs (accordion, slow bellows) between phrases, D-minor drama; NO drum kit, the ensemble IS the rhythm",
     "klezmer_freygish": "klezmer: freygish (phrygian dominant) melody with grace-note sobs (krekhts), oom-pah bass, simcha tempo — joy and grief in the same phrase",
     "celtic_reel": "celtic reel: constant 8th-note melodic motion at 110-120, fiddle/whistle doubled in unison, bodhrán pulse underneath, DRONES under everything",
     "gnawa_loop": "gnawa: guembri bass ostinato (pentatonic 2-bar loop, hypnotic), qraqeb iron clatter on the 8ths, call-response chant — trance through repetition at 80-100",
     "mariachi_son": "mariachi son: the 6/8-vs-3/4 HEMIOLA, vihuela chop + guitarrón bass, trumpets in duet thirds — write the hemiola as alternating bar accents",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "soca":     dict(bpm=(155,165), key="F major", tech=[("soca_engine",.95),("four_on_floor",.85),("call_response_melody",.7),("hat_rolls",.5)], mix=(-9,-7,"low>lowmid>mid")),
     "calypso":  dict(bpm=(100,120), key="C major", tech=[("calypso_lilt",.95),("horn_stabs",.7),("call_response_melody",.8)], mix=(-13,-9,"lowmid>low>mid")),
     "zouk":     dict(bpm=(95,110),  key="A minor", tech=[("zouk_beat",.95),("m7_chords",.7),("call_response_melody",.6),("send_reverb",.5)], mix=(-12,-8,"low>lowmid>mid")),
     "forro":    dict(bpm=(90,110),  key="G major", tech=[("forro_gallop",.95),("call_response_melody",.7),("ghost_notes",.5)], mix=(-13,-9,"lowmid>low>mid")),
     "flamenco": dict(bpm=(90,130),  key="E major", tech=[("flamenco_compas",.95),("call_response_melody",.6),("huge_space",.4)], mix=(-15,-10,"lowmid>mid>low")),
     "tango":    dict(bpm=(60,70),   key="D minor", tech=[("tango_marcato",.95),("m7_chords",.6),("behind_beat_snare",.4)], mix=(-16,-11,"lowmid>mid>low")),
     "klezmer":  dict(bpm=(110,140), key="D major", tech=[("klezmer_freygish",.95),("call_response_melody",.7),("swing_16th",.5)], mix=(-14,-10,"lowmid>mid>low")),
     "celtic":   dict(bpm=(110,120), key="D major", tech=[("celtic_reel",.95),("evolving_pads",.5),("call_response_melody",.6)], mix=(-15,-10,"lowmid>mid>low")),
     "gnawa":    dict(bpm=(80,100),  key="C minor", tech=[("gnawa_loop",.95),("call_response_melody",.8),("huge_space",.5)], mix=(-14,-9,"low>lowmid>mid")),
     "mariachi": dict(bpm=(85,110),  key="G major", tech=[("mariachi_son",.95),("horn_stabs",.8),("call_response_melody",.7)], mix=(-13,-9,"lowmid>mid>low")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    for a, b in (("soca", "calypso"), ("zouk", "kompa"), ("dembow", "zouk"),
                 ("reggaeton", "zouk")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    # the new voices belong to these traditions
    R = {
     "squeeze_box": ("accordion", "faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color", ["forro", "cumbia", "tango", "klezmer", "zouk"]),
     "pan_lead": ("steel_pan", "faust steel_pan: struck pan w/ octave halo + ping — soca/calypso riffs and leads; roll = fast low-vel repeats", ["soca", "calypso"]),
    }
    prov_v = "curated:claude/2026-07-03-world-voices (f0/centroid/tail/attack battery-verified)"
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov_v, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("wave 13:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()


def seed_color_voices():
    """Color voices (2026-07-03): harp + vibraphone — the cinematic/jazz colors.
    Battery incl. per-excitation attack thresholds (struck 1.6x, plucked-soft 1.25x)."""
    kg = KG()
    prov = "curated:claude/2026-07-03-color-voices (f0/centroid/tail/attack battery-verified)"
    R = {
     "gliss_harp": ("harp", "faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color", ["orchestral_cinematic", "jazz", "rnb", "ambient"]),
     "motor_vibes": ("vibraphone", "faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe", ["jazz", "lofi", "soul", "bossanova"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("color-voice recipes seeded")

if __name__ == "__main__" and "--color-voices" in sys.argv:
    seed_color_voices()


def fix_early_mixtargets():
    """Suite-readiness audit fixes (2026-07-03): three early-wave MixTargets
    predate the band_order field — patched so the full suite runs clean."""
    kg = KG()
    FIX = {"ambient_mix": "lowmid>mid>low", "bossanova_mix": "lowmid>mid>low",
           "breakcore_mix": "low>lowmid>mid"}
    for name, order in FIX.items():
        kg.g.query(f"MATCH (m:MixTarget {{name:'{name}'}}) SET m.band_order = '{order}'")
    print("early MixTargets patched:", ", ".join(FIX))

if __name__ == "__main__" and "--fix-mixtargets" in sys.argv:
    fix_early_mixtargets()


def seed_spectral_presence():
    """Judge lesson (2026-07-03): spectral_presence technique + funk_mix floors —
    band ORDER can pass while magnitudes collapse (eval_funk 7/7 at centroid
    979Hz). Floors make it machine-visible; the technique teaches the fix."""
    kg = KG()
    kg.upsert('Technique', 'spectral_presence',
              'lesson:judge/2026-07-03 (eval_funk 7/7 yet himid 0.4% — hand-written A beat it margin 4)',
              desc="the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.")
    for g in ('funk','soul','disco','ska','swing_bigband','salsa','jazz','merengue'):
        kg.link('Genre', g, 'USES_TECHNIQUE', 'Technique', 'spectral_presence', weight=0.8)
    kg.g.query("MATCH (m:MixTarget {name:'funk_mix'}) SET m.mid_floor_pct = 8.0, m.himid_floor_pct = 1.0")
    print("spectral_presence seeded + funk floors")

if __name__ == "__main__" and "--spectral" in sys.argv:
    seed_spectral_presence()


def spread_spectral_floors():
    """Floor spread (2026-07-03): per-genre spectral floors for the 7 remaining
    spectral_presence genres. swing_bigband's existing render re-checked PASS
    (mid 32%/himid 1.4%) — its 1.0 stands on 8 checks."""
    kg = KG()
    FLOORS = {"soul_mix": (7.0, 0.8), "disco_mix": (7.0, 0.8), "ska_mix": (10.0, 1.5),
              "swing_bigband_mix": (12.0, 1.0), "salsa_mix": (10.0, 1.2),
              "jazz_mix": (10.0, 1.0), "merengue_mix": (10.0, 1.2)}
    for name, (mid, hi) in FLOORS.items():
        kg.g.query(f"MATCH (m:MixTarget {{name:'{name}'}}) SET m.mid_floor_pct = {mid}, m.himid_floor_pct = {hi}")
    print("spectral floors spread:", len(FLOORS), "genres")

if __name__ == "__main__" and "--spread-floors" in sys.argv:
    spread_spectral_floors()
