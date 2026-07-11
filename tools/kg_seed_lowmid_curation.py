#!/usr/bin/env python3
"""KG SEED — lowmid-led curation wave 1 (W47, 2026-07-11). Idempotent.

PROVENANCE (the seed law): the breadth census + solo-lane probes
(GENERATION_UPLIFT items 79-81, 2026-07-10/11) measured ambient born with a
REESE bass at gainDb -5 owning 55% of its energy below 120Hz, against a
curated band_order of lowmid>mid>low. A reese is dnb/neuro language; ambient
records ride warm sustained low-PADS. Fix at the DNA layer: ambient's grid
gains "bass_voice": "bass_warm" (harmonic energy 120-500 = the lowmid the
genre wants; the sustained style's long holds make it a warm pad-bass).
loop_gen honors grid.bass_voice as of W47; the blanket-gain alternative was
honest-killed (item 80).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kg import KG, esc

WAVE = [("ambient", {"bass_voice": "bass_warm"},
         "breadth census 2026-07-10 + solo probe: reese owned 55% low vs "
         "lowmid>mid>low target; bass_warm's harmonics ARE the wanted band"),
        ("citypop", {"bass_voice": "bass_warm"},
         "census solo probe 2026-07-11: sub_clean at -5 owned 93% low vs a "
         "lowmid>low>mid target (gap 66.9, worst measured); citypop records "
         "ride warm electric bass — bass_warm is the genre's own sound"),
        ("ambient", {"kick_voice": "kick_punch", "kick_gain_db": -8.0},
         "wave 3 (kick owner): kick_punch_tight at -2 owned 95% low in an "
         "ambient mix — ambient thumps are soft and back (punch voice, -8)"),
        ("citypop", {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
         "wave 3 (kick owner): tight club kick at -2 owned 90% low; citypop "
         "kicks are round and sit with the band (punch voice, -5)"),
        ("afrobeat", {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
         "wave 4 solo probe 2026-07-11: kick_punch_tight@-2 = 90% low while "
         "the bass already carries the wanted lowmid (58%); afrobeat kicks "
         "are warm and sit in the ensemble (punch, -5)"),
        ("gospel", {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
         "wave 4 solo probe 2026-07-11: the loudest lane (rms -17) was the "
         "tight kick at 91% low; the gospel stomp stays but sits with the "
         "band (punch, -5)")]

# wave 5 (ensemble batch): the tight-club-kick-at--2 signature held 4/4 in
# waves 3-4 (kick = the low owner in every probed lowmid-led genre); the
# acoustic/ensemble six get the same curated staging, EACH with a rendered
# per-genre receipt in the shipping commit (blast radius scales receipts).
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 5 ensemble batch 2026-07-11: the 4/4 kick-owner signature; "
          "acoustic ensembles ride soft round kicks in the band")
         for g in ("jazz", "bossanova", "soul", "motown", "blues", "country")]

# wave 6 (jazz-family batch): same acoustic-ensemble law, per-genre rendered
# receipts in the shipping commit.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 6 jazz-family batch 2026-07-11: the 4/4 kick-owner "
          "signature; jazz kits ride soft round kicks under the ensemble")
         for g in ("bebop", "hard_bop", "modal_jazz", "free_jazz",
                   "swing_bigband", "jazzfusion")]

# wave 7 (latin batch): acoustic/percussion ensembles — the kick supports
# the tumbao/clave, never dominates it. Per-genre rendered receipts.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 7 latin batch 2026-07-11: the 4/4 kick-owner signature; "
          "latin kits ride round supportive kicks under the percussion")
         for g in ("salsa", "samba", "merengue", "bachata", "mariachi",
                   "tango")]

# wave 8 (rock/band batch): band kicks PUNCH but the guitars own the mix —
# a touch hotter than the ensembles (-4). Per-genre rendered receipts.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -4.0},
          "wave 8 rock-band batch 2026-07-11: the 4/4 kick-owner signature; "
          "band kicks punch at -4, the guitars carry the wanted lowmid")
         for g in ("rock", "indie_rock", "grunge", "punk", "post_punk",
                   "ska")]

# wave 9 (African ensemble batch): guitar/percussion-led musics — the kick
# supports the ensemble. Per-genre rendered receipts.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 9 African ensemble batch 2026-07-11: the 4/4 kick-owner "
          "signature; guitars/percussion carry the wanted lowmid")
         for g in ("benga", "highlife", "juju", "mbaqanga", "fuji", "sega")]

# wave 10 (world-folk batch): acoustic dance ensembles — the kick marks,
# never dominates. Per-genre rendered receipts.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 10 world-folk batch 2026-07-11: the 4/4 kick-owner "
          "signature; the ensemble carries the wanted lowmid")
         for g in ("celtic", "klezmer", "flamenco", "forro", "calypso",
                   "chaabi")]

# wave 11 (MENA/Asia folk): ensemble kicks + the stray-reese sweep's clear
# acoustic cases (oud/harmonium traditions ride warm low strings, never a
# reese). Per-genre rendered receipts.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 11 MENA/Asia folk batch 2026-07-11: the 4/4 kick-owner "
          "signature; the ensemble carries the wanted lowmid")
         for g in ("arabesk", "khaleeji", "qawwali", "luk_thung", "bhangra",
                   "ethio_jazz")]
WAVE += [(g, {"bass_voice": "bass_warm"},
          "wave 11 stray-reese sweep 2026-07-11: a reese in an oud/"
          "harmonium tradition — warm low strings are the genre's voice")
         for g in ("arabesk", "khaleeji", "qawwali")]

# wave 12 (string-wall batch): metal/stoner/shoegaze = band kicks (-4) +
# bass GUITAR warmth (their reeses were sweep strays); fado/morna = acoustic
# ensembles (-5) + warm low strings; spiritual_jazz = ensemble kick.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -4.0,
              "bass_voice": "bass_warm"},
          "wave 12 string-wall 2026-07-11: band kick at -4; the bass GUITAR "
          "(not a reese) carries the wall's lowmid")
         for g in ("stoner_rock", "shoegaze")]
WAVE += [("metal", {"kick_voice": "kick_punch", "kick_gain_db": -6.0,
                    "bass_voice": "bass_warm"},
          "wave 12 probe 2026-07-11: 32 double-kick hits/4 bars sum to the "
          "loudest lane at -4 (rms -13.9) — dense kicks mix LOWER per hit; "
          "-6 lets the rhythm guitars lead as the order wants")]
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0,
              "bass_voice": "bass_warm"},
          "wave 12 string-wall 2026-07-11: acoustic ensemble; warm low "
          "strings, soft kick")
         for g in ("fado", "morna")]
WAVE += [("spiritual_jazz", {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 12 string-wall 2026-07-11: the ensemble kick law")]

# wave 13 (synth-wall batch): warm synth basses (the sweep's strays —
# vaporwave IS smooth-jazz warmth, chillwave rides dusty warm subs);
# atmospheric genres take the softest kicks.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0,
              "bass_voice": "bass_warm"},
          "wave 13 synth-wall 2026-07-11: warm synth bass, soft kick — the "
          "haze carries the lowmid")
         for g in ("chillwave", "vaporwave")]
WAVE += [("synthpop", {"kick_voice": "kick_punch", "kick_gain_db": -5.0,
                       "bass_voice": "bass_warm"},
          "wave 13 synth-wall 2026-07-11: sub_clean owned 77% low (the "
          "citypop class) — synthpop rides warm analog synth bass"),
        ("balearic", {"kick_voice": "kick_punch", "kick_gain_db": -5.0,
                      "bass_voice": "bass_warm"},
         "wave 13 synth-wall 2026-07-11: sub_clean owned 79% low — sunset "
         "bass is warm and round, never a pure sub")]
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -7.0,
              "bass_voice": "bass_warm"},
          "wave 13 synth-wall 2026-07-11: atmospheric genres — the kick is "
          "a distant pulse, warmth carries the field")
         for g in ("dungeon_synth", "drone")]

# wave 14 (the closing tail): per-genre judgments — electronic-body kicks
# keep punch (-4, the genre); acoustic corridos + orchestral get warmth.
WAVE += [(g, {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 14 closing tail 2026-07-11 (stepped -4 -> -5 by measurement: "
          "the seven held a uniform 20-27 residual at -4 — the balearic "
          "class); pop kicks sit with the band")
         for g in ("ebm", "industrial", "hyperpop", "jpop", "nightcore",
                   "new_jack_swing", "singeli")]
WAVE += [("idm", {"kick_voice": "kick_punch", "kick_gain_db": -5.0},
          "wave 14 closing tail 2026-07-11: glitch kicks sit soft"),
        ("corridos_tumbados", {"kick_voice": "kick_punch",
                               "kick_gain_db": -5.0,
                               "bass_voice": "bass_warm"},
         "wave 14 closing tail 2026-07-11: tuba/bajo warmth IS the genre's "
         "low voice; ensemble kick"),
        ("orchestral_cinematic", {"kick_voice": "kick_punch",
                                  "kick_gain_db": -7.0,
                                  "bass_voice": "bass_warm"},
         "wave 14 closing tail 2026-07-11: low strings, distant percussion "
         "— never a club kick or a reese")]

WAVE += [(g, {"bass_voice": "bass_warm"},
          "wave 14b 2026-07-11: sub/reese owned 59-93% low against a "
          "lowmid-led order — pop/body genres ride warm gritty bass (the "
          "grit IS lowmid); honoring the curated order")
         for g in ("ebm", "industrial", "hyperpop", "jpop", "nightcore",
                   "new_jack_swing", "singeli", "idm")]

WAVE += [("metal", {"color_gain_db": -9.0},
          "W61 2026-07-11: the chug wall exists but sat at pad level (-14) "
          "— metal rhythm guitar runs hot; -9 lets the wall lead")]

WAVE += [("fuji", {"ghost": [2, 6, 9, 13], "ghost_voice": "dhol",
                   "ghost_gain_db": -7.0, "ghost_pitch": 55},
          "W62 2026-07-11: THE PALETTE GAP closes — fuji had no lowmid "
          "instrument (vocal palette + kick only); the dundun (talking "
          "drum, dhol voice) answers on the offbeats as the tradition does")]

# W94 THE DNB POCKET (critic round 2026-07-11): dnb-family basses were
# 2-note DRONES ("bass near-extinct, 0.4 notes/bar" — real dnb rolls).
# The new "wub" style: anchor hold + syncopated stabs on the break pocket.
WAVE += [("dnb", {"bass_style": "wub"},
          "W94: the reese moves — hold... wub-wub, ~2.5 notes/bar")]
WAVE += [("jungle", {"bass_style": "wub"},
          "W94: same family truth over the amen")]
WAVE += [("neurofunk", {"bass_style": "wub"},
          "W94: neuro IS bass movement (the W79 gain-freeze stands; the "
          "style was the missing half)")]

# W79 THE CATALOG CLOSES (radar sweeps 10a/10b, 2026-07-11): the final 16
# defects of the 202-genre census. Healthy majority again left alone.
WAVE += [("khaleeji", {"color_voice": "strings_stacc", "color_gain_db": -10.0,
                       "bass_gain_db": -8.0},
          "W79: gulf strings pair; staging")]
WAVE += [("kompa", {"color_voice": "sax_section", "color_gain_db": -9.0,
                    "lead": {"voice": "pluck", "octave": 4, "bars": 2,
                             "steps": [[0, 1, 2], [4, 3, 1], [6, 5, 2], [12, 4, 2],
                                       [16, 3, 2], [20, 5, 1], [24, 4, 2], [28, 2, 2]]},
                    "lead_gain_db": -7.0},
          "W79: kompa born melodically thin — the horn section pair + the "
          "picked guitar line (mono, one player)")]
WAVE += [("kuduro", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                              "steps": [[0, 1, 1], [4, 1, 1], [8, 4, 1], [12, 3, 1],
                                        [16, 5, 1], [20, 4, 1], [24, 3, 1], [28, 1, 1]]},
                     "lead_gain_db": -7.0, "bass_gain_db": -8.0, "kick_gain_db": -4.0},
          "W79: the chant stab over the batida")]
WAVE += [("mariachi", {"color_voice": "sax_section", "color_gain_db": -8.0,
                       "lead": {"voice": "pluck", "octave": 4, "bars": 2,
                                "steps": [[0, 1, 2], [4, 3, 2], [8, 5, 2], [14, 4, 1],
                                          [16, 6, 2], [22, 5, 1], [24, 3, 2], [28, 2, 2]]},
                       "lead_gain_db": -7.0},
          "W79: mariachi born with NO horns or vihuela — the section "
          "(vibrato pair) + the picked line")]
WAVE += [("math_rock", {"lead_gain_db": -3.0, "color_gain_db": -5.0,
                        "bass_gain_db": -8.0, "kick_gain_db": -4.0},
          "W79: the chime pairs were buried")]
WAVE += [("midwest_emo", {"lead_gain_db": -3.0, "color_gain_db": -5.0,
                          "kick_gain_db": -4.0, "bass_gain_db": -8.0},
          "W79: same family staging")]
WAVE += [("morna", {"lead_gain_db": -4.0, "color_gain_db": -7.0},
          "W79: staging; HONEST-INTIMATE declared (fado's cousin — voice+"
          "guitar truth; 0.94 -> 0.89 real, narrow is its room)")]
WAVE += [("neurofunk", {"lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                                 "steps": [[0, 1, 2], [8, 3, 2], [16, 4, 2], [24, 2, 2]]},
                        "lead_gain_db": -8.0, "color_voice": "pad_motion",
                        "color_gain_db": -12.0},
          "W79: neuro born melody-naked; the reese BASS stays untouched "
          "(the genre) — sparse dark keys + pad air only")]
WAVE += [("post_punk", {"lead": {"voice": "guitar_grit", "octave": 4, "bars": 2,
                                 "steps": [[0, 1, 1], [2, 1, 1], [4, 3, 2], [8, 5, 1],
                                           [12, 4, 2], [16, 1, 1], [18, 1, 1], [20, 6, 2],
                                           [24, 5, 2], [28, 4, 1]]},
                        "lead_gain_db": -6.0},
          "W79: the wiry guitar line (two-amp pair) over the Hook bass — "
          "post_punk had NO melodic lane")]
WAVE += [("post_rock", {"lead_gain_db": -3.0, "color_gain_db": -5.0,
                        "bass_gain_db": -8.0, "kick_gain_db": -4.0},
          "W79: the chime wall staged up")]
WAVE += [("rebetiko", {"lead_gain_db": -4.0, "color_gain_db": -8.0,
                       "kick_gain_db": -4.0, "bass_gain_db": -7.0},
          "W79: staging (bouzouki line forward)")]
WAVE += [("rocksteady", {"color_gain_db": -7.0, "bass_gain_db": -7.0,
                         "kick_gain_db": -4.0},
          "W79: the hammond Leslie skank up; the bass stays king (modest)")]
WAVE += [("samba", {"color_voice": "sax_section", "color_gain_db": -9.0,
                    "lead": {"voice": "pluck", "octave": 4, "bars": 2,
                             "steps": [[0, 1, 1], [2, 3, 1], [4, 5, 2], [8, 4, 1],
                                       [10, 3, 1], [12, 5, 2], [16, 6, 2], [20, 5, 1],
                                       [22, 4, 1], [24, 3, 2], [28, 2, 1]]},
                    "lead_gain_db": -7.0},
          "W79: samba born percussion-only — cavaquinho line (mono) + the "
          "horn section")]
WAVE += [("sexy_drill", {"lead": {"voice": "fmbell", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 2], [6, 3, 2], [12, 4, 2],
                                            [16, 5, 3], [24, 4, 2], [28, 3, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -8.0,
                         "kick_gain_db": -3.5},
          "W79: the jersey/latin bell treatment (trap family)")]
WAVE += [("shoegaze", {"color_gain_db": -7.0, "lead_gain_db": -6.0,
                       "bass_gain_db": -8.0},
          "W79: THE WALL WIDE — shoegaze's fuzz pair ran buried at -18dB "
          "width; the whole genre is that wall")]
WAVE += [("singeli", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                               "steps": [[0, 1, 1], [2, 1, 1], [4, 3, 1], [6, 4, 1],
                                         [8, 5, 1], [10, 4, 1], [12, 3, 1], [14, 1, 1],
                                         [16, 1, 1], [18, 3, 1], [20, 4, 1], [22, 5, 1],
                                         [24, 6, 1], [26, 5, 1], [28, 4, 1], [30, 3, 1]]},
                      "lead_gain_db": -6.0, "bass_gain_db": -8.0},
          "W79: the frantic 16th line IS singeli's engine")]

# W78 THE DARK TAIL (radar sweep 9, 2026-07-11): crunk/driftphonk/goa at
# 94-95 pct low with corr ~1.0; flamenco/gnawa/idm/industrial palette gaps;
# dembow/ebm/fado staging. The healthy majority (doom_metal/fuji/free_jazz/
# gamelan/dangdut...) left alone.
WAVE += [("crunk", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                             "steps": [[0, 1, 1], [4, 1, 1], [8, 3, 2], [12, 1, 1],
                                       [16, 4, 1], [20, 4, 1], [24, 5, 2], [28, 3, 1]]},
                    "lead_gain_db": -7.0, "color_voice": "strings_stacc",
                    "color_gain_db": -9.0, "bass_gain_db": -8.0,
                    "kick_gain_db": -3.5},
          "W78: crunk born drums+808 (94.8 pct low) — the chant + dark "
          "orchestral stabs ARE dirty south")]
WAVE += [("driftphonk", {"lead": {"voice": "fmbell", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 1], [2, 3, 1], [4, 5, 1], [6, 4, 1],
                                            [8, 3, 1], [10, 1, 1], [12, 4, 1], [14, 3, 1],
                                            [16, 1, 1], [18, 3, 1], [20, 5, 1], [22, 6, 1],
                                            [24, 5, 1], [26, 4, 1], [28, 3, 1], [30, 2, 1]]},
                         "lead_gain_db": -6.0, "color_voice": "keys_dark",
                         "color_gain_db": -11.0, "bass_gain_db": -8.0},
          "W78: driftphonk at corr 1.00 — THE COWBELL LINE (fmbell pair, "
          "driving 8ths) is the entire genre signature")]
WAVE += [("flamenco", {"lead": {"voice": "pluck", "octave": 4, "bars": 2,
                               "steps": [[0, 1, 2], [3, 2, 1], [6, 3, 2], [10, 4, 1],
                                         [12, 5, 2], [16, 4, 2], [20, 3, 1], [22, 2, 2],
                                         [26, 1, 3]]},
                       "lead_gain_db": -6.0, "color_voice": "pad_motion",
                       "color_gain_db": -13.0},
          "W78: flamenco born drums-only — the nylon line stays MONO (one "
          "guitarist, the reggaeton law); a whisper pad pair carries air")]
WAVE += [("gnawa", {"lead": {"voice": "pluck", "octave": 3, "bars": 2,
                             "steps": [[0, 1, 2], [4, 1, 1], [6, 3, 2], [10, 4, 1],
                                       [12, 1, 2], [16, 1, 2], [20, 3, 1], [22, 4, 2],
                                       [26, 3, 1], [28, 1, 2]]},
                    "lead_gain_db": -6.0, "hat_gain_db": -7.0,
                    "bass_gain_db": -8.0},
          "W78: gnawa = gimbri line (LOW register, mono — one player) + "
          "the qraqeb metal up; trance-bass truth kept")]
WAVE += [("goa", {"lead": {"voice": "pluck2", "octave": 4, "bars": 2,
                           "steps": [[0, 1, 1], [2, 1, 1], [4, 3, 1], [6, 1, 1],
                                     [8, 4, 1], [10, 3, 1], [12, 5, 1], [14, 4, 1],
                                     [16, 1, 1], [18, 1, 1], [20, 6, 1], [22, 5, 1],
                                     [24, 4, 1], [26, 3, 1], [28, 2, 1], [30, 1, 1]]},
                  "lead_gain_db": -6.0, "bass_gain_db": -8.0},
          "W78: goa at 94.7 pct low — the squelching 16th line over the "
          "rolling bass IS goa")]
WAVE += [("idm", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                           "steps": [[0, 1, 2], [5, 3, 1], [7, 5, 2], [11, 4, 1],
                                     [16, 6, 2], [21, 5, 1], [25, 3, 2], [29, 2, 2]]},
                  "lead_gain_db": -7.0, "color_voice": "pad_motion",
                  "color_gain_db": -11.0, "bass_gain_db": -8.0},
          "W78: idm born drums+sub — warm pads + an off-grid melody line "
          "(aphex language)")]
WAVE += [("industrial", {"lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                                  "steps": [[0, 1, 2], [6, 1, 2], [12, 3, 2],
                                            [16, 1, 2], [22, 4, 2], [28, 1, 2]]},
                         "lead_gain_db": -7.0, "color_voice": "supersaw_fat",
                         "color_gain_db": -9.0, "bass_gain_db": -8.0},
          "W78: industrial born drums+sub — the harsh saw wall + a "
          "hammering dark line")]
WAVE += [("dembow", {"lead_gain_db": -6.0, "kick_gain_db": -4.0},
          "W78: the pair was buried; bass UNTOUCHED (the reggaeton law — "
          "dembow is bass-forward mono-ish by identity)")]
WAVE += [("ebm", {"bass_gain_db": -8.0, "color_gain_db": -8.0,
                  "kick_gain_db": -4.5, "hat_gain_db": -9.0},
          "W78: staging — the sequenced bassline stays the star")]
WAVE += [("fado", {"lead_gain_db": -5.0, "color_gain_db": -9.0},
          "W78: staging (guitarra pair was buried)")]

# W77 THE WORLD TAIL (radar sweep 8, 2026-07-11): the roots family is
# mostly HEALTHY (solo-player mono leads are their truth — bachata/bossa/
# bebop/bhangra left untouched). Nine true defects, all proven classes.
WAVE += [("baltimore_club", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                                      "steps": [[0, 5, 1], [2, 5, 1], [4, 4, 2],
                                                [8, 3, 1], [16, 5, 1], [18, 5, 1],
                                                [20, 6, 2], [24, 4, 2]]},
                             "lead_gain_db": -7.0, "bass_gain_db": -8.0},
          "W77: bmore club born four lanes — the chopped vocal stab over "
          "the think break IS the genre")]
WAVE += [("bounce", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                              "steps": [[0, 1, 1], [2, 1, 1], [4, 3, 1], [6, 1, 1],
                                        [16, 4, 1], [18, 4, 1], [20, 5, 1], [22, 3, 1]]},
                     "lead_gain_db": -7.0, "bass_gain_db": -8.0},
          "W77: NOLA bounce = the triggerman chant (breath pair)")]
WAVE += [("breakbeat_hardcore", {"lead": {"voice": "supersaw", "octave": 5, "bars": 2,
                                          "steps": [[0, 1, 2], [4, 3, 2], [8, 5, 2],
                                                    [16, 6, 2], [20, 5, 2], [24, 4, 2]]},
                                 "lead_gain_db": -5.0, "color_voice": "jazz_piano",
                                 "color_octave_shift": 1, "color_gain_db": -8.0,
                                 "bass_gain_db": -9.0},
          "W77: 92-era rave born drums+sub (93.6 pct low) — hoover lead + "
          "PIANO STABS voiced up are the whole culture")]
WAVE += [("celtic", {"lead": {"voice": "flute_lead", "octave": 5, "bars": 2,
                              "steps": [[0, 1, 2], [3, 2, 1], [4, 3, 2], [8, 5, 2],
                                        [12, 4, 2], [16, 6, 2], [20, 5, 2],
                                        [24, 3, 2], [28, 2, 2]]},
                     "lead_gain_db": -7.0, "color_voice": "pad_motion",
                     "color_gain_db": -12.0},
          "W77: celtic born drums-only — the whistle line (MONO, one "
          "player: genre truth) over a soft drone pad pair")]
WAVE += [("afrobeat", {"color_voice": "sax_section", "color_gain_db": -9.0,
                       "bass_gain_db": -7.0},
          "W77: the horn SECTION (vibrato pair) is afrobeat's answer "
          "voice — its mono organ bed read corr 0.93")]
WAVE += [("arabesk", {"color_gain_db": -9.0, "bass_gain_db": -8.0,
                      "kick_gain_db": -4.0, "lead_gain_db": -5.0,
                      "hat_gain_db": -9.0},
          "W77: the string pair was buried (staging)")]
WAVE += [("black_metal", {"bass_gain_db": -8.0, "color_gain_db": -8.0,
                          "kick_gain_db": -4.0},
          "W77: the tremolo wall pair hotter, blast kick eased a step")]
WAVE += [("chaabi", {"color_gain_db": -9.0, "bass_gain_db": -8.0,
                     "kick_gain_db": -4.0, "lead_gain_db": -5.0,
                     "hat_gain_db": -9.0},
          "W77: staging (pairs existed, buried)")]
WAVE += [("champeta", {"bass_gain_db": -8.0, "kick_gain_db": -4.0,
                       "lead_gain_db": -6.0},
          "W77: one dose — 75.7 pct low, image already decent")]

# W76 THE NET-MUSIC + RETRO-POP BATCH (radar sweep 7, 2026-07-11):
# 11 true defects of 24 swept (boogie/pluggnb/wave/glitchcore carry mono
# lanes but healthy images — left alone).
WAVE += [("jpop", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                            "steps": [[0, 1, 2], [4, 3, 1], [6, 5, 2], [10, 6, 2],
                                      [16, 5, 2], [20, 4, 1], [22, 3, 2], [26, 2, 3]]},
                   "lead_gain_db": -6.0, "color_voice": "jazz_piano",
                   "color_octave_shift": 1, "color_gain_db": -9.0,
                   "kick_gain_db": -3.5},
          "W76: jpop born four lanes — the bright piano bed (voiced UP per "
          "the spectrum map) + a singable pluck hook")]
WAVE += [("italo_disco", {"bass_gain_db": -10.0, "kick_gain_db": -4.0,
                          "arp_gain_db": -9.0, "color_gain_db": -10.0},
          "W76: 91 pct low buried the arps that ARE italo — staging")]
WAVE += [("new_jack_swing", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                      "steps": [[0, 1, 1], [3, 3, 1], [6, 5, 2],
                                                [10, 4, 1], [16, 6, 2], [19, 5, 1],
                                                [22, 4, 2], [26, 3, 2]]},
                             "lead_gain_db": -6.0, "color_voice": "jazz_piano",
                             "color_octave_shift": 1, "color_gain_db": -9.0},
          "W76: NJS born four lanes — the bright keys + stab hook over the "
          "swingbeat")]
WAVE += [("hyperpop", {"lead": {"voice": "supersaw", "octave": 5, "bars": 2,
                                "steps": [[0, 1, 2], [4, 5, 2], [8, 6, 2], [12, 5, 2],
                                          [16, 8, 2], [20, 6, 2], [24, 5, 2], [28, 4, 2]]},
                       "lead_gain_db": -5.0, "color_voice": "vox_pad",
                       "color_gain_db": -10.0, "bass_gain_db": -8.0},
          "W76: hyperpop born kick/clap/hat/bass — the LOUD supersaw wall "
          "+ vox pad IS the genre's whole maximalist face")]
WAVE += [("dariacore", {"bass_gain_db": -9.0, "lead_gain_db": -5.0,
                        "color_gain_db": -10.0, "kick_gain_db": -4.0},
          "W76: maximalist mashcore staging — hooks to the front")]
WAVE += [("witch_house", {"lead": {"voice": "formant_vox", "octave": 3, "bars": 2,
                                   "steps": [[0, 1, 4], [8, 3, 3], [16, 4, 4], [24, 2, 3]]},
                          "lead_gain_db": -8.0, "bass_gain_db": -8.0,
                          "kick_gain_db": -4.0},
          "W76: witch house at 90.6 pct low — the ghosted vocal drone "
          "(breath pair, LOW register) is the genre's murk; kept dark")]
WAVE += [("nightcore", {"lead": {"voice": "supersaw", "octave": 5, "bars": 2,
                                 "steps": [[0, 5, 2], [4, 6, 2], [8, 8, 2], [12, 6, 2],
                                           [16, 5, 2], [20, 4, 2], [24, 5, 2], [28, 6, 2]]},
                        "lead_gain_db": -5.0, "color_voice": "pad_motion",
                        "color_gain_db": -11.0, "bass_gain_db": -8.0},
          "W76: nightcore born four lanes — sped-up eurodance saw hooks")]
WAVE += [("happy_hardcore", {"lead": {"voice": "supersaw", "octave": 5, "bars": 2,
                                      "steps": [[0, 1, 2], [4, 3, 2], [8, 5, 2], [12, 6, 2],
                                                [16, 8, 2], [20, 6, 2], [24, 5, 2], [28, 3, 2]]},
                             "lead_gain_db": -5.0, "color_voice": "jazz_piano",
                             "color_octave_shift": 1, "color_gain_db": -8.0,
                             "bass_gain_db": -9.0},
          "W76: HHC born four lanes — the PIANO STABS (voiced up) + "
          "euphoric saw lead ARE happy hardcore; the kick stays")]
WAVE += [("gabber", {"color_voice": "supersaw", "color_gain_db": -7.0,
                     "bass_gain_db": -11.0, "hat_gain_db": -7.0,
                     "kick_voice": "kick_gabber"},
          "W76: the HOOVER (detuned saw pair) + THE MINTED KICK — the judge "
          "ruled staging out twice ('gabber requires treble presence; its "
          "core character is intentional distortion'): kick_gabber.dsp is "
          "an overdriven kick whose drive/fold/screech-band spectrum IS "
          "the genre (22 pct mid-to-8k solo vs the clean kick's 3)")]
WAVE += [("breakcore", {"lead": {"voice": "supersaw", "octave": 5, "bars": 2,
                                 "steps": [[0, 1, 2], [6, 5, 2], [12, 6, 2],
                                           [16, 8, 2], [22, 6, 2], [28, 5, 2]]},
                        "lead_gain_db": -6.0, "color_voice": "pad_motion",
                        "color_gain_db": -12.0, "bass_gain_db": -8.0},
          "W76: breakcore born drums+bass — rave stabs over the amen "
          "chaos")]
WAVE += [("darksynth", {"bass_gain_db": -9.0, "lead_gain_db": -5.0,
                        "color_gain_db": -10.0, "lead_voice": "supersaw_fat",
                        "color_voice": "pad_motion", "kick_gain_db": -4.0},
          "W76: synthwave's evil twin — but its lead AND color were both "
          "MONO REESES (wrong DNA; reese is a bass voice). supersaw_fat "
          "lead pair + motion pad pair; the lead_voice rail born for it")]

# W75 THE CLUB TAIL (radar sweep 6, 2026-07-11): 18/24 defective — the
# house/techno family tree + breaks/triphop. Same licensed-batch rhythm.
WAVE += [("detroit_techno", {"color_voice": "strings_stacc", "color_gain_db": -11.0,
                             "lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                      "steps": [[0, 1, 1], [4, 5, 2], [10, 4, 1],
                                                [16, 6, 2], [22, 5, 1], [26, 3, 2]]},
                             "lead_gain_db": -7.0, "bass_gain_db": -9.0},
          "W75: detroit born drums+sub (corr 1.00) — hi-tek soul IS the "
          "string stab pair + a sparse lead call")]
WAVE += [("minimal_techno", {"color_voice": "keys_dark", "color_gain_db": -12.0,
                             "bass_gain_db": -9.0},
          "W75: 87 pct low + corr 1.00 is EMPTY, not minimal — the dub "
          "chord stab (detune pair, sparse held bed) is minimal's own "
          "furniture; absence stays the language elsewhere")]
WAVE += [("3step", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                             "steps": [[0, 5, 2], [6, 4, 1], [10, 3, 2], [16, 6, 2],
                                       [22, 5, 1], [26, 4, 2]]},
                    "lead_gain_db": -7.0, "bass_gain_db": -9.0},
          "W75: 3step born kick/hat/bass only — the vocal-chop line rides "
          "the swung grid (breath pair)")]
WAVE += [("breaks", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                              "steps": [[0, 1, 2], [6, 3, 2], [12, 5, 2], [16, 4, 2],
                                        [22, 3, 2], [28, 2, 2]]},
                     "lead_gain_db": -6.0, "color_voice": "pad_motion",
                     "color_gain_db": -12.0, "bass_gain_db": -8.0},
          "W75: big-beat-adjacent breaks had no synth face — stab hook + "
          "pad bed over the break")]
WAVE += [("ghettotech", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 1], [2, 1, 1], [6, 5, 1], [10, 4, 1],
                                            [16, 1, 1], [18, 1, 1], [22, 6, 1], [26, 5, 1]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -7.0},
          "W75: detroit booty tech = electro stab hook over the 808; bass "
          "stays hot (the genre IS low)")]
WAVE += [("triphop", {"color_voice": "keys_dark", "color_gain_db": -11.0,
                      "lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                               "steps": [[0, 1, 3], [8, 4, 2], [16, 5, 3], [24, 3, 3]]},
                      "lead_gain_db": -8.0, "bass_gain_db": -7.0},
          "W75: triphop born drums+bass — the dark jazz keys bed + sparse "
          "melancholy line ARE bristol; bass stays heavy (identity)")]
WAVE += [("acid_house", {"bass_gain_db": -7.0, "color_gain_db": -11.0,
                         "kick_gain_db": -4.0, "bass_octave_shift": 1,
                         "bass_params": {"cutoff": 620.0, "res": 11.0}},
          "W75: 95.9 pct low — but the 303 VOICE measured 50 pct mid at C4 "
          "(voice_spectrum): the lane just played it on the sub floor with "
          "cutoff 300. Octave up + cutoff 620/res 11 = the squeal; the "
          "bass_octave_shift + bass_params rails born for it")]
WAVE += [("chicago_house", {"bass_gain_db": -9.0, "color_gain_db": -10.0,
                            "kick_gain_db": -4.0, "hat_gain_db": -9.0},
          "W75: the jack organ stabs forward, sub eased under the kick")]
WAVE += [("deephouse", {"bass_gain_db": -9.0, "color_gain_db": -10.0,
                        "kick_gain_db": -4.0},
          "W75: 89 pct low buried the pad pair — deep house IS the warm "
          "chord wash")]
WAVE += [("tech_house", {"bass_gain_db": -9.0, "color_gain_db": -10.0,
                         "kick_gain_db": -4.0},
          "W75: staging (75 pct low, corr 0.95)")]
WAVE += [("melodic_techno", {"bass_gain_db": -10.0, "arp_gain_db": -10.0,
                             "color_gain_db": -10.0, "kick_gain_db": -4.0},
          "W75: the arp/pad pairs ARE the genre — staged up over the sub")]
WAVE += [("dub_techno", {"color_gain_db": -9.0, "bass_gain_db": -8.0,
                         "kick_gain_db": -4.0},
          "W75: the echoing dub CHORD is the whole genre — to the front")]
WAVE += [("french_house", {"bass_gain_db": -10.0, "color_gain_db": -9.0,
                           "kick_gain_db": -4.0, "hat_gain_db": -8.0},
          "W75: 94.5 pct low — filter disco lives in the loop's mids "
          "(color pair front, sub deep under)")]
WAVE += [("speed_garage", {"bass_gain_db": -8.0, "color_gain_db": -10.0,
                           "kick_gain_db": -4.0},
          "W75: warping bass stays identity; the organ/chop mids lift")]
WAVE += [("bassline", {"bass_gain_db": -7.0, "color_gain_db": -10.0,
                       "kick_gain_db": -4.0},
          "W75: bassline's BASS is the star (modest -7); mids breathe")]
WAVE += [("big_beat", {"color_gain_db": -10.0, "bass_gain_db": -8.0,
                       "kick_gain_db": -4.0},
          "W75: staging (74.7 pct, corr 0.96)")]
WAVE += [("footwork", {"bass_gain_db": -8.0, "lead_gain_db": -5.0,
                       "kick_gain_db": -4.0, "hat_gain_db": -13.0},
          "W75: the juke 808 eased under the vox-pad pair")]
WAVE += [("hard_techno", {"bass_gain_db": -9.0, "color_gain_db": -10.0,
                          "kick_gain_db": -3.0},
          "W75: the kick IS hard techno (barely eased); rumble staged "
          "under, color up")]

# W73 THE LONG TAIL BATCH (radar sweep 5, 2026-07-11): 24-genre classified
# census — 9 palette gaps, 6 no-pair, 6 staging, only 4 healthy. Licensed
# per W51 (per-genre receipts in the commit); every value genre-true.
WAVE += [("jungle", {"color_voice": "pad_motion", "color_gain_db": -12.0,
                     "lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                              "steps": [[0, 1, 3], [8, 4, 2], [14, 3, 2],
                                        [16, 5, 3], [24, 4, 3]]},
                     "lead_gain_db": -8.0, "bass_gain_db": -7.0},
          "W73: jungle born drums+sub only (-23.9 width) — dark pad bed + "
          "sparse keys stabs over the break; the Amen stays the star")]
WAVE += [("moombahton", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 2], [4, 3, 2], [8, 5, 3],
                                            [14, 4, 2], [16, 6, 2], [20, 5, 2],
                                            [24, 4, 3], [30, 3, 2]]},
                         "lead_gain_db": -6.0, "color_voice": "pad_motion",
                         "color_gain_db": -12.0, "bass_gain_db": -9.0,
                         "kick_gain_db": -4.0},
          "W73: moombahton born FOUR lanes (-31.3 width, corr 1.00 — the "
          "worst ever measured); the genre is reggaeton x house BIG synth "
          "hooks over the dembow half-time")]
WAVE += [("afro_house", {"color_voice": "pad_motion", "color_gain_db": -12.0,
                         "lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                  "steps": [[0, 5, 2], [6, 4, 2], [12, 3, 2],
                                            [16, 6, 2], [22, 5, 2], [28, 4, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -8.0},
          "W73: afro_house was percussion+sub only — organic pads + a "
          "sparse pluck call over the drums")]
WAVE += [("baile_funk", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                                  "steps": [[0, 1, 2], [6, 3, 1], [10, 1, 2],
                                            [16, 4, 2], [22, 3, 1], [26, 1, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -8.0},
          "W73: baile funk born drums+808 (-24.2) — the MC vocal stab IS "
          "the melodic furniture (formant breath pair)")]
WAVE += [("grime", {"lead": {"voice": "pluck2", "octave": 4, "bars": 2,
                             "steps": [[0, 1, 2], [3, 1, 1], [6, 3, 2], [10, 2, 2],
                                       [16, 1, 2], [19, 4, 1], [22, 3, 2], [28, 2, 3]]},
                    "lead_gain_db": -6.0, "bass_gain_db": -9.0},
          "W73: grime at 93 pct low with NO riff — the 8-bar square riff "
          "is the genre's whole face; sub eased under it")]
WAVE += [("jerseyclub", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                                  "steps": [[0, 5, 1], [2, 5, 1], [4, 4, 2],
                                            [10, 3, 1], [16, 5, 1], [18, 5, 1],
                                            [20, 6, 2], [26, 4, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -8.0},
          "W73: jerseyclub born kick/clap/hat/bass — the chopped vocal "
          "stab rides the bed-squeak kick pattern (breath pair)")]
WAVE += [("latin_trap", {"lead": {"voice": "fmbell", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 2], [6, 3, 2], [12, 4, 2],
                                            [16, 5, 3], [24, 4, 2], [28, 3, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -9.0,
                         "kick_gain_db": -3.5},
          "W73: latin_trap at 94.7 pct low — the dark bell hook (bright "
          "split pair) over an eased 808; trap-family truth")]
WAVE += [("memphis_rap", {"lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                                   "steps": [[0, 1, 3], [8, 2, 2], [12, 1, 2],
                                             [16, 4, 3], [24, 2, 2], [28, 1, 2]]},
                          "lead_gain_db": -7.0, "color_voice": "keys_dark",
                          "color_gain_db": -12.0, "bass_gain_db": -8.0},
          "W73: memphis born drums+808 — the lo-fi dark keys loop IS "
          "memphis (detune pair bed + sparse hook)")]
WAVE += [("miami_bass", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                                  "steps": [[0, 1, 1], [2, 1, 1], [4, 5, 2],
                                            [8, 4, 1], [12, 3, 2], [16, 1, 1],
                                            [18, 1, 1], [20, 6, 2], [26, 5, 2]]},
                         "lead_gain_db": -7.0, "bass_gain_db": -7.0},
          "W73: miami bass keeps its 808 showcase (the genre IS the low "
          "end) but gains the electro stab hook the records ride")]
WAVE += [("amapiano", {"bass_gain_db": -10.0, "color_voice": "jazz_piano",
                       "color_gain_db": -8.0, "hat_gain_db": -13.0,
                       "color_octave_shift": 1},
          "W73: THE PIANO, fourth pass. Judge taught it verbatim: 'pianos "
          "define the genre in the midrange' — jazz_piano bed at -9 (mid "
          "band was 2.4 pct; keys_dark voiced too low to fill it), log 808 "
          "eased -10. Earlier tells: pad_motion bed "
          "= 'unnaturally bright' (reverted); bare take = 'tonally thin, "
          "9.6 pct lowmid vs 22 authentic warmth' + centroid contradiction "
          "(hats vs 85 pct bass). Amapiano is house-rooted JAZZ KEYS music "
          "— keys_dark detune pair at -10 brings the warmth DARK, hats "
          "eased -13. MixTarget lufs_lo -16 -> -14 (judge: 'unrealistically "
          "quiet') rode the first pass")]
WAVE += [("future_garage", {"color_voice": "vox_pad", "color_gain_db": -11.0,
                            "bass_gain_db": -8.0},
          "W73: future garage = wide airy pads (shimmer pair) over the "
          "2-step skeleton; chops stay the foreground")]
WAVE += [("psytrance", {"bass_gain_db": -8.0, "lead_gain_db": -6.0},
          "W73: the rolling bass IS psy but 90.8 pct drowned the acid "
          "lead — staging only, the lead stays MONO (303 truth)")]
WAVE += [("soca", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                            "steps": [[0, 1, 2], [4, 3, 1], [6, 5, 2], [10, 4, 2],
                                      [16, 6, 2], [20, 5, 1], [22, 4, 2], [26, 3, 2]]},
                   "lead_gain_db": -6.0, "bass_gain_db": -8.0, "kick_gain_db": -4.0},
          "W73: soca's big carnival hook was missing entirely; brass bed "
          "stays mono (section-of-one truth pending a brass split)")]
WAVE += [("gqom", {"bass_gain_db": -8.0, "lead_gain_db": -6.0},
          "W73: gqom's dark weight is identity (84 pct) — ease the sub, "
          "lift the chant pair; no palette change")]
WAVE += [("bigroom", {"bass_gain_db": -9.0, "kick_gain_db": -4.0,
                      "arp_gain_db": -10.0},
          "W73: bigroom staging (78 pct low with pairs buried) — the drop "
          "stab wall forward")]
WAVE += [("electro", {"bass_gain_db": -9.0, "arp_gain_db": -10.0,
                      "color_gain_db": -11.0},
          "W73: electro at 91 pct low — the arps ARE electro; staged up")]
WAVE += [("eurodance", {"bass_gain_db": -9.0, "arp_gain_db": -10.0,
                        "color_gain_db": -11.0, "kick_gain_db": -4.0},
          "W73: eurodance at 86 pct — the piano/saw hooks forward")]
WAVE += [("gfunk", {"bass_gain_db": -7.0, "lead_gain_db": -4.0,
                    "kick_gain_db": -3.5,
                    "bass_voice": "bass_warm", "bass_style": "walking"},
          "W73: the gfunk whine lead forward; the 2-note reese HOLD was "
          "the owner (reese physics 3rd sighting) and wrong DNA besides — "
          "gfunk rides a bouncing warm funk bass (walking)")]
WAVE += [("hardstyle", {"bass_gain_db": -9.0, "lead_gain_db": -4.0,
                        "kick_gain_db": -3.0},
          "W73: hardstyle's kick IS the genre (barely eased -3); the "
          "euphoric screech pair to the FRONT at -4 — records put the "
          "lead at kick level in the drop")]

WAVE += [("dub", {"color_gain_db": -9.0, "bass_gain_db": -6.5,
                  "kick_gain_db": -3.5, "hat_gain_db": -9.0},
          "W73: the hammond Leslie pair was BORN and buried 14dB under the "
          "bass — dub's skank is audible in every record; bass stays king")]

# W72 THE MAINSTREAM FOUR (radar sweep 4, 2026-07-11): kpop the new worst
# (-22.2 / corr 0.99, hook-factory genre with NO topline); hiphop birthed
# FOUR lanes (the pop-gap twin); rnb 86% low with a mono harp bed and no
# lead; dancehall's pluck pair buried (W69 staging class).
WAVE += [("kpop", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                            "steps": [[0, 5, 1], [2, 5, 1], [4, 6, 2], [7, 4, 1],
                                      [10, 3, 2], [14, 2, 1], [16, 5, 1], [18, 5, 1],
                                      [20, 8, 2], [23, 6, 1], [26, 5, 2], [30, 4, 2]]},
                   "lead_gain_db": -5.0, "bass_gain_db": -12.0,
                   "kick_gain_db": -3.5, "color_gain_db": -12.0},
          "W72: kpop is HOOK-FACTORY music born with no topline — a bright "
          "insistent pluck-pair hook with the repeated-note stutter the "
          "genre lives on; 808 eased to -8 under it, strings bed -12")]
WAVE += [("hiphop", {"lead": {"voice": "keys_dark", "octave": 4, "bars": 2,
                              "steps": [[0, 1, 3], [6, 3, 2], [10, 4, 2],
                                        [16, 5, 3], [22, 4, 2], [26, 3, 3]]},
                     "color_voice": "keys_dark", "color_gain_db": -11.0,
                     "lead_gain_db": -7.0, "bass_gain_db": -7.0},
          "W72: hiphop birthed kick/snare/hat/bass only. The boombap truth "
          "is the KEYS: dark keys bed (detune pair) + a sparse piano-stab "
          "hook riding the beat")]
WAVE += [("rnb", {"lead": {"voice": "formant_vox", "octave": 4, "bars": 2,
                           "steps": [[2, 3, 2], [6, 5, 2], [10, 4, 3], [18, 6, 2],
                                     [22, 5, 2], [26, 4, 4]]},
                  "color_voice": "keys_dark", "color_gain_db": -11.0,
                  "lead_gain_db": -7.0, "bass_gain_db": -8.0,
                  "kick_gain_db": -3.5},
          "W72: rnb at 86 pct low with a mono harp and no melody. Genre "
          "truth: dark e-piano bed (detune pair) + a vocal-like topline "
          "(formant_vox breath pair) laid back off the beat; 808 -8")]
WAVE += [("dancehall", {"bass_gain_db": -8.0, "lead_gain_db": -5.0,
                        "kick_gain_db": -5.0, "hat_gain_db": -9.0,
                        "color_voice": "organ_soul", "color_gain_db": -10.0},
          "W72: the pluck pair was born and buried (-11.5 vs bass -5 / "
          "kick -2 = 77 pct low, corr 0.96) — W69 staging")]

# W71 THE POP GAP (radar sweep 3, 2026-07-11): pop birthed FOUR lanes
# (kick/clap/hat/bass) — no lead, no color; width -20.9 / corr 0.98 was a
# PALETTE GAP (the fuji class) on the most mainstream genre. indie_rock
# shared it; ukgarage had the lead but W69-class staging.
WAVE += [("pop", {"lead": {"voice": "pluck2", "octave": 5, "bars": 2,
                           "steps": [[0, 1, 2], [3, 3, 1], [6, 5, 2], [10, 4, 2],
                                     [16, 6, 2], [19, 5, 1], [22, 4, 1],
                                     [24, 3, 2], [28, 2, 3]]},
                  "color_voice": "pad_motion", "color_gain_db": -12.0,
                  "lead_gain_db": -6.0, "kick_gain_db": -3.5, "hat_gain_db": -9.0},
          "W71: pop born melodically NAKED (4 lanes). Genre truth: a "
          "syncopated pop topline (pluck pair via ALT) + lush pad bed "
          "(pad_motion detune pair) + kick eased off the club setting")]
WAVE += [("indie_rock", {"lead": {"voice": "guitar_grit", "octave": 4, "bars": 2,
                                  "steps": [[0, 1, 2], [4, 3, 2], [8, 5, 3],
                                            [14, 4, 2], [16, 6, 2], [20, 5, 2],
                                            [24, 3, 3], [30, 2, 2]]},
                         "color_voice": "guitar_grit", "color_gain_db": -11.0,
                         "lead_gain_db": -7.0},
          "W71: indie_rock had no melodic lane; the jangle bed + lead "
          "guitar pair (grit damp split) is the genre's whole face")]
WAVE += [("ukgarage", {"bass_gain_db": -9.0, "lead_gain_db": -6.0,
                       "kick_gain_db": -4.0},
          "W71: 88 pct low / corr 0.94 — the W69 staging class; the vox_pad "
          "lead pair was buried under sub -5 / kick -2")]

# W69 THE BALANCE BATCH (blind-judge radar sweep 2026-07-11): five genres,
# one signature — born bass -5/kick -2 vs melodic -11.5..-16.5 = low share
# 71-92%, width -12..-18, corr 0.88-0.97 (the synthwave/house class,
# batch-licensed per W51: per-genre rendered receipts ride the commit).
# Step 2 (owner probe on arranged mixes): THE KICK at -2 = 52dB low-band,
# out-powering even the bass (techno bass 49, reggaeton bass 39.5) — cutting
# bass alone RAISED reggaeton's share (W44 relative-shares law live). Kick
# staging + melodic push per genre; trance passed step 1 untouched.
WAVE += [("techno", {"bass_gain_db": -11.0, "lead_gain_db": -3.5,
                     "color_gain_db": -7.5, "hat_gain_db": -9.0,
                     "kick_gain_db": -5.0},
          "W69: born 92% low / width -17.7 / corr 0.97 (the sweep's worst); "
          "techno is KICK-led with hypnotic stabs+pads in the mids — sub "
          "-11, stabs -7, pads -11, hats -9")]
WAVE += [("trance", {"bass_gain_db": -9.0, "arp_gain_db": -10.0,
                     "color_gain_db": -10.0},
          "W69: born 74% low / width -14.1 / corr 0.92; the supersaw wall "
          "IS trance — arp pair -10, vox pad -10, sub supports at -9")]
# W69 HONEST REVERT — reggaeton: the judge CAUGHT the width/balance
# treatment at conf 5 and cited the REAL record's architecture against it:
# "74% low end with mono-like width is CLASSIC reggaeton kick/bass
# emphasis; [ours] brighter distribution and 5000Hz centroids are tonally
# wrong". The genre's born values (71% low / -16.5 width) were RIGHT.
# LAW: the fooled-population envelope is not a per-genre bar — architecture
# varies BY GENRE and the judge's tells cite each genre's own reference.
# The true defect it named: CLAP reggaeton similarity 0.0057 (doesn't sound
# like the genre at all) = a W70 identity problem, not a staging one.
WAVE += [("drill", {"bass_gain_db": -8.0, "lead_gain_db": -8.0,
                    "kick_gain_db": -4.0, "hat_gain_db": -9.0},
          "W69: born 90% low / width -12.6 / corr 0.90; trap (same family) "
          "fools the judge at 72% — the 808 slide keeps the voice, staged "
          "-8; keys_dark pair -8 keeps drill dark but present")]
WAVE += [("disco", {"bass_gain_db": -9.0, "lead_gain_db": -5.0,
                    "color_gain_db": -9.0, "kick_gain_db": -4.5,
                    "hat_gain_db": -7.0},
          "W69: born 89% low / width -12.1 / corr 0.88; disco is the "
          "BRIGHT one — strings -5, brass stabs -10, bass -9 under the "
          "four-floor kick")]

WAVE += [("house", {"bass_gain_db": -10.0, "lead_gain_db": -6.0,
                    "hat_gain_db": -8.0, "openhat_gain_db": -6.0,
                    "color_gain_db": -12.0},
          "W68 blind-judge tells 2026-07-11: 77.5% bass, width -13.9 "
          "'mono-collapse', 0.9% above 6kHz 'inaudibly thin'. Owner probe: "
          "sub_clean at -5 (41.4dB low) topped even the kick; the offbeat "
          "sizzle (openhat) reached only 5.4dB >6k. House is KICK-led with "
          "organ forward and hats that sizzle: bass -10 under the kick, "
          "organ pair -6 (Leslie split born in W68), hats -8/-6, pads -12")]

WAVE += [("synthwave", {"bass_style": "psy_rolling", "bass_voice": "sub_clean",
                        "bass_gain_db": -12.0, "lead_gain_db": -5.0,
                        "arp_gain_db": -10.0, "kick_gain_db": -5.0,
                        "color_gain_db": -10.0},
          "W67 blind-judge tell 2026-07-11: the bass ALONE out-powered every "
          "synth combined (solo probe: bass low-band 42.1dB vs full-mix "
          "42.8; synths sum ~36) -> 80% low share, full-band corr = bass "
          "corr = 1.0 though the mid band measured -0.21 (the pairs were "
          "always wide). Synthwave is SYNTHS FORWARD: driving pulse bass "
          "at -12, lead pair up to -5, arp pair -10, pads -10, kick -5 "
          "(second owner probe: kick and bass each held ~14pts of low)")]

WAVE += [("chaabi", {"bass_voice": "bass_warm"},
          "wave 10 probe 2026-07-11: a reese (67% low) in Moroccan chaabi — "
          "the gimbri/bass-guitar warmth is the genre's low voice")]

WAVE += [("post_punk", {"bass_voice": "bass_warm"},
          "wave 8 probe 2026-07-11: sub_clean at rms -14 owned 83% low; "
          "post-punk's bass IS the harmony carrier (the Hook bass) — warm "
          "harmonics, not a sub; no color lane exists to carry lowmid")]


def main():
    kg = KG()
    changed = 0
    for genre, fields, why in WAVE:
        row = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                   f"(p:PatternArchetype) WHERE p.grid IS NOT NULL "
                   f"RETURN p.name, p.grid")
        if not row:
            print(f"  !! {genre}: no archetype — skipped")
            continue
        pname, gjson = row[0]
        grid = json.loads(gjson)
        if all(grid.get(k) == v for k, v in fields.items()):
            print(f"  == {genre}: already seeded")
            continue
        grid.update(fields)
        blob = json.dumps(grid, sort_keys=True)
        kg.q(f"MATCH (p:PatternArchetype {{name: '{esc(pname)}'}}) "
             f"SET p.grid = '{esc(blob)}', "
             f"p.provenance_w47 = '{esc(why)}'")
        print(f"  ++ {genre}: {fields} ({pname})")
        changed += 1
    print(f"lowmid curation wave 1: {changed} changed (idempotent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
