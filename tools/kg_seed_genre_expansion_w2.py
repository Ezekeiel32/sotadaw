#!/usr/bin/env python3
"""KG curation wave 2 (2026-07-06): EMERGING/INTERNET FRONTIER + SOUL FOUNDATIONS — the
"doesn't exist yet" half of the coverage campaign + the missing ancestors. Session
`genre-scout` (campaign: genre-research-campaign). Research + adversarial verify ->
docs/research_genre_expansion_w2.md. Sibling waves: kg_seed_genre_expansion.py (wave 1),
kg_seed_bands_jazz.py (genre-forge). Idempotent (MERGE).

  internet/frontier : plugg, pluggnb, automotivo(bruxaria), jersey_drill, digicore,
                      sigilkore, dariacore
  dark-electronic   : darksynth, dungeon_synth
  UK/afro           : afroswing
  soul foundations  : motown, doo_wop, boogie, hi_nrg
  jazz completion   : free_jazz
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched "
        "+ adversarially verified, sources in docs/research_genre_expansion_w2.md)")
CITE = "curated:claude/2026-07-06-genrexp2"

NEW_TECH = {
 # --- plugg / pluggnb ---
 "plugg_bell_palette": "airy FM glass bells, synth flutes and soft plucks carry the melody — spacey, toy-like, LOW-PASSED soft; the beat feels weightless over hard 808s",
 "muffled_clap_3": "the plugg backbeat: ONE muffled, low-passed clap/snare on beat 3 (half-time), tucked under the melody instead of cracking over it",
 "beat_skip_dropout": "whole-beat DROPOUTS: the kick/808 skips a beat (or a whole bar goes drumless) so the loop breathes — the skip IS the hook",
 "gliding_808_melody": "the 808 voice-leads (root -> third/fifth glides) under the chords — bass as the counter-melody, portamento audible",
 "rnb_gospel_loop": "maj9/min9/add9 gospel-R&B keyboard loops (DX7 tine e-piano, glassy bells) — pluggnb's harmonic bed, 2-4 chords cycling",
 "pitched_vocal_topline": "Auto-Tuned melodic rap-sung topline, often pitched up, doubled in octaves — the voice is an instrument riding the loop",
 # --- automotivo / bruxaria ---
 "double_tresillo_kick": "the automotivo engine: tresillo kick doubled per bar (slots 1, 1.75, 2.5 + 3, 3.75, 4.5) — relentless 3+3+2 x2 propulsion",
 "tuin_siren": "the TUIN: a piercing sliding sine/square siren blip looped as the lead hook — Brazilian funk's signature synth cry",
 "vocal_shard_percussion": "chopped chipmunked vocal stabs placed AS percussion on the 16th grid — syllables become drums",
 "bruxaria_clip_wall": "bruxaria aesthetic: ONE huge distorted reverberated kick dominates beat 1, everything driven into clipping/saturation as a texture (keep the DAW master soft-clipped, clipped_samples 0)",
 "mute_slamback": "arrangement by MUTES: whole-mix cuts for 1-2 beats then a slam-back — the drop grammar of funk DJ tools",
 # --- jersey drill ---
 "jersey_five_kick": "THE Jersey club kick: 5 hits per bar at slots 1, 2, 3, 3.75, 4.5 (grid 0,4,8,11,14) — boom / boom / boom-boom / boom, nonstop",
 "bed_squeak": "the bed-squeak sample as a percussion instrument riding the kick pattern — Jersey club's meme-turned-signature",
 "drill_slide_808": "dark drill 808s GLIDING between notes (portamento) under the club kick — the NY drill low end on Jersey legs",
 "club_drill_switchup": "8-bar switch-ups alternating drill half-time sections with full Jersey club kick sections — two grooves, one song",
 # --- afroswing ---
 "afroswing_bounce": "kick on 1 + the 'a' of 2 (slot 2.75), rim/snare on 3 (often dragged late), swung shakers/hats ~55-64% — the UK afrobeats lilt under rap-sung melody",
 "melodic_808_sub": "a warm, round, MELODIC 808 sub playing the bassline (not just roots) — kick+bass anchored while everything else swings",
 "mallet_pluck_hook": "marimba/mallet/steel-ish FM plucks play the instrumental hook — sunny, bouncing, West-African-tinged",
 # --- darksynth ---
 "reese_arp_ostinato": "a distorted reese/saw bass ARP running straight 16ths as the engine — the John Carpenter pulse weaponized",
 "gated_reverb_snare": "the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat",
 "sidechain_menace": "audible sidechain pump on pads/bass to a four-on-the-floor kick — breathing dread",
 "carpenter_pad": "detuned-saw / minor-triad synth pads holding long Aeolian/Phrygian tones — the horror-score bed",
 "halftime_menace_break": "the half-time variant: kick 1, snare 3, everything darker and slower — menace between club sections",
 # --- dungeon synth ---
 "rompler_choir_bed": "cheap 90s ROMpler synth-choir and string patches as the main voices — the lo-fi fantasy orchestra",
 "fifth_ostinato_ritual": "a 2-4 bar open-fifth ostinato (organ/harpsichord/harp) cycling under a chant-like modal melody — processional, unhurried",
 "timpani_processional": "percussion only as ritual punctuation: timpani/tom on beat 1 (answer on 3) or NOTHING — a backbeat is forbidden",
 "tape_hiss_patina": "deliberate lo-fi: tape hiss bed, wow/flutter, dark low-passed master — the cassette-in-a-crypt aesthetic",
 "dungeon_modal_chant": "Aeolian/Dorian/Phrygian stepwise melodies, narrow range, repeated like a liturgy — melody as ritual not hook",
 # --- digicore ---
 "glitch_interruption": "THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop",
 "nightcore_pitch_vocal": "toplines pitched UP +3..+7 st (or an octave) — fragile, anonymized, hyper-emotive; write in a comfortable key and shift",
 "emo_axis_loop": "the Aeolian emo axis i-VI-III-VII cycling under everything — pop-punk chords in trap clothes",
 "distorted_gummy_808": "the 808 overdriven until it 'overtakes the song' — gummy, elastic, gliding 4ths/5ths; digicore's low end IS distortion",
 "hard_cut_ending": "songs end on a HARD CUT (no fade, no outro) — 1:45-2:30 total, texture-flips not harmony-changes between sections",
 # --- sigilkore ---
 "drowned_reverb_chain": "everything drenched: long detuned choir/pad reverb tails BEHIND heavy bitcrush — drowned cathedral under digital rot",
 "bitcrush_patina": "bitcrush/sample-rate-reduction ON THE BUS as the genre's texture (8-16 bit, srate drops) — apply to bells, vocals, even the master color",
 "ghost_glide_808": "long-tail 808 on beat 1 with ghost glides trailing after — half-time (snare 3) with hyperactive 1/16-1/64 hat spatter",
 "occult_bell_lead": "detuned FM bells and chiptune leads playing narrow dark minor motifs — music-box-from-a-ritual energy",
 "tape_stop_fill": "tape-stop / pitch-drop fills close phrases instead of drum fills",
 # --- dariacore ---
 "sample_switchup_wall": "a NEW chipmunked pop-sample chop every 4-8 bars — key and subgenre can change at every switch; maximalist collage as form",
 "jersey_kick_at_170": "the Jersey 5-kick figure (0,4,8,11,14) sped to ~170 BPM as the constant under the chaos",
 "meme_sfx_percussion": "meme SFX (airhorns, vine booms, notification pings) placed AS drums on the grid",
 "chipmunk_chop_lead": "pop vocals pitched way up and re-chopped into melodic stabs — the lead instrument is a mangled hook you almost recognize",
 # --- motown ---
 "four_floor_snare": "the Motown stomp: SNARE (not kick) on ALL FOUR beats (Supremes grammar) — or heavy 2&4 backbeat; either way the snare leads",
 "tambourine_24": "tambourine locked on 2 & 4 (with the snare) — the shimmer that says Hitsville",
 "jamerson_bass_weave": "James Jamerson bass: syncopated 16th-note weaving line — roots on the one, then chromatic approaches, drops, ghost 16ths AGAINST the straight grid",
 "gospel_plagal_pop": "major-key I-IV plagal gospel motion + ii-V pop cadences, 2-4 chords a bar of harmonic drive",
 "baritone_sax_floor": "baritone sax doubling the bass line / pumping roots — the warm floor under the strings and vibes",
 "call_response_backings": "lead vocal answered by group backings ('ooh', hand-claps, ad-libs) every 2 bars — church call-and-response as pop architecture",
 # --- doo wop ---
 "sung_bass_engine": "the BASS IS A VOICE: 'bom-bom-bom / dip-da-dip' nonsense syllables on the dotted-quarter pulse with walking pickups — it replaces bass AND drums",
 "fifties_changes": "the 50s progression I-vi-IV-V (or I-vi-ii-V) cycling one chord per bar — the eternal loop of doo-wop",
 "triplet_piano_1258": "piano hammers block chords on EVERY triplet 8th (12 hits a bar in 12/8) — the ballad engine",
 "falsetto_over_stack": "a falsetto lead floating over a 4-5 part block-harmony stack (triads/6ths), gospel melisma on phrase ends",
 "brush_snap_backbeat": "brushed snare or finger snaps on 2 & 4, kick soft on 1 & 3 — drums barely there, the voices carry",
 # --- boogie ---
 "octave_bounce_bass": "the boogie engine: synth bass bouncing root-octave 16ths (Minimoog/DX), locking the kick pickups — the low end IS the timekeeper",
 "no_four_floor_kick": "kick on 1 + pickups (and-of-2, and-of-3) — NOT four-on-the-floor; the space between kicks makes the bounce",
 "linn_clap_crack": "LinnDrum/DMX-era clap+snare stacked on 2 & 4, bone dry or short-gated — the early-80s crack",
 "talkbox_hook": "a talkbox/vocoder lead singing the hook (Zapp grammar) — synthesized voice as the star",
 "dorian_min7_vamp": "Dorian min7/min9 two-chord vamps (i7-IV7) — funk harmony smoothed for the roller rink",
 # --- free jazz ---
 "energy_pulse_wash": "no groove pattern: ride/cymbal-edge WASH at 6-12 hits/sec + off-grid snare bursts (3-9 hit clusters) + spasmodic kick — density replaces meter",
 "collective_improv": "everyone solos at once: sax skronk, arco bass groans, piano clusters — lines answer each other's ENERGY not chords",
 "pantonal_line": "melody is pantonal/chromatic or one modal pedal — wide leaps, overblown cries, no functional changes to spell",
 "density_arc_form": "the form is a DENSITY ARC: sparse -> boiling -> collapse -> regeneration; use tempoMap accel/rit waves, never loop a bar twice identically",
 "arco_bass_groan": "bowed double-bass groans and pizzicato flurries as a second front-line voice (often TWO basses)",
 # --- hi-nrg ---
 "octave_bass_16ths": "THE Hi-NRG signature: octave-pumping synth bass in straight 8ths/16ths (R-r'-R-r') replacing the hi-hat as timekeeper — accent via filter envelope",
 "fourfloor_hinrg": "kick 1-2-3-4, clap+snare on 2 & 4, open hat on every off-8th — the relentless 130 BPM engine",
 "simmons_tom_fill": "Simmons/synth-tom descending fills into section changes — the 80s dance exclamation mark",
 "minor_arp_stab": "natural-minor arpeggio stabs and octave lead lines (Prophet/Juno) — energetic, campy, melodramatic",
 "disco_diva_belt": "a belted diva vocal riding the top, big reverb, call-and-answer with the synth stabs",
}

G = [
 dict(name="plugg", bpm=(125,165), key="C minor", form="song",
   voicing={"style":"airy_bell_halftime","lo":36,"hi":88}, parents=["trap"], derived=[],
   tech=["plugg_bell_palette","muffled_clap_3","beat_skip_dropout","gliding_808_melody","pitched_vocal_topline"],
   pattern=("plugg_float","Plugg (~140 BPM, half-time, straight-ish): sparse syncopated kick doubling gliding 808s; ONE muffled low-passed clap on beat 3; lazy straight-8th hats; airy FM bells/flutes float the melody; a whole beat DROPS OUT every few bars so the loop breathes.",
     {"bars":1,"swing":0.52,"bass_style":"sub","kick":[0,7,10],"snare":[8],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"8":0.6},"hat":{"0":0.45,"2":0.3,"4":0.45,"6":0.3,"8":0.45,"10":0.3,"12":0.45,"14":0.3}},
      "chords":[[0,1],[2,6]],"lead":{"voice":"fmbell","octave":5,"steps":[[0,1,2],[4,5,1],[6,4,1],[8,3,2],[12,5,2]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("plugg_bells","fmbell","airy FM glass bells (fmbell) + synth flute (flute_lead) low-passed SOFT; kick_808/sub_clean gliding melodically; the clap muffled (low-pass fx_filter on the snare track); space is the luxury — leave dropout bars")]),

 dict(name="pluggnb", bpm=(125,155), key="Eb major (min9 loops)", form="song",
   voicing={"style":"glassy_gospel","lo":36,"hi":90}, parents=["plugg"], derived=["rnb","trap"],
   tech=["rnb_gospel_loop","plugg_bell_palette","gliding_808_melody","muffled_clap_3","pitched_vocal_topline"],
   pattern=("pluggnb_loop","PluggnB (~138 BPM, half-time, hats swung ~60%): a maj9/min9 gospel-R&B keys loop (DX tine e-piano + glassy bells) cycles 2-4 chords; octave-skip kicks + denser 32nd hat rolls than plugg; 808 voice-leads root->third; clap tucked on 3; pitched vocal topline melody.",
     {"bars":1,"swing":0.6,"bass_style":"sub","kick":[0,3,8,11],"snare":[8],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"8":0.6}},"chords":[[0,1],[1,6],[2,4],[3,5]],
      "lead":{"voice":"rhodes","octave":4,"steps":[[0,1,2],[2,3,1],[4,5,2],[8,4,2],[12,6,2]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("pluggnb_keys","rhodes","DX7-tine e-piano (rhodes) playing maj9/min9 gospel loops + fmbell glass on top; kick_808 gliding; soft muffled clap; keep it GLOSSY and warm — R&B in plugg clothes")]),

 dict(name="automotivo", bpm=(125,180), key="F minor (anti-harmonic)", form="club",
   voicing={"style":"clipped_funk_tool","lo":33,"hi":84}, parents=["baile_funk"], derived=[],
   tech=["double_tresillo_kick","tuin_siren","vocal_shard_percussion","bruxaria_clip_wall","mute_slamback"],
   pattern=("double_tresillo","Automotivo/bruxaria (~150 BPM): the double-tresillo kick — slots 1, 1.75, 2.5 / 3, 3.75, 4.5 (grid 0,3,6,8,11,14) — claps on 2&4; a piercing TUIN sine-siren loops the hook; chipmunked vocal shards fill 16th slots AS percussion; arrangement = whole-mix MUTES then slam-backs. Bruxaria = darker: one huge distorted kick on 1 dominates, texture driven into saturation (master stays soft-clipped, clipped_samples 0).",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,3,6,8,11,14],"snare":[4,12],"hat":[2,10],
      "vel":{"kick":{"0":1.0,"3":0.85,"6":0.9,"8":1.0,"11":0.85,"14":0.9}},"chords":[[0,1]],
      "lead":{"voice":"sine_siren","octave":6,"steps":[[0,1,1],[2,5,1],[4,1,1],[6,5,1],[8,1,1],[10,5,1],[12,1,1],[14,5,1]]}}),
   mix={"lufs_lo":-8,"lufs_hi":-5,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("tuin","sine_siren","the TUIN siren = sine_siren (pitch-tracking bare sine, glide+bite zones; test_sine was the 440Hz VALIDATOR and droned the whole genre) sliding octave blips — pierce it through; distorted 808 kick (kick_808 + fx_saturate hard); chopped formant_vox stabs as percussion; drive the bus into fx_softclip for the bruxaria wall — NEVER hard-clip the master")]),

 dict(name="jersey_drill", bpm=(130,150), key="C# minor", form="song",
   voicing={"style":"club_drill","lo":33,"hi":76}, parents=["jerseyclub","drill"], derived=[],
   tech=["jersey_five_kick","drill_slide_808","club_drill_switchup","bed_squeak","triplet_hat_roll"],
   pattern=("squeak_drill","Jersey drill (~138 BPM): THE Jersey 5-kick — grid slots 0,4,8,11,14 (1, 2, 3, 3.75, 4.5) — runs nonstop under DARK sliding drill 808s; claps stabbed at slots 9&12 (+11); hats mark 2&4 with triplet rolls; 8-bar switch-ups alternate drill half-time (snare 3, kick sparse) with the full club kick. Bed-squeak rides the kick figure.",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,4,8,11,14],"snare":[9,12],"hat":[4,12],
      "vel":{"kick":{"0":1.0,"4":0.9,"8":1.0,"11":0.85,"14":0.9},"snare":{"9":0.8,"12":0.9}},"chords":[[0,1]],
      "lead":{"voice":"fmbell","octave":4,"steps":[[0,1,2],[6,2,1],[8,1,2],[14,3,1]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-6,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("squeak_kit","kick_808","clipped Jersey kick (kick_punch layered kick_808) on the 5-figure; drill 808 gliding (sub_clean + portamento feel via note slides); dark FM bell (fmbell) minor motifs; the bed-squeak = a high pitched short formant_vox/pluck squeak riding the kick slots")]),

 dict(name="afroswing", bpm=(95,115), key="A minor", form="song",
   voicing={"style":"sunny_bounce","lo":36,"hi":84}, parents=["afrobeats"], derived=["dancehall"],
   tech=["afroswing_bounce","melodic_808_sub","mallet_pluck_hook","pitched_vocal_topline"],
   pattern=("afroswing_bounce","Afroswing (~102 BPM, hats swung ~58%): kick on 1 + the 'a' of 2 (slot 7), rim/snare on 3 (dragged a touch late), swung shakers and offbeat hats; a warm MELODIC 808 sub plays the bassline; marimba/mallet FM plucks bounce the hook; rap-sung melodic topline.",
     {"bars":1,"swing":0.58,"bass_style":"sub","kick":[0,7],"snare":[8],"hat":[2,6,10,14],
      "vel":{"snare":{"8":0.85},"hat":{"2":0.6,"6":0.5,"10":0.6,"14":0.5}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"marimba","octave":5,"steps":[[0,1,1],[3,3,1],[6,5,1],[8,4,1],[11,3,1],[14,1,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("afroswing_kit","marimba","marimba/kalimba mallet plucks for the hook; warm melodic sub (sub_clean/bass_warm) NOT aggressive; rimshot snare + shaker hats swung; sunny, bouncing, space between hits")]),

 dict(name="darksynth", bpm=(90,150), key="D minor (Phrygian)", form="club",
   voicing={"style":"horror_machine","lo":33,"hi":84}, parents=["synthwave"], derived=[],
   tech=["reese_arp_ostinato","gated_reverb_snare","carpenter_pad","sidechain_menace","halftime_menace_break"],
   pattern=("carpenter_engine","Darksynth (~125 BPM, machine-straight): four-on-the-floor kick + huge GATED-REVERB snare on 2&4; a distorted reese/saw bass arp runs straight 16ths (the Carpenter pulse); detuned minor pads hold dread above; audible sidechain pump; half-time menace breaks (kick 1, snare 3) between club sections.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "chords":[[0,1]],"lead":{"voice":"reese","octave":3,"steps":[[0,1,1],[1,1,1],[2,8,1],[3,1,1],[4,1,1],[5,8,1],[6,1,1],[7,1,1],[8,1,1],[9,1,1],[10,8,1],[11,1,1],[12,1,1],[13,8,1],[14,1,1],[15,1,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("carpenter_rig","reese","distorted reese 16th-arp (reese + fx_saturate) = the engine; supersaw/pad_motion detuned minor pads; gated snare = snare + short fx_reverb hard-cut; fx_pump sidechain audible on pads; keys_dark stabs for the stingers")]),

 dict(name="dungeon_synth", bpm=(40,110), key="E minor (Dorian/Phrygian)", form="through_composed",
   voicing={"style":"crypt_rompler","lo":33,"hi":84}, parents=["ambient"], derived=["black_metal"],
   tech=["rompler_choir_bed","fifth_ostinato_ritual","dungeon_modal_chant","timpani_processional","tape_hiss_patina"],
   pattern=("crypt_ritual","Dungeon synth (~72 BPM, processional, often drumless): a 2-4 bar open-FIFTH ostinato (organ/harpsichord/harp) cycles under a chant-like stepwise Aeolian/Dorian melody (ROMpler choir/strings); timpani strikes beat 1 (answer on 3) when percussion exists at all — a backbeat is FORBIDDEN; tape-hiss patina, dark low-passed master.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0],"chords":[[0,1]],
      "vel":{"kick":{"0":0.6}},
      "lead":{"voice":"vox_pad","octave":4,"steps":[[0,1,4],[4,2,2],[6,3,2],[8,2,4],[12,1,4]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-14,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":8.0},
   sounds=[("crypt_bed","vox_pad","ROMpler choir = vox_pad + strings via pad_motion; organ = hammond_organ dark; harpsichord-ish = pluck2/harp arpeggios; timpani for the processional strike; the cassette patina = fx_crush GENTLE on the master color (bits 12-14, srate 18-26k) + dark fx_filter ~6-8kHz + a quiet hiss bed; never loud, never bright")]),

 dict(name="digicore", bpm=(120,170), key="A minor (emo axis)", form="song",
   voicing={"style":"glitch_emo","lo":33,"hi":88}, parents=["hyperpop"], derived=["trap"],
   tech=["glitch_interruption","emo_axis_loop","distorted_gummy_808","nightcore_pitch_vocal","hard_cut_ending"],
   pattern=("glitch_emo","Digicore (~145 BPM trap grid): kick on 1 + syncopated hits following 808 slides (slots 0,6,15); clap hard on 2&4 with 1/32 rolls into them; running 16th hats; the emo axis i-VI-III-VII cycles under a nightcore-pitched topline; EVERY 2-4 bars a GLITCH INTERRUPTION — stutter-retrigger the last 16th, reverse a tail in, or hard-gate a 1/4-beat silence. End on a HARD CUT.",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,6,15],"snare":[4,12],"hat":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
      "vel":{"hat":{"1":0.3,"3":0.3,"5":0.3,"7":0.3,"9":0.3,"11":0.3,"13":0.3,"15":0.45}},"chords":[[0,1],[1,6],[2,3],[3,7]],
      "lead":{"voice":"supersaw","octave":5,"steps":[[0,1,2],[4,3,1],[6,5,1],[8,6,2],[12,5,2]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("glitch_emo_rig","supersaw","supersaw wash + guitar_grit lo-fi loops over a DISTORTED gummy 808 (kick_808 + fx_saturate heavy); nightcore lead = formant_vox/supersaw pitched HIGH; lo-fi patina = fx_crush on sends (bits 12, srate 22k = 'boombox demo tape'); glitches = arrangement-level stutter (repeat the last 16th-note slice as notes) + fx_trim hard gates; loud but soft-clipped")]),

 dict(name="sigilkore", bpm=(105,190), key="F# minor (Phrygian)", form="song",
   voicing={"style":"drowned_crush","lo":30,"hi":88}, parents=["hyperpop"], derived=["trap","witch_house"],
   tech=["drowned_reverb_chain","bitcrush_patina","ghost_glide_808","occult_bell_lead","tape_stop_fill"],
   pattern=("drowned_ritual","Sigilkore (~155 BPM, half-time): long-tail 808 on beat 1 with ghost glides trailing; snare on 3; hyperactive 1/16 hat spatter (bursts, not steady); detuned choir pads DROWNED in reverb behind heavy bitcrush; FM-bell/chip leads play narrow dark minor motifs; tape-stop fills close phrases.",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,10],"snare":[8],"hat":[0,1,2,4,5,8,9,10,12,13,14],
      "vel":{"hat":{"1":0.3,"2":0.35,"5":0.3,"9":0.3,"13":0.35,"14":0.3}},"chords":[[0,1]],
      "lead":{"voice":"fmbell","octave":5,"steps":[[0,1,1],[2,2,1],[4,1,1],[8,3,1],[10,2,1],[12,1,2]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-6,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("sigil_rig","fmbell","detuned FM bells (fmbell) + chip leads (chiptune_pulse) for the occult motifs; vox_pad choir sent HUGE into a reverb bus, then the BUS crushed with fx_crush (bits 6-9, srate 6-12k — reverb BEHIND the crush = the drowned-rot order) ; gliding kick_808 with long tails; everything darker than hyperpop, wetter than trap")]),

 dict(name="dariacore", bpm=(150,200), key="C major (sample-dictated)", form="club",
   voicing={"style":"maximal_collage","lo":36,"hi":92}, parents=["jerseyclub"], derived=["hyperpop"],
   tech=["sample_switchup_wall","jersey_kick_at_170","chipmunk_chop_lead","meme_sfx_percussion","glitch_interruption"],
   pattern=("collage_engine","Dariacore (~170 BPM): the Jersey 5-kick (0,4,8,11,14) clipped and relentless; claps 2&4; a NEW chipmunked pop-vocal chop every 4-8 bars (key/subgenre can flip at every switch); meme SFX placed as drums; supersaw + growl bass underneath; maximalist, exhausting, gleeful.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,4,8,11,14],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"4":0.9,"8":1.0,"11":0.85,"14":0.9}},"chords":[[0,1],[1,4],[2,5],[3,4]],
      "lead":{"voice":"supersaw","octave":5,"steps":[[0,1,1],[2,3,1],[4,5,1],[6,4,1],[8,6,1],[10,5,1],[12,4,1],[14,3,1]]}}),
   mix={"lufs_lo":-8,"lufs_hi":-6,"band_order":"mid>low>lowmid","clipped":0,"mid_floor":10.0},
   sounds=[("collage_rig","supersaw","chipmunk chop stand-in = supersaw/formant_vox stabs pitched high re-sequenced; clipped Jersey kick (kick_punch + fx_saturate, or fx_crush bits 8 for digital edge); switch-up law: change the lead sample/key every 4-8 bars via sections; meme SFX = short pitched noise/vox hits on the grid")]),

 dict(name="motown", bpm=(90,140), key="C major", form="song",
   voicing={"style":"hitsville_stomp","lo":33,"hi":86}, parents=["soul"], derived=[],
   tech=["four_floor_snare","tambourine_24","jamerson_bass_weave","gospel_plagal_pop","baritone_sax_floor","call_response_backings"],
   pattern=("hitsville_stomp","Motown (~126 BPM, straight-8th to light shuffle): the SNARE stomps ALL FOUR beats (Supremes grammar) with tambourine shimmering 2&4; kick anchors 1&3; the Jamerson bass WEAVES syncopated 16ths against the straight grid (root on 1, chromatic approaches, ghost pickups); piano/vibes stab the offbeats; baritone sax pumps the floor; call-and-response backings answer the lead every 2 bars.",
     {"bars":1,"swing":0.52,"bass_style":"walking","kick":[0,8],"snare":[0,4,8,12],"hat":[4,12],
      "vel":{"snare":{"0":0.8,"4":0.95,"8":0.8,"12":0.95},"hat":{"4":0.7,"12":0.7}},"chords":[[0,1],[1,4],[2,1],[3,5]],
      "lead":{"voice":"vibraphone","octave":4,"steps":[[2,1,1],[6,3,1],[10,5,1],[14,4,1]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-11,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0},
   sounds=[("hitsville_rig","vibraphone","vibraphone + jazz_piano offbeat stabs; upright_bass/bass_warm playing the Jamerson weave (write the 16th syncopation INTO the notes); tambourine = bright hat on 2&4; sax_section/brass_stab baritone floor + string pads (strings_disco soft); warm tape saturation, mid-forward vintage master — do NOT brickwall")]),

 dict(name="doo_wop", bpm=(55,160), key="Ab major", form="song",
   voicing={"style":"streetcorner_stack","lo":40,"hi":84}, parents=["rnb"], derived=[],
   tech=["sung_bass_engine","fifties_changes","triplet_piano_1258","falsetto_over_stack","brush_snap_backbeat"],
   pattern=("fifties_ballad","Doo-wop ballad (~72 BPM, 12/8 feel — swing ~0.66 on a 16-grid approximation): piano hammers the triplet 8ths; the SUNG BASS ('bom-bom-bom') walks the dotted-quarter pulse with pickups; brushed kick 1&3, snaps/snare 2&4; the I-vi-IV-V changes cycle one chord a bar; falsetto lead floats over the block-harmony stack.",
     {"bars":1,"swing":0.66,"bass_style":"walking","kick":[0,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"hat":{"0":0.5,"2":0.35,"4":0.5,"6":0.35,"8":0.5,"10":0.35,"12":0.5,"14":0.35},"snare":{"4":0.6,"12":0.6}},
      "chords":[[0,1],[1,6],[2,4],[3,5]],
      "lead":{"voice":"formant_vox","octave":5,"steps":[[0,1,2],[4,3,2],[8,5,2],[12,4,2]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":11.0},
   sounds=[("streetcorner","formant_vox","the stack = formant_vox/vox_pad block harmony; sung bass = a LOW formant_vox/bass_warm voice on the dotted pulse; jazz_piano triplets; brush_snare + soft kick; intimate room reverb, vintage warm, very dynamic — the voices ARE the record")]),

 dict(name="boogie", bpm=(100,120), key="D minor (Dorian)", form="club",
   voicing={"style":"roller_rink","lo":33,"hi":84}, parents=["disco"], derived=["funk"],
   tech=["octave_bounce_bass","no_four_floor_kick","linn_clap_crack","talkbox_hook","dorian_min7_vamp"],
   pattern=("roller_bounce","Boogie (~112 BPM, light 16th shuffle ~54%): NO four-on-the-floor — kick on 1 + pickups (and-of-2 = slot 6, and-of-3 = slot 10); LinnDrum clap+snare crack 2&4; the synth bass bounces root-octave 16ths locking the kick; min7/min9 Dorian two-chord vamps; talkbox hook on top; open hats off-8ths.",
     {"bars":1,"swing":0.54,"bass_style":"roots","kick":[0,6,10],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.95,"12":0.95},"hat":{"2":0.6,"6":0.5,"10":0.6,"14":0.5}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"clav_funk","octave":4,"steps":[[0,1,1],[2,1,1],[4,5,1],[6,4,1],[8,1,1],[10,5,1],[12,4,1],[14,3,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("roller_rig","clav_funk","Minimoog octave bass = bass_warm/chip_bass playing R-r' 16ths (write the octave bounce INTO the notes); clav_funk + rhodes stabs; talkbox hook = formant_vox riding the melody; clap_909 dry crack; strings_disco sweetener; punchy but dynamic")]),

 dict(name="free_jazz", bpm=(60,320), key="pantonal (C pedal)", form="through_composed",
   voicing={"style":"energy_music","lo":28,"hi":90}, parents=["jazz"], derived=[],
   tech=["energy_pulse_wash","collective_improv","pantonal_line","density_arc_form","arco_bass_groan"],
   pattern=("energy_wash","Free jazz (~230 BPM pulse — but NO meter): ride/cymbal-edge WASH at high density; snare bursts in off-grid clusters; kick spasmodic (never a pattern); two basses (pizz flurries + arco groans); sax skronk in wide pantonal leaps. THE LAW: never loop a bar identically — the form is a density ARC (sparse -> boiling -> collapse), use tempoMap accel/rit waves and section-level density automation.",
     {"bars":1,"swing":0.6,"bass_style":"walking","kick":[3,9],"snare":[2,5,6,11,13],"ride":[0,1,2,4,5,7,8,9,10,12,13,15],
      "vel":{"snare":{"2":0.5,"5":0.7,"6":0.4,"11":0.65,"13":0.5},"ride":{"0":0.8,"4":0.6,"8":0.75,"12":0.6}},
      "chords":[[0,1]],"lead":{"voice":"sax_section","octave":5,"steps":[[0,1,1],[1,7,1],[3,2,1],[6,8,1],[8,1,1],[11,6,1],[14,3,1]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-13,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0},
   sounds=[("energy_combo","sax_section","sax_section overblown wide-leap lines; upright_bass x2 (one pizz flurries, one long arco groans = sustained low notes); ride-forward kit at high density with NO backbeat; jazz_piano cluster stabs; room reverb, hugely dynamic, never quantize, never loop")]),

 dict(name="hi_nrg", bpm=(120,142), key="A minor", form="club",
   voicing={"style":"octane_octave","lo":33,"hi":86}, parents=["disco"], derived=["italo_disco"],
   tech=["octave_bass_16ths","fourfloor_hinrg","minor_arp_stab","simmons_tom_fill","disco_diva_belt"],
   pattern=("octane_engine","Hi-NRG (~130 BPM, machine-straight): kick 1-2-3-4, clap+snare on 2&4, open hat every off-8th; THE signature — the synth bass pumps ROOT-OCTAVE straight 8ths/16ths (R-r'-R-r') replacing the hi-hat as timekeeper, accent via filter; natural-minor arpeggio stabs; Simmons tom fills into sections; diva belt on top.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"hat":{"2":0.75,"6":0.75,"10":0.75,"14":0.75}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"supersaw","octave":4,"steps":[[0,1,1],[1,3,1],[2,5,1],[3,8,1],[4,1,1],[5,3,1],[6,5,1],[7,8,1],[8,1,1],[9,3,1],[10,5,1],[11,8,1],[12,1,1],[13,3,1],[14,5,1],[15,8,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("octane_rig","supersaw","the octave bass = chip_bass/bass_warm playing R-r' 8ths/16ths (write the octave INTO the notes — it IS the genre); Prophet arp stabs = supersaw; clap_909 + four-floor kick_punch; Simmons toms = timpani pitched high w/ short decay; bright, relentless, campy")]),
]


def seed():
    kg = KG()
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, PROV, desc=d)
    for g in G:
        kg.upsert("Genre", g["name"], PROV, bpm_lo=g["bpm"][0], bpm_hi=g["bpm"][1],
                  common_key=g["key"], voicing=json.dumps(g["voicing"]), form_family=g["form"])
    for g in G:
        name = g["name"]
        for i, t in enumerate(g["tech"]):
            kg.link("Genre", name, "USES_TECHNIQUE", "Technique", t, weight=round(1.0 - i * 0.08, 2))
        pname, pdesc, pgrid = g["pattern"]
        kg.upsert("PatternArchetype", pname, PROV, desc=pdesc, grid=json.dumps(pgrid))
        kg.link("Genre", name, "CHARACTERIZED_BY", "PatternArchetype", pname)
        mt = g["mix"]; mt_name = f"{name}_mix"
        kg.upsert("MixTarget", mt_name, PROV, lufs_lo=mt["lufs_lo"], lufs_hi=mt["lufs_hi"],
                  band_order=mt["band_order"], clipped_samples=mt["clipped"],
                  mid_floor_pct=mt.get("mid_floor"), himid_floor_pct=mt.get("himid_floor"))
        kg.link("Genre", name, "TARGETS", "MixTarget", mt_name)
        for sname, voice, sdesc in g["sounds"]:
            kg.upsert("SoundRecipe", sname, PROV, voice=voice, desc=sdesc)
            kg.link("Genre", name, "CHARACTERIZED_BY", "SoundRecipe", sname)
        for p in g["parents"]:
            kg.link("Genre", name, "SUBGENRE_OF", "Genre", p)
        for d in g["derived"]:
            kg.link("Genre", name, "DERIVED_FROM", "Genre", d, citation=CITE)

    n_gen = kg.q("MATCH (g:Genre) RETURN count(g)")[0][0]
    n_tech = kg.q("MATCH (t:Technique) RETURN count(t)")[0][0]
    print(f"seeded {len(G)} genres (+{len(NEW_TECH)} techniques). graph now: "
          f"{n_gen} genres, {n_tech} techniques.")
    for g in G:
        v = kg.genre_view(g["name"])
        print(f"  {g['name']:14s} parents={v['parents']} tech={len(v['techniques'])} "
              f"inherited={len(v['inherited_techniques'])} mix={bool(v['mixtargets'])}")


if __name__ == "__main__":
    seed()
