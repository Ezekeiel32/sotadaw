---
name: jungle-arrangement
version: 1
kind: genre
tags: [jungle, dnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 160-175; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - AMEN CHOPS is non-negotiable: jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Jungle arrangement (graph-compiled)

Jungle is a child of **dnb** — its groove laws apply unless overridden below.

## The pocket — jungle_break
chopped break leads, sub reese below, sparse dark pads; breaks re-chop every 4 bars  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **amen chops** (w1.0): jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175 *(curated:claude/2026-07-03)*
- **reese bass** (w0.93): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*
- **send reverb** (w0.86): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Inherited from dnb
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- breakbeat chop: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
- loudness recovery: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
