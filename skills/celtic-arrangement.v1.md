---
name: celtic-arrangement
version: 1
kind: genre
tags: [celtic, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-120; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -15..-10, band order lowmid>mid>low.
  - CELTIC REEL is non-negotiable: celtic reel: constant 8th-note melodic motion at 110-120, fiddle/whistle doubled in unison, bodhrán pulse underneath, DRONES under everything
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
---
# Celtic arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **celtic reel** (w0.95): celtic reel: constant 8th-note melodic motion at 110-120, fiddle/whistle doubled in unison, bodhrán pulse underneath, DRONES under everything *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **evolving pads** (w0.5): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
