---
name: kuduro-arrangement
version: 2
kind: genre
tags: [kuduro, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-140; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - KUDURO BATIDA is non-negotiable: kuduro: raw 4/4 batida at 125-140 from chopped vocal shouts, sawtooth stabs and carnival whistles; percussion loops hard-panned, energy over polish
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Kuduro arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **kuduro batida** (w0.95): kuduro: raw 4/4 batida at 125-140 from chopped vocal shouts, sawtooth stabs and carnival whistles; percussion loops hard-panned, energy over polish *(curated:claude/2026-07-03-w9)*
- **vocal chops** (w0.8): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **mallet marimba**: faust marimba: struck bar (fundamental + ~4x shine partial + thump), no sustain — kuduro/cinematic/ambient mallets; fast low-vel repeats = rolls

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
