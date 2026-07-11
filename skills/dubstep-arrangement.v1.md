---
name: dubstep-arrangement
version: 1
kind: genre
tags: [dubstep, ukgarage, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 138-142; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - HALF TIME 140 is non-negotiable: dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge
  - WOBBLE BASS is non-negotiable: LFO-filtered bass (our 'wobble' voice / reese+fx_filter automation at 1/8-1/4 rates), call-response with drums
  - RISER THROWS is non-negotiable: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)
---
# Dubstep arrangement (graph-compiled)

Dubstep is a child of **ukgarage** — its groove laws apply unless overridden below.

## The pocket — dub_halftime
snare 3 ONLY; kick 1+syncop; wobble answers the drums; drops = wobble unleashed  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **half time 140** (w1.0): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*
- **wobble bass** (w0.93): LFO-filtered bass (our 'wobble' voice / reese+fx_filter automation at 1/8-1/4 rates), call-response with drums *(curated:claude/2026-07-03)*
- **riser throws** (w0.86): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **gain staged saturation** (w0.79): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Inherited from ukgarage
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- shuffle swing: hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt
- two step kick: NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove
- chopped chords: short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
