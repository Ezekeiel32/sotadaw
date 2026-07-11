---
name: afrobeats-arrangement
version: 1
kind: genre
tags: [afrobeats, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 98-110; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -16..-9, band order low>lowmid>mid.
  - LOG DRUM BASS is non-negotiable: melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature
  - TRIPLET PERCS is non-negotiable: 3:2 cross-rhythm percussion over a straight kick — rims/toms/shaker
  - SPARSE KICK is non-negotiable: kick on 1 and ~3.5 only; space carries the bounce
---
# Afrobeats arrangement (graph-compiled)

## The pocket — afro_pocket
sparse kick (1, ~3.5), 3:2 perc lattice, light snare/rim on 3 — bounce from space not density  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **log drum bass** (w1.0): melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature *(curated:claude/2026-07-02)*
- **triplet percs** (w0.92): 3:2 cross-rhythm percussion over a straight kick — rims/toms/shaker *(curated:claude/2026-07-02)*
- **sparse kick** (w0.84): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*
- **call response melody** (w0.76): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **swing 16th** (w0.68): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **afro log**: sub_clean staccato notes (0.2-0.35 beats) walking the pentatonic + light fx_saturate — the log drum

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
