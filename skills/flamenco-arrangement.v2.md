---
name: flamenco-arrangement
version: 2
kind: genre
tags: [flamenco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-130; set the song key (suggested: E major).
  - Mix: clipped_samples == 0, LUFS -15..-10, band order lowmid>mid>low.
  - FLAMENCO COMPAS is non-negotiable: flamenco: the 12-beat compás with accents on 3-6-8-10-12 (bulería feel), palmas hand-clap layers, phrygian around E — nylon strums played AS percussion
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Flamenco arrangement (graph-compiled)

## The pocket — rumba_palmas
flamenco loop DNA (wave20)  *(source: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete))*

## Techniques (weight order — the top ones DEFINE the genre)
- **flamenco compas** (w0.95): flamenco: the 12-beat compás with accents on 3-6-8-10-12 (bulería feel), palmas hand-clap layers, phrygian around E — nylon strums played AS percussion *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **huge space** (w0.4): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
