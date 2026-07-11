---
name: footwork-arrangement
version: 1
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
triplet kick cells vs straight snares, looped vox stabs, minimal melody  *(source: curated:claude/2026-07-03)*

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
- loudness recovery: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
