---
name: dancehall-arrangement
version: 2
kind: genre
tags: [dancehall, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-105; set the song key (suggested: B minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>lowmid>mid.
  - RIDDIM BOUNCE is non-negotiable: dancehall riddim: 3+3+2 kick placement under a halftime snare on 3 — the dembow ancestor; keep melody sparse minor pentatonic so the riddim carries
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
---
# Dancehall arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **riddim bounce** (w0.95): dancehall riddim: 3+3+2 kick placement under a halftime snare on 3 — the dembow ancestor; keep melody sparse minor pentatonic so the riddim carries *(curated:claude/2026-07-03-w6)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **dembow rhythm** (w0.7): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **sparse kick** (w0.6): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- apply_groove(track='drums'-like tracks, name='dembow_lilt', amount 0.8-1.0) after writing on-grid notes — the profile carries this genre's micro-timing and velocity shape. *(curated:claude/2026-07-03 (3-3-2 lean: pushed 'a' of 2 and 4))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
