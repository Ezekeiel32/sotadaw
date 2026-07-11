---
name: balearic-arrangement
version: 2
kind: genre
tags: [balearic, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-115; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order lowmid>low>mid.
  - BALEARIC GLIDE is non-negotiable: balearic: 95-115 sunset groove — chorused clean guitars/pads, dreamy major-7 harmony, loose percussion; nothing urgent, everything warm
  - MAJ7 GLOSS is non-negotiable: citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Balearic arrangement (graph-compiled)

## The pocket — balearic_lazy
balearic loop DNA (wave20) Swing 0.53 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete))*

## Techniques (weight order — the top ones DEFINE the genre)
- **balearic glide** (w0.95): balearic: 95-115 sunset groove — chorused clean guitars/pads, dreamy major-7 harmony, loose percussion; nothing urgent, everything warm *(curated:claude/2026-07-03-w11)*
- **maj7 gloss** (w0.7): citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ *(curated:claude/2026-07-03)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **four floor disco** (w0.5): disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria *(curated:claude/2026-07-03-w5)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
