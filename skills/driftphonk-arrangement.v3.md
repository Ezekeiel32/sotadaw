---
name: driftphonk-arrangement
version: 3
kind: genre
tags: [driftphonk, phonk, memphis_phonk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - DRIFT SLOWDOWN is non-negotiable: drift phonk: 130-140 half-feel, detuned cowbell lead, tape wow (slight pitch automation), car-sub 808
  - COWBELL LEAD is non-negotiable: saturated cowbell/bell riff as THE melodic hook, minor pentatonic
  - TAPE SATURATION is non-negotiable: heavy fx_saturate drive 8-14 over the whole beat bus = grit
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Driftphonk arrangement (graph-compiled)

Driftphonk is a child of **phonk, memphis_phonk** — its groove laws apply unless overridden below.

## The pocket — drift_pocket
phonk pocket + slowed half-feel sections, wow'd cowbell, car-test sub  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## The pocket — memphis_knock
memphis_rap loop DNA (wave15) Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **drift slowdown** (w1.0): drift phonk: 130-140 half-feel, detuned cowbell lead, tape wow (slight pitch automation), car-sub 808 *(curated:claude/2026-07-03)*
- **cowbell lead** (w0.93): saturated cowbell/bell riff as THE melodic hook, minor pentatonic *(curated:claude/2026-07-02)*
- **tape saturation** (w0.86): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **808 glide** (w0.79): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*

## Inherited from phonk, memphis_phonk
- halftime groove: snare on beat 3 (not 2&4); space is the instrument
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- hat rolls: 16th->32nd bursts at phrase ends; velocity ramps
- memphis chant: dark chopped vocal stab as rhythmic texture (sample kit / choir low)
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- cadence VI i fall: VI->i fall: subdominant slide home — melancholic loop-closer (trance/dnb/phonk)
- ...and from the phonk skill itself: two chord vamp, unmask escalation ladder, parallel thwack attack

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='halftime_drag', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (phonk/memphis/doom drag: uniform lag, backbeat extra late))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
