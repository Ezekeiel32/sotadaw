---
name: highlife-arrangement
version: 3
kind: genre
tags: [highlife, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-120; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -15..-10, band order lowmid>mid>low.
  - HIGHLIFE GUITAR is non-negotiable: interlocking palm-wine guitar lines (2-finger arpeggios) over a gentle 4/4 — bright, clean, no distortion
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
---
# Highlife arrangement (graph-compiled)

## The pocket — highlife_bell
highlife loop DNA (wave16)  *(source: curated:claude/2026-07-04 + grid:curated (wave16 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **highlife guitar** (w0.95): interlocking palm-wine guitar lines (2-finger arpeggios) over a gentle 4/4 — bright, clean, no distortion *(curated:claude/2026-07-03-w5)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **horn stabs** (w0.6): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **clave 23** (w0.6): the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **tine kalimba**: faust kalimba: plucked tine (near-sine + inharmonic sparkle + thumb click) — lofi/afro signature; arpeggiate gently, let notes ring

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
