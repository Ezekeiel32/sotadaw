---
name: ukgarage-arrangement
version: 1
kind: genre
tags: [ukgarage, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-135; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -16..-9, band order low>lowmid>mid.
  - TWO STEP KICK is non-negotiable: NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove
  - SHUFFLE SWING is non-negotiable: hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt
  - CHOPPED CHORDS is non-negotiable: short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm
---
# Ukgarage arrangement (graph-compiled)

Ukgarage is a child of **house** — its groove laws apply unless overridden below.

## The pocket — ukg_2step
kick 1 + ~2.75 (no four-floor), snare 2&4 crisp, shuffled hats with ghosts in the gaps  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **two step kick** (w1.0): NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove *(curated:claude/2026-07-02)*
- **shuffle swing** (w0.92): hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt *(curated:claude/2026-07-02)*
- **chopped chords** (w0.84): short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm *(curated:claude/2026-07-02)*
- **vocal chops** (w0.76): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **send reverb** (w0.68): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **ghost notes** (w0.6): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- offbeat bass: bass hits on the 8th between kicks

## Sound recipes (this palette, these moves)
- **ukg stab**: epiano or keys_dark short m7 stab, fx_filter cutoff ~2500 warm, fx_delay subtle
- **ukg sub**: sub_clean following the kick holes, one octave below the stab root

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
