---
name: phonk-arrangement
version: 4
kind: genre
tags: [phonk, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-145; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -16..-8, band order low>lowmid>mid>himid>high.
  - COWBELL LEAD is non-negotiable: saturated cowbell/bell riff as THE melodic hook, minor pentatonic
  - LOUDNESS RECOVERY is non-negotiable: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Phonk arrangement (graph-compiled)

Phonk is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — phonk_drums
trap pocket but denser hats; kick doubles before snare; everything saturated  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **cowbell lead** (w1.0): saturated cowbell/bell riff as THE melodic hook, minor pentatonic *(curated:claude/2026-07-02)*
- **loudness recovery** (w0.97): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **gain staged saturation** (w0.95): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **memphis chant** (w0.92): dark chopped vocal stab as rhythmic texture (sample kit / choir low) *(curated:claude/2026-07-02)*
- **tape saturation** (w0.84): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **halftime groove** (w0.76): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **808 glide** (w0.68): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **swing 16th** (w0.52): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*

## Inherited from trap
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- layered kick: sample kick transient + faust 808 body, body -6 to -12 under
- layered snare: sample clap + synth snare body at -12 to -18

## Sound recipes (this palette, these moves)
- **phonk cowbell**: hat_metal detuned low (source.decay up) OR gm_drums cowbell key 56, through fx_saturate drive 10
- **phonk chant**: choir kit low register, short notes on offbeats, fx_reverb small dark
- **phonk 808**: kick_808 with 808_glide walking C#1, fx_saturate on the 808 ALLOWED here (genre exception)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-8, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
