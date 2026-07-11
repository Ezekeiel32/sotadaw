---
name: sexy_drill-arrangement
version: 2
kind: genre
tags: [sexy_drill, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 136-145; set the song key (suggested: Bb minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>lowmid>mid.
  - SEXY DRILL BOUNCE is non-negotiable: sexy drill: airy chopped vocal/soul loops floating free, SPARSE sliding 808 landing behind the beat, rimshot-led halftime drums ~140 — seduction through space, not aggression
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Sexy_Drill arrangement (graph-compiled)

## The pocket — sexydrill_bounce
displaced drill kicks under rim-led halftime  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sexy drill bounce** (w0.95): sexy drill: airy chopped vocal/soul loops floating free, SPARSE sliding 808 landing behind the beat, rimshot-led halftime drums ~140 — seduction through space, not aggression *(curated:claude/2026-07-03-w8)*
- **sliding 808** (w0.8): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **vocal chops** (w0.75): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **half time 140** (w0.7): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
