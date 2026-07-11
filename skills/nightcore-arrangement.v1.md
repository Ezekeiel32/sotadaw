---
name: nightcore-arrangement
version: 1
kind: genre
tags: [nightcore, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 160-180; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order lowmid>low>mid.
  - NIGHTCORE LIFT is non-negotiable: nightcore: pitch+tempo the whole piece UP 15-25% — vocals go bright, energy goes sugar; the TRANSFORM is the genre (warp: lower sourceBpm relative to song bpm)
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - TOPLINE FIRST is non-negotiable: pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses
---
# Nightcore arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **nightcore lift** (w0.95): nightcore: pitch+tempo the whole piece UP 15-25% — vocals go bright, energy goes sugar; the TRANSFORM is the genre (warp: lower sourceBpm relative to song bpm) *(curated:claude/2026-07-03-w12)*
- **four on floor** (w0.7): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **topline first** (w0.7): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **supersaw pads** (w0.6): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
