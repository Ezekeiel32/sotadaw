---
name: dembow-arrangement
version: 1
kind: genre
tags: [dembow, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-100; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
  - PERREO BASS is non-negotiable: sub doubling the kick roots, short, dark
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Dembow arrangement (graph-compiled)

## The pocket — dembow_grid
kick every beat, snare/rim at ~1.75 and ~3.75 (the 3-3-2 lilt), dark sparse melody on top  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **dembow rhythm** (w1.0): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **perreo bass** (w0.92): sub doubling the kick roots, short, dark *(curated:claude/2026-07-02)*
- **vocal chops** (w0.84): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **call response melody** (w0.76): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **dembow rim**: gm_drums rim/snare key at low velocity for the offbeat lilt

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
