---
name: shoegaze-arrangement
version: 1
kind: genre
tags: [shoegaze, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-120; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - WALL OF BLUR is non-negotiable: shoegaze: stack fuzz + reverse-reverb + pitch-glide guitar layers until individual notes blur into a WALL; vocals mixed INTO the wall (a texture, not a lead), tempos slow
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Shoegaze arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **wall of blur** (w0.95): shoegaze: stack fuzz + reverse-reverb + pitch-glide guitar layers until individual notes blur into a WALL; vocals mixed INTO the wall (a texture, not a lead), tempos slow *(curated:claude/2026-07-03-w9)*
- **send reverb** (w0.8): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **evolving pads** (w0.6): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
