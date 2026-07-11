---
name: techno-arrangement
version: 1
kind: genre
tags: [techno, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-136; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - RUMBLE KICK is non-negotiable: kick tail feeds a send reverb lowpassed into a rolling rumble
  - MODULAR STAB is non-negotiable: single dark stab/chord repeated with filter automation variation
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Techno arrangement (graph-compiled)

Techno is a child of **house** — its groove laws apply unless overridden below.

## The pocket — techno_grid
relentless kick, offbeat hats, one stab varied by automation, 16-bar arcs  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w1.0): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **rumble kick** (w0.92): kick tail feeds a send reverb lowpassed into a rolling rumble *(curated:claude/2026-07-02)*
- **modular stab** (w0.84): single dark stab/chord repeated with filter automation variation *(curated:claude/2026-07-02)*
- **filter build** (w0.76): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **pump sidechain** (w0.68): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*

## Inherited from house
- offbeat bass: bass hits on the 8th between kicks

## Sound recipes (this palette, these moves)
- **techno rumble**: kick_punch + send to verb bus (size 6+) with fx_filter cutoff 150 on the bus return
- **techno stab**: keys_dark single chord, fx_filter + automate cutoff per 4 bars, fx_delay dotted

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
