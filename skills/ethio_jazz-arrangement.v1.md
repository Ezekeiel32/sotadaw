---
name: ethio_jazz-arrangement
version: 1
kind: genre
tags: [ethio_jazz, jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 75-130; set the song key (suggested: C major (tizita pentatonic)).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order lowmid>mid>low.
  - TIZITA MODE is non-negotiable: the TIZITA qenet: a nostalgic Ethiopian major-type pentatonic (1 2 3 5 6) — the wistful, homesick color at the heart of Ethio-jazz
  - ETHIO PENTATONIC QENET is non-negotiable: melodies drawn from one of the four Ethiopian pentatonic qenet (tizita, ambassel [1 2 3 5 b6, natural 2nd/lowered 6th], bati, anchihoye) over Western jazz harmony
  - COMPOUND LATIN SWING is non-negotiable: a languid Latin-jazz lilt: swung ride over an even kick-snare, congas + kebero laying 6-against-4 / 12-8 cross-rhythm against the 4/4 — the Astatke groove
---
# Ethio_Jazz arrangement (graph-compiled)

Ethio_Jazz is a child of **jazz** — its groove laws apply unless overridden below.

## The pocket — tizita_vamp
Ethio-jazz (~95 BPM, swung ~60%, 12/8 feel over 4/4): a short modal bass + horn OSTINATO held under long solos; vibraphone (motor on) states the tizita-pentatonic head, Wurlitzer/organ doubling; swung ride over an even kick-snare while congas + kebero lay a 6-against-4 cross-pulse. Languid, hypnotic, minimal chord motion. Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tizita mode** (w1.0): the TIZITA qenet: a nostalgic Ethiopian major-type pentatonic (1 2 3 5 6) — the wistful, homesick color at the heart of Ethio-jazz *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **ethio pentatonic qenet** (w0.92): melodies drawn from one of the four Ethiopian pentatonic qenet (tizita, ambassel [1 2 3 5 b6, natural 2nd/lowered 6th], bati, anchihoye) over Western jazz harmony *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **compound latin swing** (w0.84): a languid Latin-jazz lilt: swung ride over an even kick-snare, congas + kebero laying 6-against-4 / 12-8 cross-rhythm against the 4/4 — the Astatke groove *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **vibraphone lead ethio** (w0.76): vibraphone (motor tremolo on) carries the modal head, doubled by organ/Wurlitzer — the signature Ethio-jazz timbre *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **modal ostinato vamp** (w0.68): a short repeating bass + horn riff held under long modal solos — vamp-based, minimal chord motion *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **kebero crossrhythm** (w0.6): the kebero hand-drum + congas stack a 6/8 triplet cross-pulse against the straight kit, giving the groove its rolling, off-square feel *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from jazz
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- swing ride: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
- jazz comping: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- axis progression: i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it

## Sound recipes (this palette, these moves)
- **ethio combo**: vibraphone (motor tremolo) lead + rhodes/organ_soul (Wurli) doubling the tizita head; bass_warm walking ostinato; congas + kebero (perc/timpani) for the 6/8 cross-rhythm; sax_section for horn lines. Warm, dynamic, tape saturation not brickwall.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
