---
name: kompa-arrangement
version: 3
kind: genre
tags: [kompa, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-95; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - KOMPA GOUYAD is non-negotiable: kompa's slow-wind groove ~90bpm: tight kick+conga pocket, guitar skank on the offbeat, bass melodic not subby
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Kompa arrangement (graph-compiled)

## The pocket — kompa_gong
kompa loop DNA (wave20)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **kompa gouyad** (w0.95): kompa's slow-wind groove ~90bpm: tight kick+conga pocket, guitar skank on the offbeat, bass melodic not subby *(curated:claude/2026-07-03-w5)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **send reverb** (w0.5): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
