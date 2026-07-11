---
name: forro-arrangement
version: 1
kind: genre
tags: [forro, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-110; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>low>mid.
  - FORRO GALLOP is non-negotiable: forró: zabumba boom on the 1 + slap on the and, triangle sizzling straight 8ths, ACCORDION leads the melody — 2/4 gallop at 90-110
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - GHOST NOTES is non-negotiable: low-velocity (0.25-0.45) off-grid hits between main hits
---
# Forro arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **forro gallop** (w0.95): forró: zabumba boom on the 1 + slap on the and, triangle sizzling straight 8ths, ACCORDION leads the melody — 2/4 gallop at 90-110 *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **ghost notes** (w0.5): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
