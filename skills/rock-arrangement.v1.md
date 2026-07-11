---
name: rock-arrangement
version: 1
kind: genre
tags: [rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-150; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order lowmid>low>mid.
  - POWER CHORDS is non-negotiable: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
  - LAYERED SNARE is non-negotiable: sample clap + synth snare body at -12 to -18
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
---
# Rock arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **power chords** (w0.95): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*
- **layered snare** (w0.7): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*
- **gain staged saturation** (w0.7): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **huge space** (w0.5): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
