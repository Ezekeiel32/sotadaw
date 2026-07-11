---
name: gqom-arrangement
version: 3
kind: genre
tags: [gqom, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-128; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - GQOM PULSE is non-negotiable: gqom: NO four-floor - broken kick pulse (1, 2.5, 3) + big tom hits, dark minimal, heavy swing feel
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - TAPE SATURATION is non-negotiable: heavy fx_saturate drive 8-14 over the whole beat bus = grit
---
# Gqom arrangement (graph-compiled)

## The pocket — gqom_dark
broken pulse, cavernous toms, chant stabs; NO melody needed; drums are the song  *(source: curated:claude/2026-07-03 + grid:curated:claude/2026-07-03 (machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gqom pulse** (w1.0): gqom: NO four-floor - broken kick pulse (1, 2.5, 3) + big tom hits, dark minimal, heavy swing feel *(curated:claude/2026-07-03)*
- **huge space** (w0.93): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **tape saturation** (w0.86): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **piano log drum**: faust log_drum: THE amapiano bass — woody pitch-drop knock over a round sub tail; sequence it as the bassline answering the kick in the holes

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
