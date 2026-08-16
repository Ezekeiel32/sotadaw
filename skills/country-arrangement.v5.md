---
name: country-arrangement
version: 5
kind: genre
tags: [country, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-130; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>mid>low.
  - MANDOLIN CHOP is non-negotiable: the mandolin 'chop': a short, damped closed-chord stab on beats 2 & 4 — it IS the snare of a drumless string band
  - HIGH THIRD HARMONY is non-negotiable: (see technique node)
  - FIDDLE LINES is non-negotiable: (see technique node)
  - TRAIN BEAT is non-negotiable: country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills
---
# Country arrangement (graph-compiled)

## The pocket — train_beat
country loop DNA (wave16) Swing 0.54 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **mandolin chop** (wNone): the mandolin 'chop': a short, damped closed-chord stab on beats 2 & 4 — it IS the snare of a drumless string band *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **high third harmony** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **fiddle lines** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **pedal steel bed** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **acoustic guitar boom chick** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **banjo rolls** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **telecaster twang** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **train beat** (w0.95): country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills *(curated:claude/2026-07-03-w7)*
- **walking bass** (w0.7): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **tape saturation** (w0.5): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **twelve bar blues** (w0.5): the 12-bar blues as head and blowing form — central to hard bop *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
