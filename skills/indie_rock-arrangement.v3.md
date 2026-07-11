---
name: indie_rock-arrangement
version: 3
kind: genre
tags: [indie_rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-145; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - JANGLE STRUM is non-negotiable: indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed
  - TAPE SATURATION is non-negotiable: heavy fx_saturate drive 8-14 over the whole beat bus = grit
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Indie_Rock arrangement (graph-compiled)

## The pocket — indie_loose
indie_rock loop DNA (wave16) Swing 0.51 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 (wave17 swing-grid migration; bug class from wave16 blues probe))*

## Techniques (weight order — the top ones DEFINE the genre)
- **jangle strum** (w0.9): indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed *(curated:claude/2026-07-03-w9)*
- **tape saturation** (w0.6): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **huge space** (w0.6): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **power chords** (w0.6): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
