---
name: uk_funky-arrangement
version: 1
kind: genre
tags: [uk_funky, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-132; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - TRIBAL KICKS is non-negotiable: uk funky: the drums are MELODIC — syncopated toms answer the kick (soca/broken-beat DNA), skippy snares, NOT four-on-floor; percussion carries the hook
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Uk_Funky arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **tribal kicks** (w0.95): uk funky: the drums are MELODIC — syncopated toms answer the kick (soca/broken-beat DNA), skippy snares, NOT four-on-floor; percussion carries the hook *(curated:claude/2026-07-03-w8)*
- **vocal chops** (w0.7): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **offbeat bass** (w0.6): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
