---
name: free_jazz-arrangement
version: 1
kind: genre
tags: [free_jazz, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-320; set the song key (suggested: pantonal (C pedal)).
  - Mix: clipped_samples == 0, LUFS -18..-13, band order lowmid>mid>low.
  - ENERGY PULSE WASH is non-negotiable: no groove pattern: ride/cymbal-edge WASH at 6-12 hits/sec + off-grid snare bursts (3-9 hit clusters) + spasmodic kick — density replaces meter
  - COLLECTIVE IMPROV is non-negotiable: everyone solos at once: sax skronk, arco bass groans, piano clusters — lines answer each other's ENERGY not chords
  - PANTONAL LINE is non-negotiable: melody is pantonal/chromatic or one modal pedal — wide leaps, overblown cries, no functional changes to spell
---
# Free_Jazz arrangement (graph-compiled)

Free_Jazz is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — energy_wash
Free jazz (~230 BPM pulse — but NO meter): ride/cymbal-edge WASH at high density; snare bursts in off-grid clusters; kick spasmodic (never a pattern); two basses (pizz flurries + arco groans); sax skronk in wide pantonal leaps. THE LAW: never loop a bar identically — the form is a density ARC (sparse -> boiling -> collapse), use tempoMap accel/rit waves and section-level density automation. Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **energy pulse wash** (w1.0): no groove pattern: ride/cymbal-edge WASH at 6-12 hits/sec + off-grid snare bursts (3-9 hit clusters) + spasmodic kick — density replaces meter *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **collective improv** (w0.92): everyone solos at once: sax skronk, arco bass groans, piano clusters — lines answer each other's ENERGY not chords *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **pantonal line** (w0.84): melody is pantonal/chromatic or one modal pedal — wide leaps, overblown cries, no functional changes to spell *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **density arc form** (w0.76): the form is a DENSITY ARC: sparse -> boiling -> collapse -> regeneration; use tempoMap accel/rit waves, never loop a bar twice identically *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **arco bass groan** (w0.68): bowed double-bass groans and pizzicato flurries as a second front-line voice (often TWO basses) *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- swing ride: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
- jazz comping: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **energy combo**: sax_section overblown wide-leap lines; upright_bass x2 (one pizz flurries, one long arco groans = sustained low notes); ride-forward kit at high density with NO backbeat; jazz_piano cluster stabs; room reverb, hugely dynamic, never quantize, never loop

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
