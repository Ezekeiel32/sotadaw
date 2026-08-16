---
name: industrial-arrangement
version: 3
kind: genre
tags: [industrial, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-145; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order lowmid>low>mid.
  - MACHINE PERCUSSION is non-negotiable: industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
  - LAYERED SNARE is non-negotiable: sample clap + synth snare body at -12 to -18
---
# Industrial arrangement (graph-compiled)

## The pocket — machine_press
industrial loop DNA (wave18)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **machine percussion** (w0.95): industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read *(curated:claude/2026-07-03-w10)*
- **gain staged saturation** (w0.9): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **layered snare** (w0.6): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*
- **filter build** (w0.5): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
