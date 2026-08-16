---
name: samba-arrangement
version: 3
kind: genre
tags: [samba, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-110; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - SAMBA BATUCADA is non-negotiable: samba engine: surdo anchors beat 2 (not 1), caixa rides 16ths with accent displacement, tamborim carries the telecoteco cell — layered percussion IS the song
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Samba arrangement (graph-compiled)

## The pocket — surdo_two
samba loop DNA (wave16)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +3 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **samba batucada** (w0.95): samba engine: surdo anchors beat 2 (not 1), caixa rides 16ths with accent displacement, tamborim carries the telecoteco cell — layered percussion IS the song *(curated:claude/2026-07-03-w7)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **walking bass** (w0.5): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **clave 23** (w0.5): the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it *(curated:claude/2026-07-03-w5)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
