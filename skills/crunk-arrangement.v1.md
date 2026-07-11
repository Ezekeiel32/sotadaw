---
name: crunk-arrangement
version: 1
kind: genre
tags: [crunk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 72-85; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - CRUNK SHOUT is non-negotiable: crunk: shouted GROUP vocals as the hook, minimal minor synth stabs (2-3 notes), halftime 808 slam at 75-85 — aggression as energy, space as tension
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Crunk arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **crunk shout** (w0.95): crunk: shouted GROUP vocals as the hook, minimal minor synth stabs (2-3 notes), halftime 808 slam at 75-85 — aggression as energy, space as tension *(curated:claude/2026-07-03-w12)*
- **sliding 808** (w0.8): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
