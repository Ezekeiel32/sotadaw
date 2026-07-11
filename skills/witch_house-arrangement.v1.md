---
name: witch_house-arrangement
version: 1
kind: genre
tags: [witch_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-75; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order low>lowmid>mid.
  - WITCH DRAG is non-negotiable: witch house: chopped-and-screwed DRAG — halftime 60-70 feel, pitched-down vocals, hi-hats crawling in triplets, occult drones underneath
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Witch_House arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **witch drag** (w0.95): witch house: chopped-and-screwed DRAG — halftime 60-70 feel, pitched-down vocals, hi-hats crawling in triplets, occult drones underneath *(curated:claude/2026-07-03-w12)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **send reverb** (w0.7): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
