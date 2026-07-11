---
name: baltimore_club-arrangement
version: 2
kind: genre
tags: [baltimore_club, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-135; set the song key (suggested: G minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - BMORE BREAK is non-negotiable: baltimore club: the Sing-Sing/Think break stuttering under a x.x.xx.x kick cell at ~130, chopped one-word vocal shots — raw, unquantized-feeling, relentless
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
---
# Baltimore_Club arrangement (graph-compiled)

## The pocket — bmore_cell
baltimore_club loop DNA (wave18)  *(source: curated:claude/2026-07-04 + grid:curated (wave18 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **bmore break** (w0.95): baltimore club: the Sing-Sing/Think break stuttering under a x.x.xx.x kick cell at ~130, chopped one-word vocal shots — raw, unquantized-feeling, relentless *(curated:claude/2026-07-03-w12)*
- **vocal chops** (w0.8): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **four on floor** (w0.5): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
