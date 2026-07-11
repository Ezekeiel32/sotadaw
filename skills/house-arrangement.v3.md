---
name: house-arrangement
version: 3
kind: genre
tags: [house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-128; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# House arrangement (graph-compiled)

## The pocket — house_grid
kick 1/2/3/4, openhat offbeats, clap 2&4  *(source: skill:house-arrangement@v1)*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w1.0): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **offbeat bass** (w0.92): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **groove ukg shuffle** (w0.9): THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **loudness recovery** (w0.85): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **pump sidechain** (w0.84): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **filter build** (w0.76): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
