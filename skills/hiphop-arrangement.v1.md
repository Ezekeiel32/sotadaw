---
name: hiphop-arrangement
version: 1
kind: genre
tags: [hiphop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-100; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - BREAK LOOPING is non-negotiable: hiphop's founding move: loop the break (the drum-solo bars), cut between two copies on the 1 — then rap over it; everything else (sampling, chopping, scratching) grew from this
  - FUNK BREAK is non-negotiable: the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Hiphop arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **break looping** (w0.95): hiphop's founding move: loop the break (the drum-solo bars), cut between two copies on the 1 — then rap over it; everything else (sampling, chopping, scratching) grew from this *(curated:claude/2026-07-03-w7)*
- **funk break** (w0.85): the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it *(curated:claude/2026-07-03-w5)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **dusty chain** (w0.7): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **ghost notes** (w0.6): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
