---
name: soul-arrangement
version: 3
kind: genre
tags: [soul, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-95; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -16..-10, band order lowmid>low>mid.
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Soul arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **walking bass** (w0.8): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **behind beat snare** (w0.75): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **horn stabs** (w0.6): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns
- **solina strings**: faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)
- **motor vibes**: faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
