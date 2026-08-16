---
name: afrobeat-arrangement
version: 4
kind: genre
tags: [afrobeat, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-130; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - TONY ALLEN GROOVE is non-negotiable: afrobeat drums: broken hi-hat/kick conversation that NEVER repeats 1:1 bar to bar, ghosted snare chatter; the band vamps ONE chord for minutes — tension from layers, not changes
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Afrobeat arrangement (graph-compiled)

## The pocket — allen_ghosts
afrobeat loop DNA (wave16) Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **tony allen groove** (w0.95): afrobeat drums: broken hi-hat/kick conversation that NEVER repeats 1:1 bar to bar, ghosted snare chatter; the band vamps ONE chord for minutes — tension from layers, not changes *(curated:claude/2026-07-03-w7)*
- **horn stabs** (w0.85): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **call and response** (w0.8): antiphony: a phrase states, a second voice answers in the gap — the gap IS the invitation (our choir ad-lib lane implements this) [Popular music: texture & form] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **journey structure** (w0.7): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **hemiola 3 2** (w0.7): 3:2 cross-rhythm — two bars of 3 heard as three bars of 2 (or within-bar 3-against-2); the lift beneath afro-latin grooves [Rhythm & meter: hemiola] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **clave 23** (w0.6): the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **mallet marimba**: faust marimba: struck bar (fundamental + ~4x shine partial + thump), no sustain — kuduro/cinematic/ambient mallets; fast low-vel repeats = rolls

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='funk_pocket', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (16th funk: leans forward on the a's, audible ghosts, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
