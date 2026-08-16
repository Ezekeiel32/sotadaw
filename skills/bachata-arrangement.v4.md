---
name: bachata-arrangement
version: 4
kind: genre
tags: [bachata, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-135; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>low>mid.
  - BACHATA REQUINTO is non-negotiable: bachata: requinto lead arpeggios answer the vocal line, guira drives 16ths, bongo rolls into every 4th beat, bass syncopates 1-and-3-and — romance at 120-135
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - GHOST NOTES is non-negotiable: low-velocity (0.25-0.45) off-grid hits between main hits
---
# Bachata arrangement (graph-compiled)

## The pocket — bachata_bongo
bachata loop DNA (wave18)  *(source: curated:claude/2026-07-04 + grid:curated (wave18) + wave24 leads+fills + wave36 canon harmony +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **bachata requinto** (w0.95): bachata: requinto lead arpeggios answer the vocal line, guira drives 16ths, bongo rolls into every 4th beat, bass syncopates 1-and-3-and — romance at 120-135 *(curated:claude/2026-07-03-w9)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **ghost notes** (w0.5): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
