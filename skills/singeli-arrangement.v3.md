---
name: singeli-arrangement
version: 3
kind: genre
tags: [singeli, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 180-300; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order lowmid>mid>low.
  - SINGELI SPRINT is non-negotiable: singeli: 180-300bpm frantic loop music — pitched-up taarab/bongo samples looped tight, MC shouts riding on top; the SPEED is the genre; keep the loop 1-2 bars max
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - SPARSE KICK is non-negotiable: kick on 1 and ~3.5 only; space carries the bounce
---
# Singeli arrangement (graph-compiled)

## The pocket — singeli_sprint
singeli loop DNA (wave20)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **singeli sprint** (w0.95): singeli: 180-300bpm frantic loop music — pitched-up taarab/bongo samples looped tight, MC shouts riding on top; the SPEED is the genre; keep the loop 1-2 bars max *(curated:claude/2026-07-03-w9)*
- **vocal chops** (w0.7): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **sparse kick** (w0.4): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
