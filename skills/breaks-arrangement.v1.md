---
name: breaks-arrangement
version: 1
kind: genre
tags: [breaks, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-135; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - BREAKS FLOOR is non-negotiable: breaks: the broken-beat 4/4 alternative — chunky break at 128-135, big bass stabs, DJ-tool arrangement (16-bar phrases, mixable intro/outro)
  - BREAKBEAT CHOP is non-negotiable: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
  - FILTER BUILD is non-negotiable: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
---
# Breaks arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **breaks floor** (w0.95): breaks: the broken-beat 4/4 alternative — chunky break at 128-135, big bass stabs, DJ-tool arrangement (16-bar phrases, mixable intro/outro) *(curated:claude/2026-07-03-w12)*
- **breakbeat chop** (w0.7): kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar *(skill:dnb-arrangement@v1)*
- **filter build** (w0.6): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **reese bass** (w0.6): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
