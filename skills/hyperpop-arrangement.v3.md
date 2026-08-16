---
name: hyperpop-arrangement
version: 3
kind: genre
tags: [hyperpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-170; set the song key (suggested: A major).
  - Mix: clipped_samples == 0, LUFS -10..-6, band order lowmid~mid.
  - PITCH VOX HYPER is non-negotiable: hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen
  - WIDTH BLOOM is non-negotiable: fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
---
# Hyperpop arrangement (graph-compiled)

## The pocket — hyper_burst
bright saturated everything, vocal chips lead, sudden drops to silence, extreme width on hooks  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **pitch vox hyper** (w1.0): hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen *(curated:claude/2026-07-03)*
- **width bloom** (w0.93): fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end *(skill:automation-motion@v1)*
- **gain staged saturation** (w0.86): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **supersaw uplift** (w0.79): trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout *(curated:claude/2026-07-03)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-6, band order lowmid~mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
