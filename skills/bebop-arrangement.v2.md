---
name: bebop-arrangement
version: 2
kind: genre
tags: [bebop, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-320; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -18..-13, band order lowmid>mid>low.
  - II V I CHANGES is non-negotiable: dense functional ii-V-I cells at a fast harmonic rhythm (often two chords a bar) — the bebop engine
  - CHROMATIC BEBOP LINE is non-negotiable: bebop-scale 8th-note lines: a chromatic passing tone inserted so chord tones land on the STRONG beats
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Bebop arrangement (graph-compiled)

Bebop is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — swing_head
Swing ride + four-feel walk (medium-up ~208 BPM, swing ~60% ~2:1). Ride: quarter on every beat + the last triplet-8th after 2 & 4 (spang-a-lang); hi-hat foot on 2 & 4; walking bass quarters (root -> chromatic-approach -> next chord tone); piano comps 2-3 short rootless chunks per bar, OFF the beat. At burnout tempos flatten swing toward 52-55%. Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **ii V I changes** (w1.0): dense functional ii-V-I cells at a fast harmonic rhythm (often two chords a bar) — the bebop engine *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **chromatic bebop line** (w0.92): bebop-scale 8th-note lines: a chromatic passing tone inserted so chord tones land on the STRONG beats *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **walking bass** (w0.84): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **swing ride** (w0.76): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **rhythm changes** (w0.68): the 'I Got Rhythm' AABA 32-bar cycle used as a contrafact blowing vehicle (bebop) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tritone substitution** (w0.6): reharmonize a V7 with the bII7 a tritone away for chromatic voice-leading (bebop) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **jazz comping** (w0.52): piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th *(curated:claude/2026-07-03-w7)*
- **trading fours** (w0.44): soloists and the drummer alternate 4-bar phrases near the out-head (bebop, hard bop) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **bop combo**: faust jazz_piano (felt additive grand) comping, sax_reed the horn front line, upright_bass walking, ride_cymbal + brush_snare kit (ride-forward, hats on 2&4); PAN hard L/C/R (Blue Note, not fx_widen); short room reverb + tape; do NOT compress (keep the swing snap).

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
