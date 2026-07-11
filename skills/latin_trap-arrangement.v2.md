---
name: latin_trap-arrangement
version: 2
kind: genre
tags: [latin_trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-100; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - LATIN TRAP BOUNCE is non-negotiable: latin trap: dembow lilt underneath trap 808 slides and hats — the drums swing like reggaeton but hit like trap; melodic minor toplines
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Latin_Trap arrangement (graph-compiled)

## The pocket — latintrap_lilt
dembow lean under trap slide Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **latin trap bounce** (w0.95): latin trap: dembow lilt underneath trap 808 slides and hats — the drums swing like reggaeton but hit like trap; melodic minor toplines *(curated:claude/2026-07-03-w10)*
- **sliding 808** (w0.85): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **hat rolls** (w0.7): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **dembow rhythm** (w0.7): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
