---
name: ambient-arrangement
version: 3
kind: genre
tags: [ambient, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-85; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -26..-14, band order .
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - SLOW FILTER DRIFT is non-negotiable: cutoff automation over 16+ bars, barely perceptible motion
---
# Ambient arrangement (graph-compiled)

## The pocket — ambient_flow
no grid tyranny: overlapping 8-16 beat pads, sparse bells, events BREATHE; drums optional/ghosted  *(source: curated:claude/2026-07-02 + grid:curated:claude/2026-07-03 (machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **evolving pads** (w1.0): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **huge space** (w0.92): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **slow filter drift** (w0.84): cutoff automation over 16+ bars, barely perceptible motion *(curated:claude/2026-07-02)*
- **pentatonic bells** (w0.76): sparse bell notes (fmbell), pentatonic, let ring *(curated:claude/2026-07-02)*
- **send reverb** (w0.68): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Sound recipes (this palette, these moves)
- **ambient wash**: pad_motion long notes through TWO reverb buses (one dark size 8, one bright size 4)
- **mallet marimba**: faust marimba: struck bar (fundamental + ~4x shine partial + thump), no sustain — kuduro/cinematic/ambient mallets; fast low-vel repeats = rolls
- **gliss harp**: faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -26..-14, band order . If a filter build was used, centroid_by_quarter must RISE into the drop.
