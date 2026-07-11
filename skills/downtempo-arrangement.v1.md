---
name: downtempo-arrangement
version: 1
kind: genre
tags: [downtempo, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-100; set the song key (suggested: G minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - HEADNOD SLOW is non-negotiable: downtempo: 85-100bpm dusty break with the snare a hair late, warm round sub, long pads — triphop's beach-side sibling; nothing louder than relaxed
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
  - DUSTY CHAIN is non-negotiable: fx_saturate drive 6-10 + fx_reverb small dark = lofi glue
---
# Downtempo arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **headnod slow** (w0.95): downtempo: 85-100bpm dusty break with the snare a hair late, warm round sub, long pads — triphop's beach-side sibling; nothing louder than relaxed *(curated:claude/2026-07-03-w10)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **dusty chain** (w0.7): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **m7 chords** (w0.5): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
