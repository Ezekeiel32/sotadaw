---
name: trap-arrangement
version: 3
kind: genre
tags: [trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -18..-9, band order low>lowmid>mid>himid>high.
  - HALFTIME GROOVE is non-negotiable: snare on beat 3 (not 2&4); space is the instrument
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Trap arrangement (graph-compiled)

## The pocket — trap_drums
kick sparse+syncopated; snare beat 3; hats 8th/16th w/ rolls  *(source: skill:trap-arrangement@v2)*

## Techniques (weight order — the top ones DEFINE the genre)
- **halftime groove** (w1.0): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **swing 16th** (w0.92): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **loudness recovery** (w0.85): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **ghost notes** (w0.84): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **hat rolls** (w0.76): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **808 glide** (w0.68): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **layered kick** (w0.6): sample kick transient + faust 808 body, body -6 to -12 under *(skill:sound-palette@v2)*
- **layered snare** (w0.52): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-9, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
