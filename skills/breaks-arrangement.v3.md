---
name: breaks-arrangement
version: 3
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

## The pocket — funky_lift
breaks loop DNA (wave15) Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **breaks floor** (w0.95): breaks: the broken-beat 4/4 alternative — chunky break at 128-135, big bass stabs, DJ-tool arrangement (16-bar phrases, mixable intro/outro) *(curated:claude/2026-07-03-w12)*
- **breakbeat chop** (w0.7): kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar *(skill:dnb-arrangement@v1)*
- **filter build** (w0.6): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **reese bass** (w0.6): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='funk_pocket', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (16th funk: leans forward on the a's, audible ghosts, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
