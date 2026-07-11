---
name: dnb-arrangement
version: 2
kind: genre
tags: [dnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 170-176; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - BREAKBEAT CHOP is non-negotiable: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
---
# Dnb arrangement (graph-compiled)

## The pocket — dnb_break
kick 0/2.5 snare 1/3; rides 16ths; sub separate from reese  *(source: skill:dnb-arrangement@v1)*

## Techniques (weight order — the top ones DEFINE the genre)
- **breakbeat chop** (w1.0): kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar *(skill:dnb-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **reese bass** (w0.92): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*
- **loudness recovery** (w0.85): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **ghost notes** (w0.84): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
