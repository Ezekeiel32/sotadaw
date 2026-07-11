---
name: jerseyclub-arrangement
version: 2
kind: genre
tags: [jerseyclub, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 132-142; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - CLUB KICK PATTERN is non-negotiable: THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - BED SQUEAK CHOPS is non-negotiable: chopped vocal/stab on straight 8ths riding the kick pattern
---
# Jerseyclub arrangement (graph-compiled)

Jerseyclub is a child of **house** — its groove laws apply unless overridden below.

## The pocket — jersey_kicks
the 5-kick bed (1, 1.5, 2.5, 3, 3.5) three bars, triplet fill bar 4, chops on 8ths  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **club kick pattern** (w1.0): THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form *(curated:claude/2026-07-02)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **bed squeak chops** (w0.92): chopped vocal/stab on straight 8ths riding the kick pattern *(curated:claude/2026-07-02)*
- **loudness recovery** (w0.85): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **triplet break** (w0.84): bar-4 triplet kick fill (hands-up moment) before the pattern restarts *(curated:claude/2026-07-02)*
- **vocal chops** (w0.76): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **send reverb** (w0.68): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- offbeat bass: bass hits on the 8th between kicks

## Sound recipes (this palette, these moves)
- **jersey chop**: choir kit high key or pluck2 stab on 8ths, fx_reverb small
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
