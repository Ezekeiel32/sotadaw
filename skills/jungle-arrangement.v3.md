---
name: jungle-arrangement
version: 3
kind: genre
tags: [jungle, dnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 160-175; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - AMEN CHOPS is non-negotiable: jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Jungle arrangement (graph-compiled)

Jungle is a child of **dnb** — its groove laws apply unless overridden below.

## The pocket — jungle_break
chopped break leads, sub reese below, sparse dark pads; breaks re-chop every 4 bars  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **amen chops** (w1.0): jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175 *(curated:claude/2026-07-03)*
- **reese bass** (w0.93): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*
- **send reverb** (w0.86): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Inherited from dnb
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- breakbeat chop: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter
- ...and from the dnb skill itself: tempo map motion, curve shaped automation, cadence VI i fall, two chord vamp, complementary eq unmask, parallel density vs emphasis, acapella bridge, structure inheritance, mono below 120, downlifter drain, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dnb_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (rolling break at 170+: tight grid, ghost 16ths a hair early, 2&4 spine full))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
