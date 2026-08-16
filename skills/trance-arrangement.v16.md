---
name: trance-arrangement
version: 16
kind: genre
tags: [trance, techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 136-142; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
  - SUPERSAW UPLIFT is non-negotiable: trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - VST FACTORY PRESETS is non-negotiable: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - GROOVE PSY STRAIGHT is non-negotiable: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - SYNTH PARAM MAPS is non-negotiable: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
  - LONG FORM PATIENCE is non-negotiable: tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late
  - FILTER JOURNEY LAYERS is non-negotiable: motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# Trance arrangement (graph-compiled)

Trance is a child of **techno** — its groove laws apply unless overridden below.

## The pocket — trance_lift
4-floor + rolling offbeat bass, supersaw pads swell 8-16 bar arcs into breakdown-rebuild  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **vst fx presets** (wNone): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **supersaw uplift** (w1.0): trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout *(curated:claude/2026-07-03)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **vst factory presets** (w0.95): factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility *(verified:one-call-apply/2026-07-04 (phrasing lesson FALSIFIED: 0.857->0.857 w/ 0 usage; refined to tool-side friction fix — TAL 87-param + Surge blob applied+rendered via single calls))*
- **four on floor** (w0.93): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **groove psy straight** (w0.9): apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **synth param maps** (w0.9): presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion *(verified:synth-maps/2026-07-04 (Odin Filter1 Frequency 400 dropped a factory lead 5121→786Hz centroid; ranges from Odin source registration))*
- **long form patience** (w0.9): tension accumulates in MINUTES, not bars: 12-32-bar sections, one journey over 300+ bars; the peak earns itself by arriving late *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **filter journey layers** (w0.9): motion at three timescales AT ONCE: per-note filter env inside a per-section cutoff ceiling inside a master LP walk — sweeps riding sweeps is the hypnosis *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **pump sidechain** (w0.86): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- also in this genre's DNA (lower weight): one change per section, glue comp grip, bass hp discipline, singer songwriter schema, bass swap, one root lattice, filter build, filter transition, sidechain unmask bass, mono check law, loudness recovery, curve shaped automation, tonal ambiguity dual tonic, mid side width control, tension and release, section contrast, energy contour, strategic pause, tempo map motion, sentence phrase, pedal point, cadence modal VII i, riser into drop, impact downbeat, seam connects law, downlifter drain, symbolic unmask, haas caution

## Inherited from techno
- rumble kick: kick tail feeds a send reverb lowpassed into a rolling rumble
- modular stab: single dark stab/chord repeated with filter automation variation
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- complementary eq unmask: two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK]
- acapella bridge: the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) over the incoming deck and fades by bar 8; find the phrase by probing the final ~24 played bars for the loudest-voiced 8-bar window — a DJ cuts where the VOICE ends, not where the file does [battery: solo render -26dB voice exactly across the swap; voiceless tails fall back honestly]
- chance operations: probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive
- mono below 120: keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law]
- mono sub stereo body: the techno bass trick: split the bass — a MONO sub (sine, dead center, <120Hz) carries the weight; a STEREO body (harmonics, saturated, widened above ~150Hz) carries the character. Club-safe AND wide [Weapon/NI law]
- ...and from the techno skill itself: true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **choir ah pad**: faust vox_pad: designed choir-ah (saws through 700/1050 formants, slow bloom) — gospel swells, trance pads, cinematic beds; the sampled choir kit is the REAL thing, this is the designed color to layer with it
- **odin modular lead**: Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette
- **pluck zones**: pluck knobs: decay 0.05-2s (squared env - snappy), color 1-12 (pitch-tracking LP multiple: 2 = dark koto, 10 = open). Dance plucks = color 6-8 decay 0.3; automate color rising into a drop.
- **pad motion zones**: pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth 0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = motion 0.6 + drift 0.3; automate depth for evolving intros.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
