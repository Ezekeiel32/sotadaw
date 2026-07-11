---
name: corridos_tumbados-arrangement
version: 3
kind: genre
tags: [corridos_tumbados, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-125; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order lowmid>low>mid.
  - REQUINTO TRAP is non-negotiable: corridos tumbados: requinto/nylon guitar arpeggios + BRASS BASS (tuba/trombone walking lines) + trap swagger; often 6/8 or 3/4 waltz feel — grid the guitars tight, let vocals lag
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Corridos_Tumbados arrangement (graph-compiled)

## The pocket — tuba_sway
corridos_tumbados loop DNA (wave20) Swing 0.54 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete))*

## Techniques (weight order — the top ones DEFINE the genre)
- **requinto trap** (w0.95): corridos tumbados: requinto/nylon guitar arpeggios + BRASS BASS (tuba/trombone walking lines) + trap swagger; often 6/8 or 3/4 waltz feel — grid the guitars tight, let vocals lag *(curated:claude/2026-07-03-w8)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **behind beat snare** (w0.5): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
