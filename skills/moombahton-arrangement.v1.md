---
name: moombahton-arrangement
version: 1
kind: genre
tags: [moombahton, dembow, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 108-112; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - MOOMBA GALLOP is non-negotiable: moombahton: dembow lilt slowed to 108-112 with house build energy, spring-reverb stabs
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
  - FILTER BUILD is non-negotiable: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
---
# Moombahton arrangement (graph-compiled)

Moombahton is a child of **dembow** — its groove laws apply unless overridden below.

## The pocket — moomba_pocket
dembow lilt at house tempo, big builds, spring stabs  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **moomba gallop** (w1.0): moombahton: dembow lilt slowed to 108-112 with house build energy, spring-reverb stabs *(curated:claude/2026-07-03)*
- **dembow rhythm** (w0.93): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **filter build** (w0.86): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **vocal chops** (w0.79): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## Inherited from dembow
- call response melody: 2-bar call, 2-bar answer; melody talks to itself
- perreo bass: sub doubling the kick roots, short, dark

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
