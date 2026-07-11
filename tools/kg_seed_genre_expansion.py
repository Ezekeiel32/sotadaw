#!/usr/bin/env python3
"""KG curation wave (2026-07-06): THE COVERAGE-EXPANSION 15 — world + guitar-lineage +
frontier genres the graph was BLANK on (South Asia, gamelan-world, key African lineages,
neo-soul, djent/post-rock, Berlin-school, future-funk, rage). Session `genre-scout`
(campaign: genre-research-campaign). Deep per-genre web research + adversarial verify ->
docs/research_genre_expansion_sota.md. Sibling wave: kg_seed_bands_jazz.py (genre-forge).
Idempotent (MERGE). Signature instruments map to the REAL faust palette; buildable .dsp
voices that would ELEVATE are named in each SoundRecipe desc.

  world/blank : gamelan, balkan_brass, bhangra, bollywood_filmi, ethio_jazz, kwaito,
                soukous, bluegrass, fado
  soul/guitar : neo_soul (<-soul,rnb), djent (<-metal), post_rock (<-rock)
  electronic  : berlin_school, future_funk (<-french_house), rage (<-trap)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research "
        "DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md)")
CITE = "curated:claude/2026-07-06-genrexp"

# ---- new Technique nodes (desc rides VERBATIM into the compiled skill) ----
NEW_TECH = {
 # --- gamelan ---
 "kotekan_interlock": "two parts (POLOS mostly on-beat + SANGSIH mostly off-beat) interlock into one stream twice as fast as either — Balinese kilitan-telu 3-note figures; neither player states the whole melody",
 "colotomic_cycle": "the structure is a nested gong cycle, NOT a backbeat: gong ageng marks the cycle END, kenong quarters it, kempul halves those, ketuk ticks the subdivisions — the strongest point is the cycle's last beat, not beat 1",
 "ombak_detune": "voice every pitch as a PAIR a few Hz apart (pengumbang + pengisep) so the sum beats and shimmers — ~5 Hz gender, ~7 Hz gong kebyar, ~8-9 Hz angklung; the beating IS the sound, do not tune it out",
 "slendro_pelog_tuning": "non-12-TET tuning: SLENDRO (5 near-equal ~240-cent steps) or PELOG (7 uneven steps played as 5-tone subsets); each ensemble tuned uniquely, no fixed reference pitch",
 "irama_density_shift": "tempo is a DENSITY level not a fixed pulse: as the drum slows the pulse, the elaborating instruments double their note-density to keep the surface busy (irama)",
 "kendang_cue": "the hand-drum pair (lanang high + wadon low) LEADS — all tempo, transitions and the final ritard (suwuk) are cued by the drum, never a click",
 # --- balkan brass ---
 "aksak_meter": "asymmetric 'limping' meter: 9/8 as 2+2+2+3 (cocek), 7/8 as 2+2+3, 11/8 as 2+2+2+2+3; accents on each subgroup head so the closing long '3' cell gives the trademark stumble",
 "hijaz_run": "a Phrygian-dominant / Hijaz melodic run (1 b2 3 4 5 b6 b7, augmented 2nd between b2 and 3) tremolo-ornamented with grace notes, mordents and chromatic slides",
 "oom_pah_engine": "tuba 'oom' on each aksak cell downbeat + alto/tenor horns chugging offbeat 'pah' chords between — the relentless propulsion under the trumpet",
 "davul_boom": "the double-headed davul: heavy beater booms the head of each cell (deep pitched sine, fast pitch-drop) + a thin switch ticks the offbeats and the long '3' cell",
 "brass_tutti_answer": "the full band answers the solo trumpet's phrase with a harmonized fortissimo tutti stab — call-and-response as arrangement",
 "accelerando_drive": "a continuous tempo push toward a frenzied climax (encode as a tempoMap ramp), the band getting faster and hotter until the final hit",
 # --- djent ---
 "polymetric_chug": "a fixed odd-length riff cell (3/16, 5/16, 7/16) cycled over a straight 4/4 kick/snare so the accents PHASE against the backbeat and re-sync every few bars — the polymeter is the hook",
 "extended_range_chug": "machine-tight straight-16th palm-muted single-note chugs on a 7/8/9-string's lowest string (drop tuning), gated silent between hits so the low end is percussive not sustained",
 "kick_follows_riff": "the kick drum doubles EVERY chug hit exactly (riff and kick are one rhythm), snare pinned to 2 & 4 as the only steady backbeat",
 "djent_thall": "the 'thall' articulation: a slack, pick-scraped, almost-bend low-string chug with a rounded pitched attack (Meshuggah/Fredrik Thordendal), heavier than a clean palm-mute",
 "ambient_clean_bloom": "lush reverbed clean/quartal-arpeggio interludes (major9 / add-color guitars, often odd meter) that make the returning chug feel heavier by contrast",
 "poly_over_common": "riff written so a repeating melodic figure of one length rides a bar of another length — 'djent math' that resolves on a big downbeat every 2-4 bars",
 # --- ethio-jazz ---
 "tizita_mode": "the TIZITA qenet: a nostalgic Ethiopian major-type pentatonic (1 2 3 5 6) — the wistful, homesick color at the heart of Ethio-jazz",
 "ethio_pentatonic_qenet": "melodies drawn from one of the four Ethiopian pentatonic qenet (tizita, ambassel [1 2 3 5 b6, natural 2nd/lowered 6th], bati, anchihoye) over Western jazz harmony",
 "compound_latin_swing": "a languid Latin-jazz lilt: swung ride over an even kick-snare, congas + kebero laying 6-against-4 / 12-8 cross-rhythm against the 4/4 — the Astatke groove",
 "vibraphone_lead_ethio": "vibraphone (motor tremolo on) carries the modal head, doubled by organ/Wurlitzer — the signature Ethio-jazz timbre",
 "modal_ostinato_vamp": "a short repeating bass + horn riff held under long modal solos — vamp-based, minimal chord motion",
 "kebero_crossrhythm": "the kebero hand-drum + congas stack a 6/8 triplet cross-pulse against the straight kit, giving the groove its rolling, off-square feel",
 # --- berlin school ---
 "analog_sequence_16th": "a locked 16th-note analog-synth sequence (Moog 960-style) is the whole engine — pitched pattern of 8-16 steps looped for minutes, evolving only by filter/gate",
 "delay_fill_sequence": "sequence programmed note-then-rest so a synced delay fills the gaps — the delay repeats become part of the melodic line, doubling the perceived density",
 "evolving_texture": "the 'composition' is a slow morph: layers fade in/out and a filter cutoff opens over minutes; no verse/chorus, the journey is the form",
 "sequencer_pedal_drone": "a sustained tonic drone / pedal held under the moving sequence — Aeolian-modal, few or no chord changes, tension from repetition",
 "mellotron_pad_wash": "a Mellotron-style tape-choir/strings pad laid over the sequence for warmth and slow harmonic swells (Tangerine Dream)",
 "drumless_pulse": "often NO kit at all — the 16th sequence provides the pulse; when drums enter they are a simple motorik or a slow kick, never busy",
 # --- neo-soul ---
 "dilla_drunk_swing": "the J Dilla 'drunk' pocket: the snare dragged ~20-50 ms LATE and hats pushed/pulled OFF the grid so the beat lurches — deliberately un-quantized, the wobble is the feel",
 "extended_jazz_chords": "m9, m11, maj9, 13 and dominant-alt voicings (rootless, close) replacing plain triads — Dorian/lush harmony borrowed from jazz",
 "behind_beat_bass": "the bass sits slightly BEHIND the kick (fingered/foam-muted P-bass, rounded), locking to the late snare for the laid-back drag",
 "rhodes_comp_neo": "warm Fender Rhodes (or Wurlitzer) comps the extended chords with light chorus/phaser — the harmonic bed of neo-soul",
 "unquantized_live_kit": "a loose live/MPC-chopped kit with real velocity spread and timing slop — hats ghosted, snare fat and dark; never grid-locked",
 "chromatic_mediant_move": "surprise chord shifts by third (e.g. a bIII or VI borrowed) for the bittersweet neo-soul lift — reharm over a simple loop",
 # --- soukous ---
 "sebene_section": "the SEBENE: the fast, euphoric instrumental peak where interlocking lead guitars cycle a bright major riff over a driving groove while an atalaku shouts animations — the payoff of the song",
 "cavacha_churn": "the cavacha drum pattern: a continuous ghosted-16th snare/hi-hat churn with the backbeat on 2 & 4 and a near-every-beat kick — the rolling engine of Congolese dance music",
 "interlocking_guitars": "three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony",
 "atalaku_animation": "an animateur's rhythmic shouts and crowd-cries punctuate the sebene, cueing the dancers and lifting the energy",
 "static_major_harmony": "a bright, static major (Ionian) I-IV-V or single-chord vamp — harmony stays put so the guitar interlock and groove carry everything",
 # --- bhangra ---
 "chaal_rhythm": "the dhol CHAAL: Dha-Na-Na-Na / Na-Dha-Dha-Dha — the bass 'dagga' head hits the downbeat + push while the treble 'tilli' stick fills the eighths; THE bhangra pulse",
 "dhol_dagga_tilli": "the double-headed dhol: a deep bass 'dagga' side (booming, pitch-dropping) + a bright thin 'tilli' side (fast ticking treble) — program them as two separate percussion voices",
 "tumbi_riff": "the tumbi: a single high-pitched string plucked as a fast repeating ostinato riff — the piercing melodic hook that says 'bhangra' instantly",
 "boliyan_call_response": "call-and-response folk vocals (boliyan) traded over the groove; hooky, chant-like, energetic",
 "four_on_floor_club_layer": "modern UK/club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol/tumbi — folk on a dancefloor engine",
 # --- bluegrass ---
 "scruggs_roll": "Scruggs 3-finger banjo ROLLS: continuous syncopated 8th-note arpeggio patterns (forward/backward/alternating-thumb) that never stop — the perpetual-motion sparkle of bluegrass",
 "mandolin_chop": "the mandolin 'chop': a short, damped closed-chord stab on beats 2 & 4 — it IS the snare of a drumless string band",
 "boom_chuck_bass": "the upright bass plays the 'boom' (root on 1, fifth on 3) as the kick of the band — root-five alternation driving the pulse",
 "fiddle_lead_break": "a bowed fiddle takes melodic breaks with bluesy double-stops and slides between the vocal verses",
 "high_lonesome_harmony": "tight, high, often modal-tinged tenor/baritone vocal harmony stacked above the melody — the 'high lonesome' sound (Bill Monroe)",
 "bluegrass_breakdown_drive": "an up-tempo instrumental 'breakdown' where soloists trade fast breaks over the relentless boom-chuck + banjo roll",
 # --- fado ---
 "guitarra_tremolo": "the guitarra portuguesa (12-string, teardrop): bright cascading tremolo and turn ornaments answering the voice in the gaps — the sound of fado",
 "saudade_rubato": "the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom",
 "fado_menor_cadence": "the fado-menor minor mood: a i - V(7) harmonic-minor pull with the raised leading tone, resolving with a heavy final V-i 'full stop'",
 "viola_strum": "the viola (classical guitar) lays a steady fingered strum + bass line under the guitarra's filigree — the harmonic and rhythmic anchor",
 "percussionless_intimacy": "NO drums: the pulse lives entirely in the strummed viola and the singer's phrasing; arrangement is voice + two guitars, intimate and dynamic",
 # --- kwaito ---
 "slowed_house_bounce": "house slowed to ~100-110 BPM: four-on-the-floor kick with a lazy, swung, half-speed-feeling bounce — the space and the slow-motion groove are the point",
 "kwaito_deep_bassline": "a deep, simple, repeating synth/DX bassline (M1/DX7 era) locked to the kick — round sub, minimal notes, the low-end hook",
 "m1_organ_stab": "the Korg M1 'organ'/'piano' house stab: a bright plucky chord stab on the offbeats — the melodic signature of kwaito and its house lineage",
 "chanted_township_vocal": "laid-back, repetitive chanted/spoken vocals in township slang, call-and-response, riding the pocket rather than singing over it",
 "loose_swing_hats": "offbeat hats with a loose human swing (not quantized) giving the slow groove its lilt and shuffle",
 # --- future funk ---
 "sample_chop_stab": "chop a 70s/80s city-pop or disco record into short pitched STABS and re-sequence them into a new syncopated hook — the sampled chops are the melody",
 "sidechain_pump_ff": "heavy sidechain compression ducking everything to the four-on-the-floor kick so the whole mix breathes/pumps on each beat — the French-house 'whomp'",
 "french_filter_sweep": "an automated resonant band/low-pass filter opens across 8-16 bars into the drop (Daft-Punk 'filter house') — the build IS a filter sweep on the sampled loop",
 "disco_string_stab": "lush unison disco-string and brass stabs punctuate the groove; four-on-the-floor kick, offbeat open hats, claps on 2 & 4",
 "citypop_maj7_color": "bright maj7 / m9 city-pop harmony kept in the chops — sunny, nostalgic, slightly wistful chord color",
 # --- rage ---
 "gliding_808": "a distorted, portamento-GLIDING 808 that slides between notes as the bassline AND the melody — overdriven so it fuzzes, the defining rage low end",
 "detuned_rage_lead": "a heavily detuned super-saw / bell / brass synth stab (slightly out-of-tune on purpose), often layered and pitched high — the aggressive, queasy rage topline",
 "triplet_hat_roll": "trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM",
 "distorted_drum_bus": "the whole drum + 808 bus pushed into overdrive/soft-clip so it distorts and glues into one aggressive, saturated wall (opium/Carti aesthetic)",
 "minimal_vamp_energy": "harmony is a single static minor/Phrygian vamp; the song is ENERGY and texture (screamed ad-libs, distortion, space) not chord movement",
 # --- post-rock ---
 "postrock_crescendo": "a multi-minute build from one sparse clean tremolo/arpeggio to an overwhelming distorted climax — AUTOMATE it (late-bloom curve, layers entering), never jump-cut it",
 "delay_repeat_groove": "the 'groove' is a delay-drenched clean-guitar arpeggio whose synced echoes weave a shimmering ostinato — the repeats form the rhythmic bed",
 "postrock_quiet_loud": "the Mogwai/EITS grammar: a restrained clean valley ERUPTS into a full distorted wall, then recedes — the dynamic swing is the hook",
 "ebow_swell": "sustained EBow / volume-swell guitar lines with no pick attack, blooming in like strings over the arpeggios",
 "major_lift_climax": "the climax resolves an Aeolian-minor build onto a bright IV or bVI/major-lift chord for the cathartic, hopeful peak",
 "layered_guitar_wash": "multiple reverbed/delayed clean guitars stacked at octaves feeding a shared reverb bus into a wide, weightless wash",
 # --- bollywood filmi ---
 "keherwa_theka": "the 8-beat Keherwa taal on dholak/tabla: Bhari (full, weighted) across beats 1-4 and the KHALI (empty, marked) on beat 5 — the default filmi dance groove with its rolling bounce",
 "playback_vocal_stack": "big, up-front lead 'playback' vocals (often doubled/harmonized male+female) are the star — everything is arranged to frame the sung melody",
 "bansuri_raga_lead": "a bamboo bansuri flute (or sitar) carries a raga-flavored melodic hook — Bhairavi / harmonic-minor color and gamak ornament over the groove",
 "filmi_orchestral_hybrid": "lush strings + brass + tabla/dholak fused with modern 808s, four-on-the-floor or trap layers — cinematic maximalism, genres stacked in one song",
 "tanpura_tonic_drone": "a sustained tanpura/tambura tonic-fifth drone underpins the tonality, grounding the modal/raga melody",
}

# ---- the 15 genres (bpm/key/mix from research + adversarial corrections folded in) ----
G = [
 dict(name="gamelan", bpm=(60,200), key="D pentatonic (slendro approx.)", form="through_composed",
   voicing={"style":"inharmonic_bronze","lo":45,"hi":96}, parents=[], derived=[],
   tech=["kotekan_interlock","colotomic_cycle","ombak_detune","slendro_pelog_tuning","irama_density_shift","kendang_cue"],
   pattern=("colotomic_kotekan","Cyclic colotomic gamelan (felt 4/4, 16-beat gongan, 0 swing): the low gong marks the CYCLE END (last slot), a mid gong quarters it; over it two metallophone parts INTERLOCK (polos + sangsih) into one fast cascade twice their individual speed; core-melody tones ring underneath. No chord changes, no backbeat pocket — momentum from repetition + ombak shimmer. [encode 16/32-beat cycles + slendro/pelog via microtuning; the grid approximates.]",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,8],"hat":[2,6,10,14],"ride":[15],
      "vel":{"ride":{"15":1.0},"hat":{"2":0.5,"6":0.5,"10":0.5,"14":0.5}},"chords":[[0,1]],
      "lead":{"voice":"gamelan_saron","octave":5,"steps":[[0,1,1],[1,3,1],[2,5,1],[3,3,1],[4,1,1],[5,3,1],[6,5,1],[7,3,1],[8,1,1],[9,3,1],[10,5,1],[11,3,1],[12,1,1],[13,3,1],[14,5,1],[15,3,1]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":11.0},
   sounds=[("gamelan_metallophone","gamelan_saron","faust gamelan_saron: REAL inharmonic struck bronze — stretched partials 1:2.76:5.40:8.93 with the OMBAK pair BUILT IN (knobs: ombak Hz 5-9, ring, shimmer, strike). Sharp attack, long ring. Do NOT compress — the amplitude beating IS the sound. vibraphone/marimba remain as softer companions."),
           ("gamelan_gong","gamelan_gong","faust gamelan_gong: the gong ageng at each cycle END — deep slowly-beating sub fundamental + soft inharmonic partials + the downward strike pitch-glide, very long tail (knobs: tail s, ombak Hz, glide, boom)")]),

 dict(name="balkan_brass", bpm=(90,210), key="D Phrygian dominant (Hijaz)", form="song",
   voicing={"style":"overblown_brass","lo":36,"hi":82}, parents=[], derived=[],
   tech=["aksak_meter","hijaz_run","oom_pah_engine","davul_boom","brass_tutti_answer","accelerando_drive"],
   pattern=("aksak_oompah","Balkan brass (aksak 9/8 as 2+2+2+3 approximated on a driving 4/4 read, ~140 BPM): tuba 'oom' on each cell downbeat, horns chug offbeat 'pah', davul booms the cell heads + snare cracks, a virtuoso trumpet tears a Hijaz (Phrygian-dominant) run on top; band answers each phrase with a tutti stab; the whole thing accelerates. [encode true 9/8 via section time-sig / tempoMap; add an accelerando ramp for the climax.]",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"8":1.0},"snare":{"4":0.9,"12":0.9}},"chords":[[0,1]],
      "lead":{"voice":"brass_stab","octave":4,"steps":[[0,1,1],[1,2,1],[2,3,1],[4,5,1],[6,4,1],[8,3,1],[10,2,1],[12,1,2]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-7,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("overblown_brass","brass_stab","bright brash overblown brass: brass_stab/cine_brass/sax_section detuned-stacked for the ensemble mass, driven with fx_saturate (more drive = more overblown upper partials), bandpass ~1.2 kHz brass formant + 2-4 kHz air; the reedy lead can use `zurna`. Tuba = bass_warm octave-down staccato. Finish with tape saturation + light room."),
           ("davul","hardkick","davul boom = a pitched sine 55-90 Hz with a fast pitch-drop (hardkick/timpani) + a noise-burst switch tick (hat)")]),

 dict(name="bhangra", bpm=(90,165), key="G major (club: minor)", form="song",
   voicing={"style":"folk_hook","lo":41,"hi":81}, parents=[], derived=[],
   tech=["chaal_rhythm","dhol_dagga_tilli","tumbi_riff","boliyan_call_response","four_on_floor_club_layer"],
   pattern=("dhol_chaal","The dhol CHAAL (4/4, ~100 BPM straight): bass 'dagga' on the downbeat + a push (slots 0,3,8,11), bright 'tilli' treble ticking the eighths, a piercing tumbi ostinato riff on top; modern club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol for dancefloor weight; boliyan call-response vocals.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,3,8,11],"snare":[2,6,10,14],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"kick":{"0":1.0,"8":1.0,"3":0.7,"11":0.7},"snare":{"2":0.6,"6":0.6,"10":0.6,"14":0.6}},"chords":[[0,1]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[2,1,1],[4,5,1],[6,5,1],[8,1,1],[10,1,1],[12,3,1],[14,2,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"lowmid>low>mid","clipped":0},
   sounds=[("dhol","dhol","faust dhol: THE dagga (bass head) — deep booming membrane with the STRONG strike pitch-drop (knobs: decay, bend, slap). Pair it with a tight snare/hat tick as the 'tilli' treble head so the chaal reads as two hands."),
           ("tumbi","pluck","tumbi = a single bright high plucked string (pluck) as a fast repeating ostinato — the instant-bhangra hook; dholak/tabla for the acoustic bed")]),

 dict(name="bollywood_filmi", bpm=(70,140), key="C harmonic minor (Bhairavi)", form="song",
   voicing={"style":"orchestral_hybrid","lo":33,"hi":88}, parents=[], derived=["bhangra"],
   tech=["keherwa_theka","playback_vocal_stack","bansuri_raga_lead","filmi_orchestral_hybrid","tanpura_tonic_drone"],
   pattern=("keherwa_filmi","Modern filmi (Keherwa 8-beat, ~100 BPM): dholak/tabla lay the theka — weighted Bhari across beats 1-4, KHALI marked on beat 5 — with a rolling bounce; a bansuri/sitar raga hook (Bhairavi/harmonic-minor) over lush strings + brass, a tanpura tonic drone grounding it, and a modern 808 / four-on-the-floor dance layer under big doubled playback vocals. Max BPM ~140 for dance numbers.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,6,8,12],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"kick":{"0":1.0,"8":0.8}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"flute_lead","octave":5,"steps":[[0,1,1],[2,2,1],[4,3,1],[6,4,1],[8,5,1],[10,6,1],[12,5,1],[14,1,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("filmi_bed","flute_lead","bansuri = flute_lead (raga hook + gamak); cine_brass + strings_disco/strings_stacc for the orchestral maximalism; tanpura_drone under everything; dholak/tabla (kick_punch/timpani + tight snare) for Keherwa; kick_808 for the modern layer."),
           ("playback_vox","formant_vox","big doubled/harmonized lead vocals up front (formant_vox/vox_pad as synth stand-in; real vocal via tune_vocal) — the song frames the sung melody")]),

 dict(name="ethio_jazz", bpm=(75,130), key="C major (tizita pentatonic)", form="song",
   voicing={"style":"modal_vibraphone","lo":33,"hi":84}, parents=["jazz"], derived=[],
   tech=["tizita_mode","ethio_pentatonic_qenet","compound_latin_swing","vibraphone_lead_ethio","modal_ostinato_vamp","kebero_crossrhythm"],
   pattern=("tizita_vamp","Ethio-jazz (~95 BPM, swung ~60%, 12/8 feel over 4/4): a short modal bass + horn OSTINATO held under long solos; vibraphone (motor on) states the tizita-pentatonic head, Wurlitzer/organ doubling; swung ride over an even kick-snare while congas + kebero lay a 6-against-4 cross-pulse. Languid, hypnotic, minimal chord motion.",
     {"bars":1,"swing":0.6,"bass_style":"walking","kick":[0,8],"snare":[4,12],"ride":[0,4,6,8,12,14],"hat":[4,12],
      "vel":{"ride":{"0":1.0,"6":0.8,"14":0.8}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"vibraphone","octave":4,"steps":[[0,1,2],[2,2,1],[4,3,2],[8,5,2],[12,6,2]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0},
   sounds=[("ethio_combo","vibraphone","vibraphone (motor tremolo) lead + rhodes/organ_soul (Wurli) doubling the tizita head; bass_warm walking ostinato; congas + kebero (perc/timpani) for the 6/8 cross-rhythm; sax_section for horn lines. Warm, dynamic, tape saturation not brickwall.")]),

 dict(name="kwaito", bpm=(95,112), key="A minor", form="club",
   voicing={"style":"deep_slow_house","lo":33,"hi":72}, parents=["house"], derived=[],
   tech=["slowed_house_bounce","kwaito_deep_bassline","m1_organ_stab","chanted_township_vocal","loose_swing_hats"],
   pattern=("kwaito_bounce","Kwaito (~105 BPM, slowed-house bounce, swing ~55%): four-on-the-floor kick with a lazy half-speed feel, clap/snare on 2 & 4, loosely-swung offbeat hats; a deep simple synth bassline locked to the kick; a bright M1-organ chord stab on the offbeats; laid-back chanted township vocals riding the pocket. Space and slow-motion groove are the point.",
     {"bars":1,"swing":0.55,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"4":0.9,"8":1.0,"12":0.9}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"organ_soul","octave":4,"steps":[[2,1,1],[6,1,1],[10,4,1],[14,5,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("kwaito_kit","organ_soul","M1-organ/piano stab = organ_soul/hammond_organ on the offbeats; deep round bassline = sub_clean/bass_warm (DX7 character) locked to the kick; clap_909 + kick_808/kick_punch for the slowed-house kit; loose swing (not quantized).")]),

 dict(name="soukous", bpm=(110,145), key="C major", form="song",
   voicing={"style":"interlocking_guitar","lo":40,"hi":88}, parents=[], derived=[],
   tech=["sebene_section","cavacha_churn","interlocking_guitars","atalaku_animation","static_major_harmony"],
   pattern=("sebene","Soukous SEBENE (~128 BPM, 4/4, light triplet-vs-16th lilt ~54%): the cavacha churn (ghosted-16th snare/hat + backbeat 2&4 + near-every-beat kick) drives three interlocking guitars in different registers cycling a bright major riff; static I-IV-V or one-chord vamp; atalaku shouts punctuate. Euphoric, fast, guitar-led.",
     {"bars":1,"swing":0.54,"bass_style":"roots","kick":[0,2,4,6,8,10,12,14],"snare":[4,12],"hat":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
      "vel":{"snare":{"4":0.9,"12":0.9},"hat":{"1":0.4,"3":0.4,"5":0.4,"7":0.4,"9":0.4,"11":0.4,"13":0.4,"15":0.4}},"chords":[[0,1],[1,4],[2,5],[3,1]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[1,3,1],[2,5,1],[3,1,1],[4,5,1],[5,3,1],[6,1,1],[8,3,1],[9,5,1],[10,1,1],[12,5,1],[13,3,1],[14,1,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("soukous_guitars","pluck","three CLEAN interlocking guitars: bright lead (pluck octave 5), mid mi-solo (pluck2), rhythm (pluck octave 4) — light fx_delay + small reverb, NO fuzz; bass_warm; cavacha kit (snare/hat churn). The interlock is the harmony.")]),

 dict(name="bluegrass", bpm=(80,180), key="G major", form="song",
   voicing={"style":"string_band","lo":40,"hi":88}, parents=["country"], derived=[],
   tech=["scruggs_roll","mandolin_chop","boom_chuck_bass","fiddle_lead_break","high_lonesome_harmony","bluegrass_breakdown_drive"],
   pattern=("boom_chuck_roll","Bluegrass 'drive' (~140 BPM, 4/4, near-straight ~52%): a DRUMLESS string-band kit — upright bass = the boom (root on 1, fifth on 3), mandolin CHOP = the snare (damped chord on 2 & 4), banjo Scruggs rolls = the continuous 8th-note hi-hat sparkle; fiddle and banjo trade fast breaks; high-lonesome tenor harmony above.",
     {"bars":1,"swing":0.52,"bass_style":"walking","kick":[0,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"4":0.85,"12":0.85}},"chords":[[0,1],[2,5]],
      "lead":{"voice":"pluck","octave":4,"steps":[[0,1,1],[1,3,1],[2,5,1],[3,1,1],[4,3,1],[5,5,1],[6,1,1],[7,3,1],[8,5,1],[9,1,1],[10,3,1],[11,5,1],[12,1,1],[13,3,1],[14,5,1],[15,1,1]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":11.0},
   sounds=[("string_band","pluck","banjo = bright pluck rolling continuous 8ths; mandolin chop = pluck2 damped on 2&4; upright_bass boom-chuck (root-five walking); fiddle breaks = faust `fiddle` (bowed saw + violin body formants, delayed vibrato — knobs bow/vibrato/vibrate/bright; double-stop by playing two notes); acoustic, dynamic, mid-forward — do NOT brickwall (keep the crest).")]),

 dict(name="fado", bpm=(60,140), key="A minor (fado menor)", form="song",
   voicing={"style":"guitarra_voice","lo":40,"hi":84}, parents=[], derived=[],
   tech=["guitarra_tremolo","saudade_rubato","fado_menor_cadence","viola_strum","percussionless_intimacy"],
   pattern=("fado_menor","Fado (percussionless, ~88 BPM but RUBATO): voice + two guitars only. Viola (classical guitar) lays a steady fingered strum + bass line; the guitarra portuguesa (12-string) answers with bright cascading tremolo filigree in the vocal gaps; harmonic-minor i - V(7) - i with a heavy final full-stop cadence. The voice pulls and pushes the tempo (saudade). Intimate, dynamic, no drums.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","chords":[[0,1],[2,5]],
      "lead":{"voice":"pluck2","octave":4,"steps":[[0,1,2],[4,7,1],[6,1,1],[8,5,2],[12,1,2]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-13,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":9.0},
   sounds=[("fado_guitars","pluck2","guitarra portuguesa = pluck2 (bright 12-string tremolo cascades) answering the voice; viola = pluck (fingered strum + bassline); viola baixo / upright_bass for the low. NO percussion. A short intimate room reverb; keep it very dynamic (high crest). Real vocal via tune_vocal with rubato preserved.")]),

 dict(name="neo_soul", bpm=(60,100), key="D minor (Dorian)", form="song",
   voicing={"style":"lush_extended","lo":33,"hi":84}, parents=["soul","rnb"], derived=["hiphop"],
   tech=["dilla_drunk_swing","extended_jazz_chords","behind_beat_bass","rhodes_comp_neo","unquantized_live_kit","chromatic_mediant_move"],
   pattern=("dilla_pocket","Neo-soul (~85 BPM, half-time, Dilla 'drunk' pocket): backbeat on 3 but the snare is dragged ~20-50 ms LATE and the hats push/pull OFF the grid so the beat lurches; a foam-muted bass sits BEHIND the kick; Fender Rhodes comps lush m9/m11/maj9 (Dorian) chords with chorus. Never quantize — the wobble IS the feel.",
     {"bars":1,"swing":0.56,"bass_style":"sustained","kick":[0,6,10],"snare":[8],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"8":1.0},"hat":{"0":0.5,"2":0.35,"4":0.5,"6":0.35,"8":0.5,"10":0.35,"12":0.5,"14":0.35}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"rhodes","octave":4,"steps":[[0,1,3],[6,4,2],[10,5,3]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("neo_soul_bed","rhodes","Fender Rhodes (light chorus/phaser) comping extended chords + jazz_piano fills; foam-muted P-bass = bass_warm sitting late; loose live/MPC kit with velocity spread (dark fat snare, ghosted hats); keep it warm, round, bass-forward and un-brickwalled (DR-preserving master).")]),

 dict(name="djent", bpm=(90,180), key="E minor (Phrygian)", form="song",
   voicing={"style":"polymetric_chug","lo":33,"hi":76}, parents=["metal"], derived=[],
   tech=["polymetric_chug","extended_range_chug","kick_follows_riff","djent_thall","ambient_clean_bloom","poly_over_common"],
   pattern=("poly_chug","Djent (~120 BPM, 4/4 with a phasing odd-length riff cell): machine-tight straight-16th palm-muted chugs on the lowest string of a 7/8-string (drop tuning), gated silent between hits; the KICK doubles every chug exactly; snare pinned to 2 & 4; a 5/16 or 7/16 riff cell cycles over the 4/4 so accents phase and re-sync on a big downbeat every few bars. Lush reverbed clean bloom in the interludes.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,3,4,6,8,11,12,14],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"4":1.0,"12":1.0}},"chords":[[0,1]],
      "lead":{"voice":"highgain_guitar","octave":2,"steps":[[0,1,1],[3,1,1],[4,1,1],[6,2,1],[8,1,1],[11,1,1],[12,1,1],[14,2,1]]}}),
   mix={"lufs_lo":-9,"lufs_hi":-6,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("djent_guitar","highgain_guitar","highgain_guitar (tight, gated, HP ~90 Hz, mids KEPT for the chug to read), hard L/R double-track; sub_clean doubling the low chug for weight; clean interludes = clean_chime_guitar into a big reverb bus; a punchy triggered kick (hardkick/kick_punch) glued to the riff. Tight, loud, gated low end.")]),

 dict(name="post_rock", bpm=(60,140), key="E minor", form="through_composed",
   voicing={"style":"crescendo_wash","lo":33,"hi":84}, parents=["rock"], derived=[],
   tech=["postrock_crescendo","delay_repeat_groove","postrock_quiet_loud","ebow_swell","major_lift_climax","layered_guitar_wash"],
   pattern=("crescendo_arp","Post-rock (~110 BPM, 4/4 + odd meters): a delay-drenched clean-guitar arpeggio whose synced echoes weave the ostinato; drums sparse-to-huge; the piece BUILDS vertically over minutes — start with one clean tremolo + brushed ride, each cycle adds a layer (2nd guitar -> EBow swell -> distortion engages -> bass sub -> crash wall) so the same motif detonates as a distorted climax that resolves onto a bright major-lift chord. AUTOMATE the crescendo (late-bloom curve).",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,8],"snare":[8],"ride":[0,2,4,6,8,10,12,14],
      "chords":[[0,1],[2,6],[3,4]],
      "lead":{"voice":"clean_chime_guitar","octave":4,"steps":[[0,1,2],[2,5,2],[4,3,2],[6,5,2],[8,1,2],[10,5,2],[12,3,2],[14,5,2]]}}),
   mix={"lufs_lo":-15,"lufs_hi":-11,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("postrock_wash","clean_chime_guitar","layered clean_chime_guitar arpeggios (dotted/triplet fx_delay -> shimmer fx_reverb bus) for the wash; guitar_grit engages ONLY at the climax; EBow swells = pad_motion/vox_pad; drone bass. THE CRESCENDO IS AUTOMATION — fx_trim gain + fx_saturate drive + reverb-send + layer mute-ins over 60-120 s with a LATE-BLOOM curve (>0). Do NOT brickwall (preserve the arc).")]),

 dict(name="berlin_school", bpm=(70,132), key="A minor", form="through_composed",
   voicing={"style":"analog_sequence","lo":33,"hi":84}, parents=[], derived=[],
   tech=["analog_sequence_16th","delay_fill_sequence","evolving_texture","sequencer_pedal_drone","mellotron_pad_wash","drumless_pulse"],
   pattern=("moog_sequence","Berlin school (~110 BPM, 4/4, often DRUMLESS): a locked 16th-note analog sequence is the whole engine — an 8-16 step pitched pattern (Aeolian, over a tonic pedal drone) looped for minutes, programmed note-then-rest so a synced delay fills the gaps; a Mellotron pad washes slow swells above; the 'composition' is a filter cutoff opening + layers fading over time, NOT verse/chorus. When drums enter they are a simple slow kick.",
     {"bars":1,"swing":0.5,"bass_style":"roots","hat":[0,2,4,6,8,10,12,14],"kick":[0,8],
      "vel":{"kick":{"0":0.6,"8":0.6}},"chords":[[0,1]],
      "lead":{"voice":"phase_distortion","octave":3,"steps":[[0,1,1],[1,5,1],[2,1,1],[3,5,1],[4,3,1],[5,5,1],[6,1,1],[7,5,1],[8,1,1],[9,5,1],[10,7,1],[11,5,1],[12,4,1],[13,5,1],[14,1,1],[15,5,1]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("berlin_sequence","phase_distortion","a locked 16th analog sequence (phase_distortion/supersaw/pluck2) through a tape-echo fx_delay (note-then-rest so echoes fill); pad_motion = the Mellotron wash; a held tonic drone; a SLOW automated fx_filter LP sweep = 'the evolution'; drums dead-simple or absent. Optional slow tempoMap drift.")]),

 dict(name="future_funk", bpm=(110,128), key="D minor (maj7 color)", form="club",
   voicing={"style":"filtered_chops","lo":36,"hi":88}, parents=["french_house"], derived=["citypop","disco"],
   tech=["sample_chop_stab","sidechain_pump_ff","french_filter_sweep","disco_string_stab","citypop_maj7_color"],
   pattern=("chop_pump","Future funk (~120 BPM, 4/4, heavy sidechain): four-on-the-floor kick with the WHOLE mix pumping/ducking to it; claps on 2 & 4, offbeat open hats; chopped 70s/80s city-pop stabs re-sequenced as the syncopated hook (bright maj7/m9 color); an automated resonant filter opens across 8-16 bars into the drop; disco-string + supersaw stabs punctuate.",
     {"bars":1,"swing":0.52,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"4":1.0,"8":1.0,"12":1.0},"hat":{"2":0.7,"6":0.7,"10":0.7,"14":0.7}},"chords":[[0,1],[1,4],[2,6],[3,5]],
      "lead":{"voice":"supersaw","octave":4,"steps":[[0,1,1],[2,3,1],[4,5,1],[6,4,1],[8,1,1],[10,6,1],[12,5,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"mid>low>lowmid","clipped":0},
   sounds=[("ff_chops","supersaw","chopped city-pop sample stabs (use supersaw/strings_disco + pluck as synth stand-ins, or sample-chop a source) with heavy fx_pump sidechain to the kick; bass_warm French-house bass; strings_disco stabs; fx_djfilter/fx_filter sweep opening into the drop. Bright, glossy, pumping.")]),

 dict(name="rage", bpm=(130,170), key="F minor (Phrygian)", form="song",
   voicing={"style":"distorted_808","lo":28,"hi":84}, parents=["trap"], derived=[],
   tech=["gliding_808","detuned_rage_lead","triplet_hat_roll","distorted_drum_bus","minimal_vamp_energy"],
   pattern=("rage_grid","Rage / opium (~145 BPM sweet-spot — 155 runs hot; 4/4, triplet hats): a distorted, portamento-GLIDING 808 is bass AND melody, sliding between notes overdriven so it fuzzes; snare/clap on beat 3 (half-time feel); triplet hat rolls and stutters; a heavily DETUNED super-saw/bell stab screams high; single static minor/Phrygian vamp; the whole drum+808 bus soft-clipped into one aggressive wall.",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,7,10],"snare":[8],"hat":[0,2,3,4,6,8,10,11,12,14],
      "vel":{"snare":{"8":1.0},"hat":{"3":0.5,"11":0.5}},"chords":[[0,1]],
      "lead":{"voice":"supersaw_fat","octave":4,"steps":[[0,1,2],[4,1,1],[8,6,1],[10,5,1],[12,1,2]]}}),
   mix={"lufs_lo":-8,"lufs_hi":-5,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("rage_808","supersaw_fat","gliding distorted 808 = sub_clean/kick_808 with portamento + HEAVY fx_saturate/fx_softclip; detuned lead = supersaw_fat/reese/fmbell pitched high, layered and slightly out of tune ON PURPOSE; hardkick + triplet hats; push the drum bus into fx_softclip for the wall. Loud and aggressive but keep clipped_samples=0 (soft-clip, don't hard-clip).")]),
]

# ---- reuse the existing jazz_swing Groove for ethio_jazz (feel profile in library/grooves.json) ----
JAZZ_SWING_GENRES = ["ethio_jazz"]


def seed():
    kg = KG()
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, PROV, desc=d)
    # genres first (so intra-set DERIVED_FROM targets like bhangra exist), then edges
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
    for gname in JAZZ_SWING_GENRES:
        kg.link("Genre", gname, "HAS_GROOVE", "Groove", "jazz_swing")

    n_gen = kg.q("MATCH (g:Genre) RETURN count(g)")[0][0]
    n_tech = kg.q("MATCH (t:Technique) RETURN count(t)")[0][0]
    print(f"seeded {len(G)} genres (+{len(NEW_TECH)} techniques). graph now: "
          f"{n_gen} genres, {n_tech} techniques.")
    for g in G:
        v = kg.genre_view(g["name"])
        print(f"  {g['name']:16s} parents={v['parents']} tech={len(v['techniques'])} "
              f"inherited={len(v['inherited_techniques'])} mix={bool(v['mixtargets'])} "
              f"grooves={[gr['name'] for gr in v['grooves']]}")


if __name__ == "__main__":
    seed()
