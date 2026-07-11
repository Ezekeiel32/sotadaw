---
name: jerseyclub-arrangement
version: 1
kind: genre
tags: [jerseyclub, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 132-142; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - CLUB KICK PATTERN is non-negotiable: THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form
  - BED SQUEAK CHOPS is non-negotiable: chopped vocal/stab on straight 8ths riding the kick pattern
  - TRIPLET BREAK is non-negotiable: bar-4 triplet kick fill (hands-up moment) before the pattern restarts
---
# Jerseyclub arrangement (graph-compiled)

Jerseyclub is a child of **house** — its groove laws apply unless overridden below.

## The pocket — jersey_kicks
the 5-kick bed (1, 1.5, 2.5, 3, 3.5) three bars, triplet fill bar 4, chops on 8ths  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **club kick pattern** (w1.0): THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form *(curated:claude/2026-07-02)*
- **bed squeak chops** (w0.92): chopped vocal/stab on straight 8ths riding the kick pattern *(curated:claude/2026-07-02)*
- **triplet break** (w0.84): bar-4 triplet kick fill (hands-up moment) before the pattern restarts *(curated:claude/2026-07-02)*
- **vocal chops** (w0.76): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **send reverb** (w0.68): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- offbeat bass: bass hits on the 8th between kicks

## Sound recipes (this palette, these moves)
- **jersey chop**: choir kit high key or pluck2 stab on 8ths, fx_reverb small

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
