---
name: punk-arrangement
version: 1
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

## Techniques (weight order — the top ones DEFINE the genre)
- **dbeat energy** (w0.95): punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30 *(curated:claude/2026-07-03-w9)*
- **power chords** (w0.9): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*
- **gain staged saturation** (w0.7): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
