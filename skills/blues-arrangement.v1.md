---
name: blues-arrangement
version: 1
kind: genre
tags: [blues, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-120; set the song key (suggested: E major).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - TWELVE BAR BLUES is non-negotiable: the 12-bar form is the LAW: I-I-I-I / IV-IV-I-I / V-IV-I-V(turnaround), shuffle triplet feel (swing ~0.66), melody answers itself every 2 bars
  - BLUES BENDS is non-negotiable: melody lives on the blue notes: b3, b5, b7 approached by bend/slide (pitch scoop 30-80ms) — never land ON the major 3rd while the band plays dominant chords
  - SHUFFLE SWING is non-negotiable: hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt
---
# Blues arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **twelve bar blues** (w0.95): the 12-bar form is the LAW: I-I-I-I / IV-IV-I-I / V-IV-I-V(turnaround), shuffle triplet feel (swing ~0.66), melody answers itself every 2 bars *(curated:claude/2026-07-03-w7)*
- **blues bends** (w0.9): melody lives on the blue notes: b3, b5, b7 approached by bend/slide (pitch scoop 30-80ms) — never land ON the major 3rd while the band plays dominant chords *(curated:claude/2026-07-03-w7)*
- **shuffle swing** (w0.8): hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt *(curated:claude/2026-07-02)*
- **ghost notes** (w0.6): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
