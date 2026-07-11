---
name: tango-arrangement
version: 1
kind: genre
tags: [tango, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-70; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - TANGO MARCATO is non-negotiable: tango: marcato in 4 — dry stabbing strings/piano on EVERY beat, bandoneon-style sighs (accordion, slow bellows) between phrases, D-minor drama; NO drum kit, the ensemble IS the rhythm
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Tango arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **tango marcato** (w0.95): tango: marcato in 4 — dry stabbing strings/piano on EVERY beat, bandoneon-style sighs (accordion, slow bellows) between phrases, D-minor drama; NO drum kit, the ensemble IS the rhythm *(curated:claude/2026-07-03-w13)*
- **m7 chords** (w0.6): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.4): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
