---
name: forro-arrangement
version: 3
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

## The pocket — baiao_zabumba
forro loop DNA (wave20)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **forro gallop** (w0.95): forró: zabumba boom on the 1 + slap on the and, triangle sizzling straight 8ths, ACCORDION leads the melody — 2/4 gallop at 90-110 *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **ghost notes** (w0.5): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
