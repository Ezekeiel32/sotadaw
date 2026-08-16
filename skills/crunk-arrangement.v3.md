---
name: crunk-arrangement
version: 3
kind: genre
tags: [crunk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-80; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - CRUNK SHOUT is non-negotiable: crunk: shouted GROUP vocals as the hook, minimal minor synth stabs (2-3 notes), halftime 808 slam at 75-85 — aggression as energy, space as tension
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Crunk arrangement (graph-compiled)

## The pocket — crunk_menace
crunk loop DNA (wave18)  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **crunk shout** (w0.95): crunk: shouted GROUP vocals as the hook, minimal minor synth stabs (2-3 notes), halftime 808 slam at 75-85 — aggression as energy, space as tension *(curated:claude/2026-07-03-w12)*
- **sliding 808** (w0.8): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
