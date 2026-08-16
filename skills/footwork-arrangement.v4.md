---
name: footwork-arrangement
version: 4
kind: genre
tags: [footwork, jerseyclub, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 158-162; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - TRIPLET FOOTWORK is non-negotiable: footwork: 160bpm, kick/808 in triplet cells vs straight claps, hypnotic 1-bar vocal-stab loops
  - MEMPHIS CHANT is non-negotiable: dark chopped vocal stab as rhythmic texture (sample kit / choir low)
  - SPARSE KICK is non-negotiable: kick on 1 and ~3.5 only; space carries the bounce
---
# Footwork arrangement (graph-compiled)

Footwork is a child of **jerseyclub** — its groove laws apply unless overridden below.

## The pocket — footwork_cells
triplet kick cells vs straight snares, looped vox stabs, minimal melody  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **triplet footwork** (w1.0): footwork: 160bpm, kick/808 in triplet cells vs straight claps, hypnotic 1-bar vocal-stab loops *(curated:claude/2026-07-03)*
- **memphis chant** (w0.93): dark chopped vocal stab as rhythmic texture (sample kit / choir low) *(curated:claude/2026-07-02)*
- **sparse kick** (w0.86): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*

## Inherited from jerseyclub
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- club kick pattern: THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form
- bed squeak chops: chopped vocal/stab on straight 8ths riding the kick pattern
- triplet break: bar-4 triplet kick fill (hands-up moment) before the pattern restarts
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- ...and from the jerseyclub skill itself: phrase aligned blend, bass swap, filter transition

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
