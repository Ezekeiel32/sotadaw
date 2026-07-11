---
name: dembow-arrangement
version: 2
kind: genre
tags: [dembow, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-100; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
  - PERREO BASS is non-negotiable: sub doubling the kick roots, short, dark
  - GROOVE DEMBOW LILT is non-negotiable: apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean.
---
# Dembow arrangement (graph-compiled)

## The pocket — dembow_grid
kick every beat, snare/rim at ~1.75 and ~3.75 (the 3-3-2 lilt), dark sparse melody on top  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **dembow rhythm** (w1.0): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **perreo bass** (w0.92): sub doubling the kick roots, short, dark *(curated:claude/2026-07-02)*
- **groove dembow lilt** (w0.9): apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **vocal chops** (w0.84): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **call response melody** (w0.76): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **dembow rim**: gm_drums rim/snare key at low velocity for the offbeat lilt
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
