---
name: sexy_drill-arrangement
version: 3
kind: genre
tags: [sexy_drill, ny_drill, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-140; set the song key (suggested: Bb minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>lowmid>mid.
  - SEXY DRILL BOUNCE is non-negotiable: sexy drill: airy chopped vocal/soul loops floating free, SPARSE sliding 808 landing behind the beat, rimshot-led halftime drums ~140 — seduction through space, not aggression
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Sexy_Drill arrangement (graph-compiled)

Sexy_Drill is a child of **ny_drill** — its groove laws apply unless overridden below.

## The pocket — sexydrill_bounce
displaced drill kicks under rim-led halftime  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sexy drill bounce** (w0.95): sexy drill: airy chopped vocal/soul loops floating free, SPARSE sliding 808 landing behind the beat, rimshot-led halftime drums ~140 — seduction through space, not aggression *(curated:claude/2026-07-03-w8)*
- **sliding 808** (w0.8): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **vocal chops** (w0.75): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **half time 140** (w0.7): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='drill_slip', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (drill's slippery lean: 3rd 16th of each beat pushed hard, light drag elsewhere))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
