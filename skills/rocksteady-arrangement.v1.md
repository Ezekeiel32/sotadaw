---
name: rocksteady-arrangement
version: 1
kind: genre
tags: [rocksteady, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-100; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - SKANK UPSTROKE is non-negotiable: ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - ONE DROP is non-negotiable: reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole
---
# Rocksteady arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **skank upstroke** (w0.9): ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse *(curated:claude/2026-07-03-w7)*
- **walking bass** (w0.75): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **one drop** (w0.7): reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole *(curated:claude/2026-07-03-w6)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
