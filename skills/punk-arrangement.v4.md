---
name: punk-arrangement
version: 4
kind: genre
tags: [punk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 160-190; set the song key (suggested: A major).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order lowmid>mid>low.
  - DBEAT ENERGY is non-negotiable: punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30
  - POWER CHORDS is non-negotiable: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
---
# Punk arrangement (graph-compiled)

## The pocket — punk_dbeat
d-beat gallop, relentless 8th hats  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **dbeat energy** (w0.95): punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30 *(curated:claude/2026-07-03-w9)*
- **power chords** (w0.9): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*
- **gain staged saturation** (w0.7): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
