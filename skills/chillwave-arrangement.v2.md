---
name: chillwave-arrangement
version: 2
kind: genre
tags: [chillwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-115; set the song key (suggested: A major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order lowmid>low>mid.
  - CHILLWAVE HAZE is non-negotiable: chillwave: washed-out synth loops under heavy chorus/tape wobble, falsetto-height melodies, drums soft and set back — memory as a production style
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Chillwave arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **chillwave haze** (w0.95): chillwave: washed-out synth loops under heavy chorus/tape wobble, falsetto-height melodies, drums soft and set back — memory as a production style *(curated:claude/2026-07-03-w12)*
- **evolving pads** (w0.7): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **behind beat snare** (w0.6): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **tape saturation** (w0.6): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **tine kalimba**: faust kalimba: plucked tine (near-sine + inharmonic sparkle + thumb click) — lofi/afro signature; arpeggiate gently, let notes ring

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
