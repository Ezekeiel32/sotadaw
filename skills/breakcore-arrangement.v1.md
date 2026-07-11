---
name: breakcore-arrangement
version: 1
kind: genre
tags: [breakcore, jungle, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 180-220; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order .
  - BREAKCORE MASH is non-negotiable: breakcore: jungle chops at 180-220 with abrupt pattern switches every 1-2 bars, extreme dynamics
  - AMEN CHOPS is non-negotiable: jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
---
# Breakcore arrangement (graph-compiled)

Breakcore is a child of **jungle** — its groove laws apply unless overridden below.

## The pocket — breakcore_chaos
pattern chaos every 1-2 bars, extreme dynamic jumps, melody optional and haunted  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **breakcore mash** (w1.0): breakcore: jungle chops at 180-220 with abrupt pattern switches every 1-2 bars, extreme dynamics *(curated:claude/2026-07-03)*
- **amen chops** (w0.93): jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175 *(curated:claude/2026-07-03)*
- **reese bass** (w0.86): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*

## Inherited from jungle
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order . If a filter build was used, centroid_by_quarter must RISE into the drop.
