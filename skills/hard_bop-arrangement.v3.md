---
name: hard_bop-arrangement
version: 3
kind: genre
tags: [hard_bop, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-240; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -17..-12, band order lowmid>mid>low.
  - BACKBEAT ACCENT is non-negotiable: ride spang-a-lang but with the hi-hat/snare hit HARD on 2 & 4 (or a shuffle) — the bop -> hard-bop groove shift
  - GOSPEL BLUES PIANO is non-negotiable: funky rootless and gospel BLOCK-chord comping with blue notes and grace-note bends (hard bop, soul jazz)
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Hard_Bop arrangement (graph-compiled)

Hard_Bop is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — backbeat_shuffle
Backbeat-driven swing shuffle (medium ~132 BPM, swing ~65% ~2:1). Ride spang-a-lang; snare cross-stick / hi-hat accented HARD on 2 & 4 (the backbeat drive); walking bass, bluesier and more repetitive (or a 2-bar riff on soul/Latin tunes); piano lays gospel block-chord stabs + bluesy fills. Latin sections switch to STRAIGHT eighths (swing 50%) montuno. Swing 0.65 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **backbeat accent** (w1.0): ride spang-a-lang but with the hi-hat/snare hit HARD on 2 & 4 (or a shuffle) — the bop -> hard-bop groove shift *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **gospel blues piano** (w0.92): funky rootless and gospel BLOCK-chord comping with blue notes and grace-note bends (hard bop, soul jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **walking bass** (w0.84): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **swing ride** (w0.76): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **twelve bar blues** (w0.68): the 12-bar blues as head and blowing form — central to hard bop *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **soul jazz groove** (w0.6): a riff/vamp-based, danceable, R&B- and gospel-inflected groove (hard bop / soul jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **afro latin vamp** (w0.52): a straight-eighth montuno / calypso vamp section bookending the swung blowing (hard bop — Song for My Father) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **trading fours** (w0.44): soloists and the drummer alternate 4-bar phrases near the out-head (bebop, hard bop) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- jazz comping: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **blue note combo**: faust hammond_organ (drawbars + Leslie + key-click) or jazz_piano gospel block comping, sax_reed harmonized front line, upright_bass walking, ride_cymbal + brush_snare with a HARD 2&4 backbeat; vibraphone as a Blue Note color; short plate + tape warmth; stay dynamic.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -17..-12, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
