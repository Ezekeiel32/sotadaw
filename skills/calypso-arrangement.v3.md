---
name: calypso-arrangement
version: 3
kind: genre
tags: [calypso, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-120; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>low>mid.
  - CALYPSO LILT is non-negotiable: calypso: lilting boom-chick at 100-120, steel pan + brass ANSWER the vocal line, storytelling verse structure — wit over aggression
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
---
# Calypso arrangement (graph-compiled)

## The pocket — calypso_bell
calypso loop DNA (wave20)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **calypso lilt** (w0.95): calypso: lilting boom-chick at 100-120, steel pan + brass ANSWER the vocal line, storytelling verse structure — wit over aggression *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **horn stabs** (w0.7): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **pan lead**: faust steel_pan: struck pan w/ octave halo + ping — soca/calypso riffs and leads; roll = fast low-vel repeats

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
