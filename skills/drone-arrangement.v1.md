---
name: drone-arrangement
version: 1
kind: genre
tags: [drone, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-60; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -20..-12, band order lowmid>low>mid.
  - DRONE TENSION is non-negotiable: drone: one sustained cluster evolving by slow filter/detune/partial motion — no rhythm, no bar lines; FORM IS DURATION; motion so slow it is felt not heard
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Drone arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **drone tension** (w0.95): drone: one sustained cluster evolving by slow filter/detune/partial motion — no rhythm, no bar lines; FORM IS DURATION; motion so slow it is felt not heard *(curated:claude/2026-07-03-w10)*
- **evolving pads** (w0.8): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **huge space** (w0.7): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -20..-12, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
