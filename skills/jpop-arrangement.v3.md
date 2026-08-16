---
name: jpop-arrangement
version: 3
kind: genre
tags: [jpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-160; set the song key (suggested: E major).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order lowmid>low>mid.
  - JPOP MODULATION is non-negotiable: jpop: dense borrowed-from-jazz chord motion under a bright topline, and the LAST-CHORUS KEY CHANGE (+1 semitone) — earnestness is the aesthetic
  - TOPLINE FIRST is non-negotiable: pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
---
# Jpop arrangement (graph-compiled)

## The pocket — jpop_drive
jpop loop DNA (wave19)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **jpop modulation** (w0.9): jpop: dense borrowed-from-jazz chord motion under a bright topline, and the LAST-CHORUS KEY CHANGE (+1 semitone) — earnestness is the aesthetic *(curated:claude/2026-07-03-w10)*
- **topline first** (w0.85): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **m7 chords** (w0.7): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **prechorus lift** (w0.7): the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1 *(curated:claude/2026-07-03-w9)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
