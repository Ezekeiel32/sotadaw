---
name: hardstyle-arrangement
version: 5
kind: genre
tags: [hardstyle, trance, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -11..-6, band order low>lowmid>mid.
  - HARDSTYLE KICK is non-negotiable: distorted kick with tonal tail (kick_psy punch 18+ through fx_saturate drive 12; tail pitched to key)
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - RISER THROWS is non-negotiable: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)
---
# Hardstyle arrangement (graph-compiled)

Hardstyle is a child of **trance** — its groove laws apply unless overridden below.

## The pocket — hard_pocket
kick IS the bass (tonal tail); offbeat screech leads; halftime breakdowns  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **hardstyle kick** (w1.0): distorted kick with tonal tail (kick_psy punch 18+ through fx_saturate drive 12; tail pitched to key) *(curated:claude/2026-07-03)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **riser throws** (w0.93): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **supersaw uplift** (w0.86): trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout *(curated:claude/2026-07-03)*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **gain staged saturation** (w0.79): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Inherited from trance
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- groove psy straight: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow
- curve shaped automation: automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat.
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- vst fx presets: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
- synth param maps: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
- sentence phrase: the 2+2+4 sentence: presentation (idea x2) then continuation/drive to cadence — THE build shape; EDM risers are sentences in disguise [Form: phrase models]
- pedal point: static bass under moving harmony — tension by refusal; the dominant pedal is the classic pre-drop device [Diatonic harmony: pedal/prolongation]
- long form patience: tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late
- one change per section: every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart
- filter journey layers: motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis
- one root lattice: every voice octave-locked to ONE fundamental (x1 bass, x2 acid, x4 pad, x8 lead) — the spectrum fuses into a single instrument; voicings that wander break the lattice
- glue comp grip: a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage
- bass hp discipline: HP-filter EVERYTHING that is not kick or bass — the 40-80Hz lane belongs to the bassline fundamentals alone; clash-free low end is arrangement + EQ discipline, not limiting
- cadence modal VII i: the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)
- singer songwriter schema: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
- tonal ambiguity dual tonic: the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas]
- sidechain unmask bass: sustained bass masks a percussive kick because the ear locks onto the constant voice — duck the bass only when the kick hits and both survive; the FX-side complement to rolling_offbeat_bass (where the ARRANGEMENT is the sidechain: bass written in the kick's holes needs no ducking) [MASK]
- mono check law: AUDITION IN MONO with and without your width moves: side-channel content disappears completely in the fold, and aggressive M/S EQ (the classic +8dB-lows-on-sides) can make a track barely audible summed — if the mix collapses, the width was borrowed, not earned [the fold test]
- mid side width control: width is DYNAMIC, not a static knob: compressing/boosting the MID makes loud center sounds read wider by contrast; side-only processing adds air that vanishes in mono (acceptable IF it only sweetens the stereo image) — treat mid and side as two mixes [mid/side processing]
- haas caution: the Haas trick (10-40ms delay on one side = instant width) is a MONO TRAP: the delay comb-filters on the fold. Use it on throwaway ear-candy, NEVER the bass, kick, or lead — and always fold-check [width without phase, the caveat]
- riser into drop: the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop
- impact downbeat: a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note
- seam connects law: sections must CONNECT, not just abut: after each part breathes per-section (density), the boundary INTO a lift wants a build (riser/fill/filter-open) and the arrival wants a mark (impact/crash) — the glue is what separates an arrangement from a playlist of loops
- downlifter drain: the drop-out drain: close a lowpass filter on the outgoing lead/pad over the last 1-2 bars into a break/outro (cutoff 18k->~420Hz, early-jump curve) — energy LEAVES so the break lands as relief; the automation complement to the riser (no dedicated FX needed)
- symbolic unmask: find frequency collisions WITHOUT rendering: two sustained melodic tracks whose note pitch-RANGES overlap share a register (the range IS the band profile) -> complementary EQ at the overlap center (focal +1.5, accompaniment -3.5, mud zone 120-2000Hz only). The unmask ladder rung 1, applied symbolically
- tension and release: the core arrangement arc: build energy + anticipation (risers, filter opens, added layers, strategic PAUSE) then release it dramatically at the drop. A track without a tension curve is a loop. (composes with transitions risers/impacts + automation builds)
- section contrast: adjacent sections MUST differ to keep engagement — the chorus/drop stands out from the verse by altering melody, harmony, rhythm OR instrumentation; the bridge/break introduces new material. Sameness across sections = the doctor A2 breathe failure.
- energy contour: shape dynamics across the song. THE KEY LAW: impact comes from CONTRAST, not pushing the limiter — if the build is already loud+full, the drop has nowhere to go. So make a drop hit harder by SOFTENING the section before it (intensify build -) AND hardening the drop (intensify drop +): louder hits + more 16th hats + more layers. Keep the sub OUT of the build so the drop bass lands. Density+velocity+layer-count are the energy dial.
- strategic pause: a beat of silence or a filter-swept gap right BEFORE the release amplifies its impact — the ear resolves the held breath. The downlifter + a 1-beat drum cut sells the drop.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
