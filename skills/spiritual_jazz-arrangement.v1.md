---
name: spiritual_jazz-arrangement
version: 1
kind: genre
tags: [spiritual_jazz, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -18..-14, band order lowmid>mid>low.
  - MODAL VAMP is non-negotiable: hold a single scale/mode for 8-16 bars and improvise FROM the mode, not the changes (modal & spiritual jazz)
  - PEDAL DRONE is non-negotiable: a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock)
  - PENTATONIC WAIL is non-negotiable: an overblown minor-pentatonic saxophone CRY climbing into the ecstatic register (spiritual jazz)
---
# Spiritual_Jazz arrangement (graph-compiled)

Spiritual_Jazz is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — drone_build
'The A Love Supreme / Satchidananda drone-build' (~98-126 BPM, swung ~60%, or gridless free zones). A sustained tonic drone (tanpura + bass) under a short modal-minor bass ostinato (e.g. the 4-note 'a-love-su-preme' cell in F minor); McCoy-style piano lays a LH fifth-pedal + RH quartal stabs; Elvin-style ride pours triplets; tambourine + hand percussion layer in; the sax enters low and slowly climbs into pentatonic WAILS as the ensemble crescendos over 16+ bars to an ecstatic peak. Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **modal vamp** (w1.0): hold a single scale/mode for 8-16 bars and improvise FROM the mode, not the changes (modal & spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pedal drone** (w0.92): a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pentatonic wail** (w0.84): an overblown minor-pentatonic saxophone CRY climbing into the ecstatic register (spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tanpura drone** (w0.76): a sustained Indian-classical tonic drone (tanpura/tambura or a bass ostinato) under the whole vamp (spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **long crescendo** (w0.68): a multi-minute dynamic build from one sparse layer to an overwhelming/ecstatic climax — AUTOMATE it (late-bloom curve), never jump-cut it (post-metal, spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **quartal voicing** (w0.6): chords built by stacking FOURTHS — the 'So What' chord (Bill Evans / McCoy Tyner); rootless, open, harmonically ambiguous *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hand percussion layer** (w0.52): congas, tambourine and bells stacked polyrhythmically over the kit (spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **devotional climax** (w0.44): the ecstatic free/collective PEAK that resolves back to calm — the spiritual arc's payoff *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- swing ride: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
- jazz comping: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **devotional combo**: sax_section pentatonic WAILS over a sustained drone (supersaw/pad held = tanpura stand-in) + a bass_warm ostinato, harp (Alice Coltrane) arpeggios, rhodes McCoy quartal+pedal comp, hand percussion; a DEEP long fx_reverb SEND bus; a multi-minute crescendo AUTOMATION (rising gain/reverb/opening filter, percussion entering); leave free sections un-quantized; keep highly dynamic

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-14, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
