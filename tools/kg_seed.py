#!/usr/bin/env python3
"""Seed the knowledge graph (curation pass v1).

Sources, each stamped in provenance:
  skill:<name>@v<N>   — knowledge lifted from our 13 shipped, ear-validated skills
  curated:claude/2026-07-02 — hand-curated genre lore (incl. graph-only genres the
                              compiler will turn into brand-new skills: phonk, techno)

Deterministic + idempotent (MERGE everywhere). Run: .venv/bin/python tools/kg_seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

CUR = "curated:claude/2026-07-02"

def seed():
    kg = KG()

    # ---------------- universal techniques (from fx-usage/mix-headroom/automation-motion skills)
    tech = [
        ("halftime_groove", "snare on beat 3 (not 2&4); space is the instrument", "skill:trap-arrangement@v2"),
        ("swing_16th", "shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk", "skill:trap-arrangement@v2"),
        ("ghost_notes", "low-velocity (0.25-0.45) off-grid hits between main hits", "skill:trap-arrangement@v2"),
        ("hat_rolls", "16th->32nd bursts at phrase ends; velocity ramps", "skill:trap-arrangement@v2"),
        ("808_glide", "long overlapping 808 notes walking the scale; tune to key", "skill:faust-808@v1"),
        ("layered_kick", "sample kick transient + faust 808 body, body -6 to -12 under", "skill:sound-palette@v2"),
        ("layered_snare", "sample clap + synth snare body at -12 to -18", "skill:sound-palette@v2"),
        ("send_reverb", "reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY", "skill:fx-usage@v1"),
        ("dotted8_delay", "delay time = 45000/bpm*1.5 ms, feedback <=0.45, on leads", "skill:fx-usage@v1"),
        ("filter_build", "fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop", "skill:automation-motion@v1"),
        ("width_bloom", "fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end", "skill:automation-motion@v1"),
        ("pump_sidechain", "fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums", "skill:fx-usage@v1"),
        ("four_on_floor", "kick every beat; openhat on offbeat 8ths", "skill:house-arrangement@v1"),
        ("offbeat_bass", "bass hits on the 8th between kicks", "skill:house-arrangement@v1"),
        ("breakbeat_chop", "kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar", "skill:dnb-arrangement@v1"),
        ("reese_bass", "detuned saw stack, movement via slow LFO on filter", "skill:faust-reese@v1"),
        ("behind_beat_snare", "snare 0.02-0.05 beats late = laid-back head-nod", "skill:lofi-arrangement@v1"),
        ("m7_chords", "minor 7th / extended chords, mid register, soft velocity", "skill:lofi-arrangement@v1"),
        ("dusty_chain", "fx_saturate drive 6-10 + fx_reverb small dark = lofi glue", "skill:lofi-arrangement@v1"),
        ("sliding_808", "808 pitch slides between roots (overlapping notes)", "skill:drill-arrangement@v1"),
        ("ghost_snare_drill", "extra snares at 3.75/4.25 around the main pocket", "skill:drill-arrangement@v1"),
        # curated for the graph-only genres
        ("cowbell_lead", "saturated cowbell/bell riff as THE melodic hook, minor pentatonic", CUR),
        ("memphis_chant", "dark chopped vocal stab as rhythmic texture (sample kit / choir low)", CUR),
        ("tape_saturation", "heavy fx_saturate drive 8-14 over the whole beat bus = grit", CUR),
        ("rumble_kick", "kick tail feeds a send reverb lowpassed into a rolling rumble", CUR),
        ("modular_stab", "single dark stab/chord repeated with filter automation variation", CUR),
        # wave 2 curation (2026-07-02): six more genres
        ("shuffle_swing", "hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt", CUR),
        ("two_step_kick", "NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove", CUR),
        ("chopped_chords", "short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm", CUR),
        ("vocal_chops", "short pitched vocal stabs (choir kit, high keys) placed rhythmically", CUR),
        ("log_drum_bass", "melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature", CUR),
        ("triplet_percs", "3:2 cross-rhythm percussion over a straight kick — rims/toms/shaker", CUR),
        ("sparse_kick", "kick on 1 and ~3.5 only; space carries the bounce", CUR),
        ("call_response_melody", "2-bar call, 2-bar answer; melody talks to itself", CUR),
        ("club_kick_pattern", "THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form", CUR),
        ("bed_squeak_chops", "chopped vocal/stab on straight 8ths riding the kick pattern", CUR),
        ("triplet_break", "bar-4 triplet kick fill (hands-up moment) before the pattern restarts", CUR),
        ("supersaw_pads", "wide detuned saw chords, whole/half notes, fx_widen — the neon wall", CUR),
        ("gated_reverb_snare", "big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law", CUR),
        ("arp_8th", "relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted", CUR),
        ("neon_bass", "8th-note bass locked to the kick root, slightly saturated", CUR),
        ("evolving_pads", "8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush", CUR),
        ("huge_space", "bus reverb at maximum size, generous sends — the room is the instrument", CUR),
        ("slow_filter_drift", "cutoff automation over 16+ bars, barely perceptible motion", CUR),
        ("pentatonic_bells", "sparse bell notes (fmbell), pentatonic, let ring", CUR),
        ("dembow_rhythm", "kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine", CUR),
        ("perreo_bass", "sub doubling the kick roots, short, dark", CUR),
    ]
    for name, desc, prov in tech:
        kg.upsert("Technique", name, prov, desc=desc)

    # ---------------- genres from shipped skills
    genres = [
        ("trap", 130, 160, "F minor", "skill:trap-arrangement@v2",
         ["halftime_groove", "swing_16th", "ghost_notes", "hat_rolls", "808_glide", "layered_kick", "layered_snare"],
         {"name": "trap_drums", "desc": "kick sparse+syncopated; snare beat 3; hats 8th/16th w/ rolls", "prov": "skill:trap-arrangement@v2"},
         {"lufs_lo": -18, "lufs_hi": -9, "band_order": "low>lowmid>mid>himid>high", "clipped": 0, "prov": "skill:mix-headroom@v2"}),
        ("drill", 138, 146, "C# minor", "skill:drill-arrangement@v1",
         ["sliding_808", "ghost_snare_drill", "halftime_groove", "hat_rolls"],
         {"name": "drill_drums", "desc": "UK drill pocket: snare 3, ghosts 3.75/4.25, sliding 808", "prov": "skill:drill-arrangement@v1"},
         {"lufs_lo": -18, "lufs_hi": -9, "band_order": "low>lowmid>mid>himid>high", "clipped": 0, "prov": "skill:drill-arrangement@v1"}),
        ("boombap", 85, 95, "A minor", "skill:boombap-arrangement@v1",
         ["swing_16th", "ghost_notes", "layered_snare", "m7_chords"],
         {"name": "boombap_drums", "desc": "snare 1&3 hard, swing 0.56-0.62, dusty kit", "prov": "skill:boombap-arrangement@v1"},
         {"lufs_lo": -16, "lufs_hi": -9, "band_order": "low>lowmid>mid", "clipped": 0, "prov": "skill:boombap-arrangement@v1"}),
        ("house", 120, 128, "A minor", "skill:house-arrangement@v1",
         ["four_on_floor", "offbeat_bass", "pump_sidechain", "filter_build"],
         {"name": "house_grid", "desc": "kick 1/2/3/4, openhat offbeats, clap 2&4", "prov": "skill:house-arrangement@v1"},
         {"lufs_lo": -14, "lufs_hi": -8, "band_order": "low>lowmid>mid", "clipped": 0, "prov": "skill:house-arrangement@v1"}),
        ("dnb", 170, 176, "E minor", "skill:dnb-arrangement@v1",
         ["breakbeat_chop", "reese_bass", "ghost_notes"],
         {"name": "dnb_break", "desc": "kick 0/2.5 snare 1/3; rides 16ths; sub separate from reese", "prov": "skill:dnb-arrangement@v1"},
         {"lufs_lo": -14, "lufs_hi": -8, "band_order": "low>lowmid>mid", "clipped": 0, "prov": "skill:dnb-arrangement@v1"}),
        ("lofi", 70, 85, "D minor", "skill:lofi-arrangement@v1",
         ["behind_beat_snare", "m7_chords", "dusty_chain", "swing_16th"],
         {"name": "lofi_pocket", "desc": "loose kicks, snare late, everything soft", "prov": "skill:lofi-arrangement@v1"},
         {"lufs_lo": -20, "lufs_hi": -12, "band_order": "low~lowmid>mid", "clipped": 0, "prov": "skill:lofi-arrangement@v1"}),
        # ---------------- GRAPH-ONLY GENRES (no skill exists yet — the compiler's job)
        ("phonk", 130, 145, "C# minor", CUR,
         ["cowbell_lead", "memphis_chant", "tape_saturation", "halftime_groove", "808_glide", "hat_rolls", "swing_16th"],
         {"name": "phonk_drums", "desc": "trap pocket but denser hats; kick doubles before snare; everything saturated", "prov": CUR},
         {"lufs_lo": -16, "lufs_hi": -8, "band_order": "low>lowmid>mid>himid>high", "clipped": 0, "prov": CUR}),
        ("techno", 128, 136, "A minor", CUR,
         ["four_on_floor", "rumble_kick", "modular_stab", "filter_build", "pump_sidechain"],
         {"name": "techno_grid", "desc": "relentless kick, offbeat hats, one stab varied by automation, 16-bar arcs", "prov": CUR},
         {"lufs_lo": -12, "lufs_hi": -7, "band_order": "low>lowmid>mid", "clipped": 0, "prov": CUR}),
        ("ukgarage", 128, 135, "E minor", CUR,
         ["two_step_kick", "shuffle_swing", "chopped_chords", "vocal_chops", "send_reverb", "ghost_notes"],
         {"name": "ukg_2step", "desc": "kick 1 + ~2.75 (no four-floor), snare 2&4 crisp, shuffled hats with ghosts in the gaps", "prov": CUR},
         {"lufs_lo": -16, "lufs_hi": -9, "band_order": "low>lowmid>mid", "clipped": 0, "prov": CUR}),
        ("afrobeats", 98, 110, "A minor", CUR,
         ["log_drum_bass", "triplet_percs", "sparse_kick", "call_response_melody", "swing_16th"],
         {"name": "afro_pocket", "desc": "sparse kick (1, ~3.5), 3:2 perc lattice, light snare/rim on 3 — bounce from space not density", "prov": CUR},
         {"lufs_lo": -16, "lufs_hi": -9, "band_order": "low>lowmid>mid", "clipped": 0, "prov": CUR}),
        ("jerseyclub", 132, 142, "F minor", CUR,
         ["club_kick_pattern", "bed_squeak_chops", "triplet_break", "vocal_chops", "send_reverb"],
         {"name": "jersey_kicks", "desc": "the 5-kick bed (1, 1.5, 2.5, 3, 3.5) three bars, triplet fill bar 4, chops on 8ths", "prov": CUR},
         {"lufs_lo": -14, "lufs_hi": -8, "band_order": "low>lowmid>mid", "clipped": 0, "prov": CUR}),
        ("synthwave", 100, 118, "A minor", CUR,
         ["supersaw_pads", "gated_reverb_snare", "arp_8th", "neon_bass", "width_bloom"],
         {"name": "synthwave_grid", "desc": "kick 1&3 (or four-floor soft), BIG snare 2&4, arps drive 8ths, pads hold the sky", "prov": CUR},
         {"lufs_lo": -15, "lufs_hi": -9, "band_order": "low>lowmid~mid", "clipped": 0, "prov": CUR}),
        ("ambient", 60, 85, "C major", CUR,
         ["evolving_pads", "huge_space", "slow_filter_drift", "pentatonic_bells", "send_reverb"],
         {"name": "ambient_flow", "desc": "no grid tyranny: overlapping 8-16 beat pads, sparse bells, events BREATHE; drums optional/ghosted", "prov": CUR},
         {"lufs_lo": -26, "lufs_hi": -14, "band_order": "", "clipped": 0, "prov": CUR}),
        ("dembow", 88, 100, "D minor", CUR,
         ["dembow_rhythm", "perreo_bass", "vocal_chops", "call_response_melody"],
         {"name": "dembow_grid", "desc": "kick every beat, snare/rim at ~1.75 and ~3.75 (the 3-3-2 lilt), dark sparse melody on top", "prov": CUR},
         {"lufs_lo": -14, "lufs_hi": -8, "band_order": "low>lowmid>mid", "clipped": 0, "prov": CUR}),
    ]
    for name, lo, hi, key, prov, techniques, pattern, mt in genres:
        kg.upsert("Genre", name, prov, bpm_lo=lo, bpm_hi=hi, common_key=key)
        for i, t in enumerate(techniques):
            kg.link("Genre", name, "USES_TECHNIQUE", "Technique", t, weight=round(1.0 - i * 0.08, 2))
        kg.upsert("PatternArchetype", pattern["name"], pattern["prov"], desc=pattern["desc"])
        kg.link("Genre", name, "CHARACTERIZED_BY", "PatternArchetype", pattern["name"])
        mt_name = f"{name}_mix"
        kg.upsert("MixTarget", mt_name, mt["prov"], lufs_lo=mt["lufs_lo"], lufs_hi=mt["lufs_hi"],
                  band_order=mt["band_order"], clipped_samples=mt["clipped"])
        kg.link("Genre", name, "TARGETS", "MixTarget", mt_name)

    # subgenre lattice
    for child, parent in [("drill", "trap"), ("phonk", "trap"), ("techno", "house"),
                          ("lofi", "boombap"), ("ukgarage", "house"), ("jerseyclub", "house")]:
        kg.link("Genre", child, "SUBGENRE_OF", "Genre", parent)

    # sound recipes from the 27-voice bank (sound-palette@v2 + curated for new genres)
    sounds = [
        ("phonk_cowbell", "hat_metal detuned low (source.decay up) OR gm_drums cowbell key 56, through fx_saturate drive 10", CUR, "phonk"),
        ("phonk_chant", "choir kit low register, short notes on offbeats, fx_reverb small dark", CUR, "phonk"),
        ("phonk_808", "kick_808 with 808_glide walking C#1, fx_saturate on the 808 ALLOWED here (genre exception)", CUR, "phonk"),
        ("techno_rumble", "kick_punch + send to verb bus (size 6+) with fx_filter cutoff 150 on the bus return", CUR, "techno"),
        ("techno_stab", "keys_dark single chord, fx_filter + automate cutoff per 4 bars, fx_delay dotted", CUR, "techno"),
        ("ukg_stab", "epiano or keys_dark short m7 stab, fx_filter cutoff ~2500 warm, fx_delay subtle", CUR, "ukgarage"),
        ("ukg_sub", "sub_clean following the kick holes, one octave below the stab root", CUR, "ukgarage"),
        ("afro_log", "sub_clean staccato notes (0.2-0.35 beats) walking the pentatonic + light fx_saturate — the log drum", CUR, "afrobeats"),
        ("jersey_chop", "choir kit high key or pluck2 stab on 8ths, fx_reverb small", CUR, "jerseyclub"),
        ("neon_pad", "pad_motion chords + fx_widen 1.4 + send verb — the horizon", CUR, "synthwave"),
        ("retro_arp", "pluck2 16th arp + fx_delay dotted-8th feedback 0.35", CUR, "synthwave"),
        ("ambient_wash", "pad_motion long notes through TWO reverb buses (one dark size 8, one bright size 4)", CUR, "ambient"),
        ("dembow_rim", "gm_drums rim/snare key at low velocity for the offbeat lilt", CUR, "dembow"),
    ]
    for name, desc, prov, genre in sounds:
        kg.upsert("SoundRecipe", name, prov, desc=desc)
        kg.link("Genre", genre, "CHARACTERIZED_BY", "SoundRecipe", name)

    # conflicts (constitutional mix law)
    kg.upsert("Technique", "widen_low_end", "skill:fx-usage@v1", desc="fx_widen on 808/kick/sub — FORBIDDEN")
    for t in ("808_glide", "layered_kick", "rumble_kick"):
        kg.link("Technique", "widen_low_end", "CONFLICTS_WITH", "Technique", t)

    print("seeded:", kg.stats())

if __name__ == "__main__":
    seed()
