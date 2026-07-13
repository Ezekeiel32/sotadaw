#!/usr/bin/env python3
"""KG curation wave (2026-07-06): THE GUITAR-BAND + MODERN-JAZZ CANON — 15 genres the
graph had only generic `rock`/`metal`/`jazz` stand-ins for. Session `genre-forge`
(campaign: genre-research-campaign). Every genre SUBGENRE_OF rock|metal|jazz so it
INHERITS the parent's techniques in the compiled skill, then adds its own distinctive
DNA. Deep web-research provenance -> docs/research_bands_jazz_sota.md. Idempotent (MERGE).

  rock lineage : surf_rock, krautrock, grunge, stoner_rock, math_rock, midwest_emo
  metal lineage: black_metal, death_metal, doom_metal(+sludge), metalcore, post_metal
  jazz lineage : bebop, hard_bop, modal_jazz, spiritual_jazz
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research "
        "DNA, sources in docs/research_bands_jazz_sota.md)")
CITE = "curated:claude/2026-07-06-bandsjazz"

# ---- new Technique nodes (desc rides VERBATIM into the compiled skill) ----
NEW_TECH = {
 # --- heavy / extreme guitar ---
 "tremolo_picking": "continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing)",
 "traditional_blast_beat": "single-stroke blast: snare on every off-16th, kick on every on-16th (continuous roll), ride/crash in unison with the kick, NO backbeat pocket — felt as pure motion at 180+ BPM",
 "bomb_blast": "bomb blast: snare on every 8th over 16th-note double-kick (Cannibal Corpse) — the articulate, clicky death-metal blast",
 "double_bass_gallop": "fast continuous double-kick under a tremolo or galloped riff — the low-end engine of extreme metal",
 "gallop_rhythm": "d-U-d-d 16th gallop palm-muted on the low string — driving verse propulsion (metalcore, thrash lineage)",
 "breakdown_chug": "half-time palm-muted low-open-string staccato hits with RESTS for mosh weight — the space IS the heaviness (metalcore)",
 "half_time_breakdown": "at the breakdown the backbeat HALVES (snare to beat 3) and chug density thins — the structural payoff, not a jam",
 "downtuned_power_chord": "slow, sustained root-fifth chords rung across whole bars, heavily downtuned — the Sabbath/Iommi trudge (doom)",
 "downtuned_groove": "a syncopated downtuned power-chord riff with air between the hits — the space between IS the groove (stoner)",
 "dissonant_tritone": "flat-fifth / minor-second interval clusters for cold, atonal dread (black & death metal)",
 "chromatic_riff": "semitone-crawling, key-agnostic riffing — note-collections over tonality (death metal)",
 "hm2_buzzsaw": "a Boss HM-2 with EVERY knob maxed into a cranked amp = the Swedish 'buzzsaw' wall of distortion (Entombed / Sunlight Studio)",
 "death_growl": "a guttural, false-cord low vocal roar — the death-metal voice",
 "rasp_shriek_vocal": "a high, distorted, throat-forward black-metal shriek, mixed BACK behind the guitars",
 "necro_lo_fi": "DELIBERATE low fidelity (4-track/cassette): thin trebly guitars, buried vocals, tape hiss as texture — the 'necro' aesthetic (black metal)",
 "open_power_chords": "un-muted RINGING power chords (not palm-muted) so the trebly wall sustains (black metal)",
 "melodic_minor_riff": "a long, mournful harmonic/natural-minor tremolo melody riding over the blast (black metal)",
 "harmonized_lead": "twin-guitar thirds/sixths harmony lines lifted from melodic death metal (metalcore, death metal)",
 "scream_clean_dynamic": "a harsh-scream verse alternating with a big SUNG melodic chorus — built-in tension (metalcore)",
 "feedback_drone": "sustained amp feedback held over and between chords as texture — doom's connective tissue",
 "fuzz_wall": "stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom)",
 "doom_crawl": "a half-time / sub-60-BPM trudging pulse, huge spaced hits ringing across the whole bar",
 "sludge_stomp": "a dragged, dirty, hardcore-inflected mid-tempo groove with screamed vocals and feedback bleed (sludge)",
 "bluesy_bend": "slow pentatonic/blues string bends and heavy vibrato — the Southern lean (doom, stoner)",
 "epic_clean_vocal": "an operatic, sustained CLEAN vocal melody soaring over the crawl (epic doom)",
 "syncopated_power_chord": "a power-chord riff built on space and sustain, hits placed OFF the grid (stoner)",
 "wah_lead_sweep": "a Cry Baby wah realized as a filter-automation sweep on the solo (stoner)",
 "pentatonic_minor_riff": "a minor-pentatonic (root-b3-4-5-b7) bluesy riff — the desert/grunge/doom lick",
 "drop_d_powerchord": "one-finger low-D (drop-D) power-chord riffing (grunge, metalcore)",
 "eb_standard_detune": "tune a half-step down (Eb standard) for thickness and weight (grunge)",
 "vocal_harmony_dread": "stacked minor two-part vocal harmonies (Layne Staley + Jerry Cantrell) — dread as melody (grunge)",
 # --- dynamics / crescendo / long-form ---
 "quiet_loud_dynamics": "the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo)",
 "long_crescendo": "a multi-minute dynamic build from one sparse layer to an overwhelming/ecstatic climax — AUTOMATE it (late-bloom curve), never jump-cut it (post-metal, spiritual jazz)",
 "pedal_drone": "a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock)",
 "tremolo_wall": "a fast-picked distorted chord wash detonating at the climax (post-metal)",
 "tectonic_lowend": "downtuned bass and guitar in UNISON for physical sub weight (post-metal, doom)",
 "ambient_interlude": "a clean/effected/orchestral breather between heavy movements (post-metal, black metal)",
 "layered_tuning_stack": "several differently-tuned guitars stacked for a dense harmonic haze (post-metal)",
 "additive_arrangement": "the piece evolves by LAYERS entering and exiting over long spans, not by verse/chorus (krautrock, post-metal, spiritual jazz)",
 # --- math / emo ---
 "odd_meter_riff": "a riff in 5/4, 7/8, 11/8 or 13/8 with additive groupings (e.g. 2+2+3) — the meter IS the hook (math rock)",
 "polymeter": "a fixed-length melodic cell cycled over a differently-lengthed drum bar so the accents walk and re-sync (math rock)",
 "tapped_arpeggio": "bright, clean two-hand TAPPED arpeggio cascades — every note articulate (math rock, emo)",
 "angular_riff": "wide-interval, disjunct, stop-start melodic lines (math rock)",
 "start_stop_dynamics": "abrupt full-band CUTS and re-entries as structural seams (math rock)",
 "counterpoint_interplay": "independent contrapuntal guitar and bass lines rather than root-support (math rock)",
 "metric_modulation": "the tempo re-pivots by reinterpreting the note value — a felt gear-change (math rock)",
 "twinkly_arpeggio": "fingerpicked cascading OPEN-string arpeggios that ring and overlap — the twinkle (midwest emo)",
 "open_tuning_chime": "open tunings (FACGCE, DADGAD) so strummed shapes ring as lush extended chords with droning open strings (midwest emo)",
 "unconventional_voicing": "maj7 / add9 / sus2 recolorings in place of plain triads — one note changes everything (emo, math rock)",
 "hemiola_pattern": "2-against-3 overlapping guitar phrases — dreamy but math-y (midwest emo)",
 "untrained_earnest_vocal": "a heartfelt, imperfect, slightly off-key confessional delivery — the imperfection IS the point (midwest emo)",
 # --- surf / krautrock ---
 "spring_reverb_wash": "the drippy, bright, LONG outboard spring-tank splash — surf's actual fingerprint (distinct from plate/hall)",
 "phrygian_dominant_run": "a hijaz / double-harmonic exotic melodic run (the Misirlou lick) tremolo-picked on a low string (surf)",
 "whammy_dive": "a vibrato-arm downward pitch-bend — a pitch-automation dip on the lead (surf)",
 "bridge_pickup_twang": "a bright, close-to-the-bridge single-coil pick attack — maximum twang (surf)",
 "surf_beat_tom_roll": "the tom-forward surf drum beat with rimshots and rolls (Wipe Out)",
 "motorik_pulse": "the MOTORIK beat: kick on the downbeat (often 1 & 3), snare backbeat on 2 & 4, unbroken even 8th-notes on the hats, and NO fills — linear 'autobahn' propulsion (krautrock)",
 "harmonic_stasis": "one or two chords held as a drone; the tension comes from repetition, not changes (krautrock)",
 "hypnotic_repetition": "an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom)",
 "analog_sequencer_arp": "a locked analog-synth arpeggio riding the steady pulse (krautrock)",
 "tape_echo_space": "tape-echo, phasing and spatial treatment used AS an instrument (Conny Plank; krautrock)",
 # --- jazz: bebop / hard bop / modal / spiritual ---
 "ii_V_I_changes": "dense functional ii-V-I cells at a fast harmonic rhythm (often two chords a bar) — the bebop engine",
 "chromatic_bebop_line": "bebop-scale 8th-note lines: a chromatic passing tone inserted so chord tones land on the STRONG beats",
 "rhythm_changes": "the 'I Got Rhythm' AABA 32-bar cycle used as a contrafact blowing vehicle (bebop)",
 "tritone_substitution": "reharmonize a V7 with the bII7 a tritone away for chromatic voice-leading (bebop)",
 "trading_fours": "soloists and the drummer alternate 4-bar phrases near the out-head (bebop, hard bop)",
 "backbeat_accent": "ride spang-a-lang but with the hi-hat/snare hit HARD on 2 & 4 (or a shuffle) — the bop -> hard-bop groove shift",
 "gospel_blues_piano": "funky rootless and gospel BLOCK-chord comping with blue notes and grace-note bends (hard bop, soul jazz)",
 "twelve_bar_blues": "the 12-bar blues as head and blowing form — central to hard bop",
 "soul_jazz_groove": "a riff/vamp-based, danceable, R&B- and gospel-inflected groove (hard bop / soul jazz)",
 "afro_latin_vamp": "a straight-eighth montuno / calypso vamp section bookending the swung blowing (hard bop — Song for My Father)",
 "modal_vamp": "hold a single scale/mode for 8-16 bars and improvise FROM the mode, not the changes (modal & spiritual jazz)",
 "quartal_voicing": "chords built by stacking FOURTHS — the 'So What' chord (Bill Evans / McCoy Tyner); rootless, open, harmonically ambiguous",
 "slow_harmonic_rhythm": "two or three chords across an ENTIRE tune — harmony as a held space (modal jazz)",
 "scalar_improvisation": "solo lines drawn from the mode's scale rather than spelling fast changes (modal jazz)",
 "rootless_comping": "the piano omits the root, leaving it to the bass, and voices only the color tones (modal, hard bop)",
 "contrafact": "a new head written over an existing modal/harmonic frame (Impressions <- So What)",
 "pentatonic_wail": "an overblown minor-pentatonic saxophone CRY climbing into the ecstatic register (spiritual jazz)",
 "coltrane_sheets": "sheets-of-sound cascades and multiphonic overblowing (spiritual jazz)",
 "hand_percussion_layer": "congas, tambourine and bells stacked polyrhythmically over the kit (spiritual jazz)",
 "devotional_climax": "the ecstatic free/collective PEAK that resolves back to calm — the spiritual arc's payoff",
 "tanpura_drone": "a sustained Indian-classical tonic drone (tanpura/tambura or a bass ostinato) under the whole vamp (spiritual jazz)",
}

# ---- the 15 genres ----
# each: bpm, key, voicing{style,lo,hi}, parents(SUBGENRE_OF), derived(DERIVED_FROM),
#       tech[ordered, most-defining first], pattern(name,desc,grid), mix, sounds[(name,voice,desc)]
G = [
 dict(name="surf_rock", bpm=(150,180), key="E minor", form="song",
   voicing={"style":"twangy_single_note","lo":40,"hi":76}, parents=["rock"], derived=[],
   tech=["tremolo_picking","spring_reverb_wash","phrygian_dominant_run","whammy_dive","bridge_pickup_twang","surf_beat_tom_roll","pentatonic_minor_riff"],
   pattern=("surf_beat","Tremolo-picked hijaz lead over the driving surf beat (~160 BPM, 4/4 straight): kick 1&3, snare 2&4, 8th ride, bass drives root 8ths; the lead is a continuous 16th tremolo line drenched in a long bright spring tank.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"4":0.95,"12":1.0}},"chords":[[0,1],[2,1]],
      "lead":{"voice":"pluck","octave":4,"steps":[[0,1,1],[2,7,1],[4,1,1],[6,2,1],[8,3,2],[12,1,2]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":12.0},
   sounds=[("surf_twang","pluck","bright single-coil pluck, tremolo-picked, into a LONG bright spring-tank fx_reverb + short slap fx_delay; light amp-breakup fx_saturate only, NEVER fuzz")]),

 dict(name="krautrock", bpm=(110,150), key="A major", form="song",
   voicing={"style":"droning_steady","lo":33,"hi":81}, parents=["rock"], derived=[],
   tech=["motorik_pulse","harmonic_stasis","hypnotic_repetition","analog_sequencer_arp","additive_arrangement","tape_echo_space","pedal_drone"],
   pattern=("motorik_beat","THE MOTORIK BEAT (~140 BPM, 4/4, 0% swing): kick on 1 (&3), snare on 2&4, unbroken even-8th hats, NO fills; bass = constant 8th root pedal; one droning chord held. Every bar identical — the variation lives only in slowly-morphing texture on top.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"hat":{"0":0.9,"2":0.7,"4":0.9,"6":0.7,"8":0.9,"10":0.7,"12":0.9,"14":0.7}},"chords":[[0,1]],
      "lead":{"voice":"supersaw","octave":4,"steps":[[0,1,4],[8,5,4]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("motorik_drone","supersaw","a held saw drone + a locked analog_sequencer_arp; tape-echo fx_delay, a SLOW automated fx_filter LP sweep = 'the evolution'; drums dead-straight, no fills; optional slow tempoMap accelerando as the build")]),

 dict(name="grunge", bpm=(90,160), key="E minor", form="song",
   voicing={"style":"gritty_powerchord","lo":38,"hi":64}, parents=["rock"], derived=[],
   tech=["quiet_loud_dynamics","fuzz_wall","drop_d_powerchord","pentatonic_minor_riff","eb_standard_detune","vocal_harmony_dread","palm_mute_chug"],
   pattern=("quiet_loud","Quiet clean verse -> loud fuzz chorus (~117 BPM, 4/4 straight). VERSE: clean/lightly-driven guitar, restrained backbeat, bass carries motion. CHORUS: fuzz power chords on the downbeats, crash-forward drums, doubled panned guitars. The defining event is the dynamic JUMP (a gain/saturation automation step), not one note grid.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,6,8],"snare":[4,12],"hat":[0,4,8,12],
      "vel":{"snare":{"4":1.0,"12":1.0}},"chords":[[0,1],[1,6],[2,4],[3,1]],
      "lead":{"voice":"guitar_grit","octave":3,"steps":[[0,1,2],[2,1,1],[4,6,2],[8,4,2],[12,1,2]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"lowmid>low>mid","clipped":0},
   sounds=[("grunge_fuzz","guitar_grit","guitar_grit into HEAVY fx_saturate (Big-Muff character) + mid-focused fx_filter for the chorus; near-BYPASS saturation for the clean verse -- the verse->chorus GAIN AUTOMATION (curve <0, early-jump) is the song. Preserve dynamics at master (DR11-12 feel, NOT a -8 brickwall).")]),

 dict(name="stoner_rock", bpm=(65,120), key="C minor", form="song",
   voicing={"style":"downtuned_riff","lo":33,"hi":55}, parents=["rock"], derived=["doom_metal","metal"],
   tech=["downtuned_groove","fuzz_wall","pentatonic_minor_riff","syncopated_power_chord","hypnotic_repetition","wah_lead_sweep","bluesy_bend"],
   pattern=("desert_groove","The downtuned fuzz groove riff (~90 BPM, 4/4, straight-to-slightly-behind ~53%): a syncopated root-fifth power-chord figure on the low strings (Drop C/D), kick locks the riff hits, snare cracks 2&4, riff cycles every 1-2 bars ending on a ringing sustained chord.",
     {"bars":1,"swing":0.53,"bass_style":"roots","kick":[0,3,8],"snare":[4,12],"hat":[0,4,8,12],
      "chords":[[0,1],[2,1],[3,4]],"lead":{"voice":"guitar_grit","octave":2,"steps":[[0,1,3],[6,4,1],[8,1,3]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"lowmid>low>mid","clipped":0},
   sounds=[("desert_fuzz","guitar_grit","downtuned guitar_grit through THICK fx_saturate + a low-mid fx_filter wall; bass_warm with light drive doubling near-lead; wah = an fx_djfilter/fx_filter sweep automated on leads; analog-warm, not brickwalled")]),

 dict(name="math_rock", bpm=(90,170), key="D major", form="song",
   voicing={"style":"bright_extended","lo":38,"hi":88}, parents=["rock"], derived=[],
   tech=["odd_meter_riff","polymeter","tapped_arpeggio","angular_riff","start_stop_dynamics","counterpoint_interplay","unconventional_voicing","metric_modulation"],
   pattern=("odd_meter_cell","The odd-meter cell: 7/8 grouped 2+2+3 (~150 BPM, clean tone). Accents on the group heads (8th-slots 1,3,5); drums lock the 2+2+3 while the bass runs a contrapuntal line -- or flip to POLYMETER (a 4-note guitar cell over the 7/8 bar so the downbeat drifts and re-syncs every 8 bars). [16-slot grid approximates the 4/4 read; encode the true 7/8 in section time-sigs via tempoMap.]",
     {"bars":1,"swing":0.5,"bass_style":"walking","kick":[0,8],"snare":[4],"hat":[0,2,4,6,8,10,12,14],
      "chords":[[0,1],[2,5]],"lead":{"voice":"pluck2","octave":4,"steps":[[0,1,1],[2,5,1],[4,3,1],[6,7,1],[8,1,1],[10,4,1],[12,6,1]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":12.0},
   sounds=[("clean_chime","pluck2","bright CLEAN pluck arpeggios, minimal saturation, light fx_delay for tapped cascades + a small fx_reverb; two tracks panned L/R for counterpoint legibility; tempoMap drives the meter/tempo pivots; preserve transient crest at master (do NOT limit hard)")]),

 dict(name="midwest_emo", bpm=(90,155), key="F major", form="song",
   voicing={"style":"open_arpeggio","lo":38,"hi":76}, parents=["rock"], derived=["math_rock","indie_rock"],
   tech=["twinkly_arpeggio","open_tuning_chime","unconventional_voicing","hemiola_pattern","quiet_loud_dynamics","tapped_arpeggio","untrained_earnest_vocal"],
   pattern=("twinkle_cell","The twinkly arpeggio cycle: a fingerpicked open-tuning (FACGCE) maj7/add9 arpeggio in 6/8 (~140 BPM, light swing ~55%); notes RING and overlap (long lengths, no muting), ascending then cascading, one guitar's cycle displaced against the other's for a 2-against-3 hemiola.",
     {"bars":1,"swing":0.55,"bass_style":"roots","kick":[0,8],"snare":[4,12],"hat":[0,3,6,9,12],
      "chords":[[0,1],[2,4]],"lead":{"voice":"pluck","octave":4,"steps":[[0,1,2],[3,5,2],[6,3,2],[9,6,2],[12,1,2]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-11,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":12.0},
   sounds=[("twinkle_guitar","pluck","fingerpicked OPEN-tuning pluck arpeggios, DRY, a medium plate fx_reverb + a triplet/dotted fx_delay; ringing open strings, hard-panned pair; a dedicated ringing clean-chime voice would elevate; intimate, un-brickwalled master (high crest)")]),

 dict(name="black_metal", bpm=(140,250), key="E minor", form="song",
   voicing={"style":"cold_trebly","lo":40,"hi":72}, parents=["metal"], derived=[],
   tech=["tremolo_picking","traditional_blast_beat","dissonant_tritone","open_power_chords","melodic_minor_riff","necro_lo_fi","rasp_shriek_vocal","hypnotic_repetition"],
   pattern=("frostbite_blast","'Frostbite Blast' (~190 BPM, 4/4, 0% swing): traditional blast = snare on every off-16th, kick on every on-16th (continuous single-stroke roll), crash/ride with each kick, NO backbeat; one power-chord root tremolo-picked as unbroken 16ths, the chord changing every 1-2 bars while the picking never stops. The groove is the ABSENCE of a pocket -- pure forward blur.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,2,4,6,8,10,12,14],"snare":[1,3,5,7,9,11,13,15],"ride":[0,2,4,6,8,10,12,14],
      "chords":[[0,1],[8,6]],"lead":{"voice":"guitar_grit","octave":4,"steps":[[0,1,1],[1,2,1],[2,3,1],[3,1,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-8,"band_order":"mid>lowmid>low","clipped":0,"himid_floor":2.0},
   sounds=[("frost_tremolo","guitar_grit","TREBLY guitar_grit (HP ~120 Hz, presence lift, mids KEPT -- do NOT scoop) tremolo-picked; a cold fx_reverb on a bus; double-tracked thin. Aesthetic is fidelity, not loudness -- keep it raw and treble-forward")]),

 dict(name="death_metal", bpm=(90,220), key="B minor", form="song",
   voicing={"style":"guttural_chromatic","lo":33,"hi":59}, parents=["metal"], derived=[],
   tech=["palm_mute_chug","bomb_blast","hm2_buzzsaw","chromatic_riff","double_bass_gallop","death_growl","half_time_breakdown","tremolo_picking"],
   pattern=("bomb_blast_chug","'Bomb-Blast Chug' (~200 BPM, 4/4, straight): bomb blast = snare on every 8th, double-kick on every 16th, crash on bar-heads; guitar palm-mutes the low root (B1/C2) as 16ths with chromatic passing tones; at the section break the kit HALVES to a ~100-BPM half-time breakdown with the same riff at quarter-note weight.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],"snare":[0,2,4,6,8,10,12,14],"ride":[0,4,8,12],
      "chords":[[0,1]],"lead":{"voice":"guitar_grit","octave":2,"steps":[[0,1,1],[2,1,1],[4,2,1],[6,1,1],[8,1,1],[10,3,1],[12,1,1]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-6,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("buzzsaw","guitar_grit","guitar_grit at MAX fx_saturate (the HM-2 buzzsaw) + a bandpass fx_filter (Swedish = mid-bump ~1 kHz; Florida = tight HP ~90 Hz + slight scoop); hard L/R double-track; loud, tight, gated low end; a blast-capable clicky kick is the biggest render gap")]),

 dict(name="doom_metal", bpm=(40,110), key="C# minor", form="song",
   voicing={"style":"leaden_crush","lo":33,"hi":55}, parents=["metal"], derived=[],
   tech=["downtuned_power_chord","doom_crawl","feedback_drone","fuzz_wall","bluesy_bend","dissonant_tritone","epic_clean_vocal","sludge_stomp"],
   pattern=("iommi_crawl","'Iommi Crawl' (~65 BPM, 4/4, straight-to-behind): kick on 1, snare on 3 (a HUGE half-time backbeat, heavy room reverb), sparse fills; a single downtuned power chord struck on beat 1 and left to RING and decay across the bar, moving every 1-2 bars through a minor riff; feedback bleeds in the gaps; bass doubles the guitar an octave-fat. (Sludge variant = same skeleton ~85 BPM, dirtier, screamed, occasional d-beat burst.)",
     {"bars":1,"swing":0.53,"bass_style":"sustained","kick":[0],"snare":[8],"ride":[0,4,8,12],
      "vel":{"snare":{"8":1.0}},"chords":[[0,1]],"lead":{"voice":"guitar_grit","octave":2,"steps":[[0,1,8]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("iommi_wall","guitar_grit","downtuned guitar_grit + sub_clean in unison, WARM heavy fx_saturate (not bright), a gentle LP keeping mids + huge low, a large room/hall fx_reverb; long sustained hits + a low-level held drone track for feedback; let the slow hits BREATHE (higher crest than death metal)")]),

 dict(name="metalcore", bpm=(80,200), key="C minor", form="song",
   voicing={"style":"chug_powerchord","lo":35,"hi":76}, parents=["metal"], derived=["punk"],
   tech=["breakdown_chug","scream_clean_dynamic","half_time_breakdown","gallop_rhythm","harmonized_lead","drop_d_powerchord","palm_mute_chug"],
   pattern=("breakdown","'The Breakdown' (~130 BPM, 4/4, half-time feel): palm-muted low-open-string (Drop-C) chugs on a syncopated grid WITH RESTS for weight, crash+kick accent the downbeat of each 2-bar cycle, snare pinned to beat 3 (the half-time backbeat), double-kick filling the chug gaps. The verse gallops; the CHORUS is a wide sung melody; the breakdown is the payoff.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,3,4,7,8,11,12,15],"snare":[8],"ride":[0],
      "chords":[[0,1]],"lead":{"voice":"guitar_grit","octave":2,"steps":[[0,1,1],[3,1,1],[4,1,1],[7,1,1],[8,1,2],[11,1,1],[12,1,1]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-6,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("core_chug","guitar_grit","drop-tuned guitar_grit, hard fx_saturate + a cab-tame fx_filter (HP ~80, LP ~7k), hard L/R double; the breakdown is an ARRANGEMENT half-time (thin note density + snare-to-3), NOT a tempo change; an fx_djfilter riser + fx_trim lift into the drop")]),

 dict(name="post_metal", bpm=(40,160), key="D minor", form="song",
   voicing={"style":"tectonic_pedal","lo":33,"hi":69}, parents=["metal"], derived=["doom_metal"],
   tech=["long_crescendo","quiet_loud_dynamics","pedal_drone","tremolo_wall","hypnotic_repetition","tectonic_lowend","ambient_interlude","layered_tuning_stack"],
   pattern=("crescendo","'The Crescendo' (~70 BPM, 4/4 or 6/8): a 4-8-bar pedal-tone/power-chord motif repeated 8-16x; movement is VERTICAL not horizontal -- start with a single clean tremolo note + brushed cymbal, each repeat adds a layer (2nd guitar -> distortion engages -> bass sub -> double-bass + crash wall) so the SAME motif detonates as a full distorted climax by the last cycle. The 'hit' is the payoff downbeat where the wall lands.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,8],"snare":[8],"ride":[0,2,4,6,8,10,12,14],
      "chords":[[0,1]],"lead":{"voice":"guitar_grit","octave":3,"steps":[[0,1,4],[8,1,4]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("tectonic_layers","guitar_grit","2-3 guitar_grit layers at octaves/detunes feeding a SHARED reverb BUS for the wash; clean valleys = keys_dark/pad_motion + a big fx_reverb; THE CRESCENDO IS AUTOMATION -- fx_trim gain + fx_saturate drive + reverb-send + layer mute-ins over 60-120s with a LATE-BLOOM curve (point curve >0). Do NOT brickwall (preserve the arc).")]),

 dict(name="bebop", bpm=(120,320), key="F major", form="song",
   voicing={"style":"rootless_chromatic","lo":28,"hi":86}, parents=["jazz"], derived=["swing_bigband"],
   tech=["ii_V_I_changes","chromatic_bebop_line","walking_bass","swing_ride","rhythm_changes","tritone_substitution","jazz_comping","trading_fours"],
   pattern=("swing_head","Swing ride + four-feel walk (medium-up ~208 BPM, swing ~60% ~2:1). Ride: quarter on every beat + the last triplet-8th after 2 & 4 (spang-a-lang); hi-hat foot on 2 & 4; walking bass quarters (root -> chromatic-approach -> next chord tone); piano comps 2-3 short rootless chunks per bar, OFF the beat. At burnout tempos flatten swing toward 52-55%.",
     {"bars":1,"swing":0.6,"bass_style":"walking","kick":[0],"ride":[0,4,6,8,12,14],"hat":[4,12],
      "vel":{"ride":{"0":1.0,"6":0.8,"14":0.8},"hat":{"4":0.7,"12":0.7}},"chords":[[0,2],[1,5],[2,1],[3,6]],
      "lead":{"voice":"sax_section","octave":5,"steps":[[0,1,1],[2,2,1],[4,3,1],[6,5,1],[8,1,1],[10,7,1],[12,2,1],[14,1,1]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-13,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0,"himid_floor":1.0},
   sounds=[("bop_combo","rhodes","rhodes/keys for bebop comping (a felt jazz_piano voice would elevate), sax_section + brass_stab as the unison horn front line, bass_warm walking, ride-forward kit; PAN hard L/C/R (Blue Note image, not fx_widen), a short room fx_reverb + tape fx_saturate -- do NOT compress (keep the swing snap)")]),

 dict(name="hard_bop", bpm=(70,240), key="F minor", form="song",
   voicing={"style":"gospel_block","lo":28,"hi":82}, parents=["jazz"], derived=["bebop"],
   tech=["backbeat_accent","gospel_blues_piano","walking_bass","swing_ride","twelve_bar_blues","soul_jazz_groove","afro_latin_vamp","trading_fours"],
   pattern=("backbeat_shuffle","Backbeat-driven swing shuffle (medium ~132 BPM, swing ~65% ~2:1). Ride spang-a-lang; snare cross-stick / hi-hat accented HARD on 2 & 4 (the backbeat drive); walking bass, bluesier and more repetitive (or a 2-bar riff on soul/Latin tunes); piano lays gospel block-chord stabs + bluesy fills. Latin sections switch to STRAIGHT eighths (swing 50%) montuno.",
     {"bars":1,"swing":0.65,"bass_style":"walking","kick":[0],"snare":[4,12],"ride":[0,4,6,8,12,14],"hat":[4,12],
      "vel":{"snare":{"4":0.9,"12":0.9}},"chords":[[0,2],[1,5],[2,1],[3,1]],
      "lead":{"voice":"brass_stab","octave":4,"steps":[[0,1,2],[4,3,2],[8,5,2],[12,1,2]]}}),
   mix={"lufs_lo":-17,"lufs_hi":-12,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0,"himid_floor":1.0},
   sounds=[("blue_note_combo","organ_soul","organ_soul / rhodes gospel block-chord comping, sax_section + brass_stab HARMONIZED front line, bass_warm walking, backbeat-accented kit; vibraphone as a Blue Note color; a short plate fx_reverb + a touch more tape warmth than bebop; keep it dynamic")]),

 dict(name="modal_jazz", bpm=(60,300), key="D dorian", form="song",
   voicing={"style":"quartal_open","lo":28,"hi":84}, parents=["jazz"], derived=["bebop"],
   tech=["modal_vamp","quartal_voicing","slow_harmonic_rhythm","pedal_drone","scalar_improvisation","rootless_comping","swing_ride","contrafact"],
   pattern=("so_what_vamp","'The So What vamp' (32-bar AABA at ~134 BPM, swung ~64%). Upright bass states the 2-bar D-Dorian riff, piano ANSWERS with the So What quartal stab (E-A / D-G-B) syncopated on the 'and'; ride plays swung spang-a-lang, hi-hat on 2 & 4, kick feathered. Bridge: transpose the whole call-and-response up a half-step to Eb Dorian for 8 bars, then back.",
     {"bars":1,"swing":0.64,"bass_style":"walking","kick":[0],"ride":[0,4,6,8,12,14],"hat":[4,12],
      "chords":[[0,1],[2,1]],"lead":{"voice":"rhodes","octave":4,"steps":[[2,1,2],[6,4,2],[10,5,2]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-13,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0},
   sounds=[("modal_combo","rhodes","rhodes QUARTAL comping over a bass_warm modal PEDAL, sax_section lead, ride-forward kit; ONE shared room-reverb SEND bus (buses[]+sends[]); a long AABA vamp; build intensity over the solo via gainDb + reverb-send AUTOMATION (late-bloom curve >0); steady tempoMap")]),

 dict(name="spiritual_jazz", bpm=(60,160), key="F minor", form="song",
   voicing={"style":"quartal_pedal_pentatonic","lo":28,"hi":88}, parents=["jazz"], derived=["modal_jazz"],
   tech=["modal_vamp","pedal_drone","pentatonic_wail","tanpura_drone","long_crescendo","quartal_voicing","hand_percussion_layer","devotional_climax"],
   pattern=("drone_build","'The A Love Supreme / Satchidananda drone-build' (~98-126 BPM, swung ~60%, or gridless free zones). A sustained tonic drone (tanpura + bass) under a short modal-minor bass ostinato (e.g. the 4-note 'a-love-su-preme' cell in F minor); McCoy-style piano lays a LH fifth-pedal + RH quartal stabs; Elvin-style ride pours triplets; tambourine + hand percussion layer in; the sax enters low and slowly climbs into pentatonic WAILS as the ensemble crescendos over 16+ bars to an ecstatic peak.",
     {"bars":1,"swing":0.6,"bass_style":"roots","kick":[0,8],"ride":[0,2,4,6,8,10,12,14],"hat":[4,12],
      "chords":[[0,1]],"lead":{"voice":"sax_section","octave":5,"steps":[[0,1,2],[4,4,1],[6,5,1],[8,1,3]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-14,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":8.0},
   sounds=[("devotional_combo","sax_section","sax_section pentatonic WAILS over a sustained drone (supersaw/pad held = tanpura stand-in) + a bass_warm ostinato, harp (Alice Coltrane) arpeggios, rhodes McCoy quartal+pedal comp, hand percussion; a DEEP long fx_reverb SEND bus; a multi-minute crescendo AUTOMATION (rising gain/reverb/opening filter, percussion entering); leave free sections un-quantized; keep highly dynamic")]),
]

# ---- jazz swing feel (Groove node; profile arrays live in library/grooves.json) ----
JAZZ_SWING_PROV = "curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat)"
JAZZ_SWING_GENRES = ["bebop", "hard_bop", "modal_jazz", "spiritual_jazz"]


def seed():
    kg = KG()
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, PROV, desc=d)
    # genres first (so intra-set DERIVED_FROM targets exist), then edges
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
        mt = g["mix"]
        mt_name = f"{name}_mix"
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
    # jazz swing groove
    kg.upsert("Groove", "jazz_swing", JAZZ_SWING_PROV)
    for gname in JAZZ_SWING_GENRES:
        kg.link("Genre", gname, "HAS_GROOVE", "Groove", "jazz_swing")

    n_gen = kg.q("MATCH (g:Genre) RETURN count(g)")[0][0]
    n_tech = kg.q("MATCH (t:Technique) RETURN count(t)")[0][0]
    print(f"seeded {len(G)} genres (+{len(NEW_TECH)} techniques). graph now: "
          f"{n_gen} genres, {n_tech} techniques.")
    for g in G:
        v = kg.genre_view(g["name"])
        print(f"  {g['name']:14s} parents={v['parents']} tech={len(v['techniques'])} "
              f"inherited={len(v['inherited_techniques'])} mix={bool(v['mixtargets'])} "
              f"grooves={[gr['name'] for gr in v['grooves']]}")


if __name__ == "__main__":
    seed()
