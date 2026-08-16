---
name: dnb-arrangement
version: 7
kind: genre
tags: [dnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 170-176; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - BREAKBEAT CHOP is non-negotiable: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# Dnb arrangement (graph-compiled)

## The pocket — dnb_break
kick 0/2.5 snare 1/3; rides 16ths; sub separate from reese  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **breakbeat chop** (w1.0): kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar *(skill:dnb-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **reese bass** (w0.92): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **mono below 120** (w0.85): keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **ghost notes** (w0.84): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **loudness recovery** (w0.8): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **bass swap** (w0.8): ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **complementary eq unmask** (w0.8): two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **filter transition** (w0.75): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **structure inheritance** (w0.75): a remix/companion inherits the SOURCE'S section skeleton: its sections become the arrangement form at their real durations — same bar count, same energy arc [battery: Foote on the RENDER, blind to the JSON, found 5/6 joints within 3 bars of the source's] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- also in this genre's DNA (lower weight): curve shaped automation, acapella bridge, parallel density vs emphasis, tension and release, section contrast, energy contour, strategic pause, tempo map motion, cadence VI i fall, two chord vamp, downlifter drain

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **dnb reese color**: reese-family color: detuned unison saws, phase-beating (futureproof/toolroom refs)

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dnb_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (rolling break at 170+: tight grid, ghost 16ths a hair early, 2&4 spine full))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
