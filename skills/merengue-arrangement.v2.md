---
name: merengue-arrangement
version: 2
kind: genre
tags: [merengue, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order lowmid>mid>low.
  - MERENGUE DRIVE is non-negotiable: merengue: tambora roll-slap pattern + guira SIXTEENTH sprint at 130-160 2/4 feel, saxophone jaleo riffs in unison octaves — relentless forward drive, no half-time ever
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Merengue arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **merengue drive** (w0.95): merengue: tambora roll-slap pattern + guira SIXTEENTH sprint at 130-160 2/4 feel, saxophone jaleo riffs in unison octaves — relentless forward drive, no half-time ever *(curated:claude/2026-07-03-w9)*
- **horn stabs** (w0.8): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
