---
name: jazzfusion-arrangement
version: 3
kind: genre
tags: [jazzfusion, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-140; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - GHOST NOTES is non-negotiable: low-velocity (0.25-0.45) off-grid hits between main hits
---
# Jazzfusion arrangement (graph-compiled)

## The pocket — fusion_sixteen
jazzfusion loop DNA (wave19) Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **walking bass** (w0.8): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **ghost notes** (w0.7): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **chopped chords** (w0.5): short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='funk_pocket', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (16th funk: leans forward on the a's, audible ghosts, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
