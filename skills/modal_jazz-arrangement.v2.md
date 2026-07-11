---
name: modal_jazz-arrangement
version: 2
kind: genre
tags: [modal_jazz, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-300; set the song key (suggested: D dorian).
  - Mix: clipped_samples == 0, LUFS -18..-13, band order lowmid>mid>low.
  - MODAL VAMP is non-negotiable: hold a single scale/mode for 8-16 bars and improvise FROM the mode, not the changes (modal & spiritual jazz)
  - QUARTAL VOICING is non-negotiable: chords built by stacking FOURTHS — the 'So What' chord (Bill Evans / McCoy Tyner); rootless, open, harmonically ambiguous
  - SLOW HARMONIC RHYTHM is non-negotiable: two or three chords across an ENTIRE tune — harmony as a held space (modal jazz)
---
# Modal_Jazz arrangement (graph-compiled)

Modal_Jazz is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — so_what_vamp
'The So What vamp' (32-bar AABA at ~134 BPM, swung ~64%). Upright bass states the 2-bar D-Dorian riff, piano ANSWERS with the So What quartal stab (E-A / D-G-B) syncopated on the 'and'; ride plays swung spang-a-lang, hi-hat on 2 & 4, kick feathered. Bridge: transpose the whole call-and-response up a half-step to Eb Dorian for 8 bars, then back. Swing 0.64 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **modal vamp** (w1.0): hold a single scale/mode for 8-16 bars and improvise FROM the mode, not the changes (modal & spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **quartal voicing** (w0.92): chords built by stacking FOURTHS — the 'So What' chord (Bill Evans / McCoy Tyner); rootless, open, harmonically ambiguous *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **slow harmonic rhythm** (w0.84): two or three chords across an ENTIRE tune — harmony as a held space (modal jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pedal drone** (w0.76): a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **scalar improvisation** (w0.68): solo lines drawn from the mode's scale rather than spelling fast changes (modal jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **rootless comping** (w0.6): the piano omits the root, leaving it to the bass, and voices only the color tones (modal, hard bop) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **swing ride** (w0.52): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **contrafact** (w0.44): a new head written over an existing modal/harmonic frame (Impressions <- So What) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- jazz comping: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **modal combo**: faust jazz_piano QUARTAL comping over an upright_bass modal PEDAL, sax_reed lead, ride_cymbal + brush_snare kit; ONE shared room-reverb send bus; long AABA vamp; build intensity over the solo via gain + reverb-send AUTOMATION (late-bloom); steady tempoMap.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
