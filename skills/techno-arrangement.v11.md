---
name: techno-arrangement
version: 11
kind: genre
tags: [techno, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-136; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
  - RUMBLE KICK is non-negotiable: kick tail feeds a send reverb lowpassed into a rolling rumble
  - GROOVE PSY STRAIGHT is non-negotiable: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# Techno arrangement (graph-compiled)

Techno is a child of **house** — its groove laws apply unless overridden below.

## The pocket — techno_grid
relentless kick, offbeat hats, one stab varied by automation, 16-bar arcs  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w1.0): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **gain staged saturation** (w0.95): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **rumble kick** (w0.92): kick tail feeds a send reverb lowpassed into a rolling rumble *(curated:claude/2026-07-02)*
- **groove psy straight** (w0.9): apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **one change per section** (w0.85): every 8-14 bars exactly ONE element enters or leaves — the ear tracks a single novelty; two changes at once read as a restart *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **glue comp grip** (w0.85): a MUSICAL bus compressor (~6dB grip, ~200ms release) BEFORE the brickwall makes the whole mix breathe with the kick — compliance chains measure right but don't GRIP; add the glue stage *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **mono below 120** (w0.85): keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **modular stab** (w0.84): single dark stab/chord repeated with filter automation variation *(curated:claude/2026-07-02)*
- **bass swap** (w0.8): ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **complementary eq unmask** (w0.8): two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **filter build** (w0.76): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **filter transition** (w0.75): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **mono check law** (w0.75): AUDITION IN MONO with and without your width moves: side-channel content disappears completely in the fold, and aggressive M/S EQ (the classic +8dB-lows-on-sides) can make a track barely audible summed — if the mix collapses, the width was borrowed, not earned [the fold test] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **curve shaped automation** (w0.7): automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat. *(skill:automation-motion@v2 (2026-07-03, engine-verified))*
- **acapella bridge** (w0.7): the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) over the incoming deck and fades by bar 8; find the phrase by probing the final ~24 played bars for the loudest-voiced 8-bar window — a DJ cuts where the VOICE ends, not where the file does [battery: solo render -26dB voice exactly across the swap; voiceless tails fall back honestly] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **mono sub stereo body** (w0.7): the techno bass trick: split the bass — a MONO sub (sine, dead center, <120Hz) carries the weight; a STEREO body (harmonics, saturated, widened above ~150Hz) carries the character. Club-safe AND wide [Weapon/NI law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **pump sidechain** (w0.68): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **tempo map motion** (w0.6): tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow *(skill:dj-blend@v2 (2026-07-03))*
- **pedal point** (w0.6): static bass under moving harmony — tension by refusal; the dominant pedal is the classic pre-drop device [Diatonic harmony: pedal/prolongation] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **chance operations** (w0.6): probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive *(engine-witnessed weighted follow actions (firing 49: trackNext w0.7 | globalPlayAgain w0.3 read back from te state) + WF13 Action Probability teardown via curated:claude/2026-07-05 (wave33 addendum))*

## Inherited from house
- offbeat bass: bass hits on the 8th between kicks
- groove ukg shuffle: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- sentence phrase: the 2+2+4 sentence: presentation (idea x2) then continuation/drive to cadence — THE build shape; EDM risers are sentences in disguise [Form: phrase models]
- cadence modal VII i: the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)
- andalusian descent: stepwise minor descent (i-VII-VI-...): the andalusian/lament lineage
- singer songwriter schema: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
- tonal ambiguity dual tonic: the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas]
- schema rotation: cyclical schemas keep their identity started ANYWHERE in the cycle (rotation) — one schema = four progressions; choose the rotation whose first chord is the section's mood anchor (IV-start = lift, vi-start = ache) [Popular music: four-chord schemas (variation laws)]
- unmask escalation ladder: unmask in escalating precision, stop at the first rung that works: 1) static complementary EQ; 2) wideband sidechain duck (whole voice, when trigger plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the trigger hits) — never pay more transparency than the collision costs [MASK]
- sidechain unmask bass: sustained bass masks a percussive kick because the ear locks onto the constant voice — duck the bass only when the kick hits and both survive; the FX-side complement to rolling_offbeat_bass (where the ARRANGEMENT is the sidechain: bass written in the kick's holes needs no ducking) [MASK]
- structure inheritance: a remix/companion inherits the SOURCE'S section skeleton: its sections become the arrangement form at their real durations — same bar count, same energy arc [battery: Foote on the RENDER, blind to the JSON, found 5/6 joints within 3 bars of the source's]
- auxiliary sections law: intros/outros/interludes/codas are AUXILIARY: they never count toward a form's identity (a strophic song with an intro is still AAA) — judge form by the MAIN-section pattern only; our labeler/arranger semantics follow this

## Sound recipes (this palette, these moves)
- **techno rumble**: kick_punch + send to verb bus (size 6+) with fx_filter cutoff 150 on the bus return
- **techno stab**: keys_dark single chord, fx_filter + automate cutoff per 4 bars, fx_delay dotted
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **psy kick tight**: kick_psy (zones punch/decay): psy/techno kick — punch 10-16 hard styles, decay 0.2-0.3 tight; ALWAYS dry
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **kick punch zones**: kick_punch now has knobs (source.params or automate): punch 0-1.5 (click level), drop 0-8 (pitch-env depth), decay 0.05-1.2s (body), tail 0-1, drive 0.2-4 (pre-tanh). Defaults = the classic sound. Longer decay 0.6-0.9 = room-shaking house kick; drive 2+ = distorted techno.
- **hat zones**: hat knobs: decay 0.01-0.6 (0.05 closed default; 0.25-0.4 = OPEN HAT — same voice, one knob), tone 4k-16k (bp centre), sizzle 0.5-8 (Q). Automate decay for open/closed patterns on ONE track.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
