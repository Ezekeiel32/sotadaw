---
name: gnawa-arrangement
version: 2
kind: genre
tags: [gnawa, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-100; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - GNAWA LOOP is non-negotiable: gnawa: guembri bass ostinato (pentatonic 2-bar loop, hypnotic), qraqeb iron clatter on the 8ths, call-response chant — trance through repetition at 80-100
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Gnawa arrangement (graph-compiled)

## The pocket — krakeb_shuffle
gnawa loop DNA (wave20) Swing 0.66 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gnawa loop** (w0.95): gnawa: guembri bass ostinato (pentatonic 2-bar loop, hypnotic), qraqeb iron clatter on the 8ths, call-response chant — trance through repetition at 80-100 *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **huge space** (w0.5): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
