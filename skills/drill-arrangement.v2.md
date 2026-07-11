---
name: drill-arrangement
version: 2
kind: genre
tags: [drill, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 138-146; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -18..-9, band order low>lowmid>mid>himid>high.
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - GHOST SNARE DRILL is non-negotiable: extra snares at 3.75/4.25 around the main pocket
---
# Drill arrangement (graph-compiled)

Drill is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — drill_drums
UK drill pocket: snare 3, ghosts 3.75/4.25, sliding 808  *(source: skill:drill-arrangement@v1)*

## Techniques (weight order — the top ones DEFINE the genre)
- **sliding 808** (w1.0): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **ghost snare drill** (w0.92): extra snares at 3.75/4.25 around the main pocket *(skill:drill-arrangement@v1)*
- **halftime groove** (w0.84): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **hat rolls** (w0.76): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*

## Inherited from trap
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- 808 glide: long overlapping 808 notes walking the scale; tune to key
- layered kick: sample kick transient + faust 808 body, body -6 to -12 under
- layered snare: sample clap + synth snare body at -12 to -18
- loudness recovery: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-9, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
