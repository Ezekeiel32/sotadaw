---
name: mariachi-arrangement
version: 3
kind: genre
tags: [mariachi, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-110; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - MARIACHI SON is non-negotiable: mariachi son: the 6/8-vs-3/4 HEMIOLA, vihuela chop + guitarrón bass, trumpets in duet thirds — write the hemiola as alternating bar accents
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Mariachi arrangement (graph-compiled)

## The pocket — ranchera_walk
mariachi loop DNA (wave20)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **mariachi son** (w0.95): mariachi son: the 6/8-vs-3/4 HEMIOLA, vihuela chop + guitarrón bass, trumpets in duet thirds — write the hemiola as alternating bar accents *(curated:claude/2026-07-03-w13)*
- **horn stabs** (w0.8): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
