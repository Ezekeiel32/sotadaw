---
name: happy_hardcore-arrangement
version: 2
kind: genre
tags: [happy_hardcore, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 165-180; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order low>mid>lowmid.
  - HARDCORE STOMP is non-negotiable: happy hardcore: 165-180 four-floor stomp + offbeat bass stabs + pitched-up vocal hooks; rave-piano half-time breakdown, then slam back to double-time
  - PIANO HOUSE STAB is non-negotiable: rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast
  - SUPERSAW PADS is non-negotiable: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
---
# Happy_Hardcore arrangement (graph-compiled)

## The pocket — happy_bounce
happy_hardcore loop DNA (wave15)  *(source: curated:claude/2026-07-04 + grid:curated (wave15 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **hardcore stomp** (w0.95): happy hardcore: 165-180 four-floor stomp + offbeat bass stabs + pitched-up vocal hooks; rave-piano half-time breakdown, then slam back to double-time *(curated:claude/2026-07-03-w8)*
- **piano house stab** (w0.75): rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast *(curated:claude/2026-07-03-w6)*
- **supersaw pads** (w0.7): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **pitch vox hyper** (w0.6): hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen *(curated:claude/2026-07-03)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
