---
name: ska-arrangement
version: 2
kind: genre
tags: [ska, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-145; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - SKANK UPSTROKE is non-negotiable: ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Ska arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **skank upstroke** (w0.95): ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse *(curated:claude/2026-07-03-w7)*
- **horn stabs** (w0.85): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **walking bass** (w0.8): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **four floor disco** (w0.5): disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
