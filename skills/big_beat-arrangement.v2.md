---
name: big_beat-arrangement
version: 2
kind: genre
tags: [big_beat, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-120; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - BIG BEAT BREAK is non-negotiable: big beat: a LOUD compressed funk break at 100-120 (half rave tempo) + acid 303 + rock-energy stabs; the break is the lead instrument — distort it, filter it, drop it out for the build
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
  - ACID SQUELCH LEAD is non-negotiable: resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice
---
# Big_Beat arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **big beat break** (w0.95): big beat: a LOUD compressed funk break at 100-120 (half rave tempo) + acid 303 + rock-energy stabs; the break is the lead instrument — distort it, filter it, drop it out for the build *(curated:claude/2026-07-03-w8)*
- **gain staged saturation** (w0.8): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **acid squelch lead** (w0.7): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- **filter build** (w0.6): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
