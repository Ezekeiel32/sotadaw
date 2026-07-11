---
name: berlin_school-arrangement
version: 1
kind: genre
tags: [berlin_school, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-132; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - ANALOG SEQUENCE 16TH is non-negotiable: a locked 16th-note analog-synth sequence (Moog 960-style) is the whole engine — pitched pattern of 8-16 steps looped for minutes, evolving only by filter/gate
  - DELAY FILL SEQUENCE is non-negotiable: sequence programmed note-then-rest so a synced delay fills the gaps — the delay repeats become part of the melodic line, doubling the perceived density
  - EVOLVING TEXTURE is non-negotiable: the 'composition' is a slow morph: layers fade in/out and a filter cutoff opens over minutes; no verse/chorus, the journey is the form
---
# Berlin_School arrangement (graph-compiled)

## The pocket — moog_sequence
Berlin school (~110 BPM, 4/4, often DRUMLESS): a locked 16th-note analog sequence is the whole engine — an 8-16 step pitched pattern (Aeolian, over a tonic pedal drone) looped for minutes, programmed note-then-rest so a synced delay fills the gaps; a Mellotron pad washes slow swells above; the 'composition' is a filter cutoff opening + layers fading over time, NOT verse/chorus. When drums enter they are a simple slow kick.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **analog sequence 16th** (w1.0): a locked 16th-note analog-synth sequence (Moog 960-style) is the whole engine — pitched pattern of 8-16 steps looped for minutes, evolving only by filter/gate *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **delay fill sequence** (w0.92): sequence programmed note-then-rest so a synced delay fills the gaps — the delay repeats become part of the melodic line, doubling the perceived density *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **evolving texture** (w0.84): the 'composition' is a slow morph: layers fade in/out and a filter cutoff opens over minutes; no verse/chorus, the journey is the form *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **sequencer pedal drone** (w0.76): a sustained tonic drone / pedal held under the moving sequence — Aeolian-modal, few or no chord changes, tension from repetition *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **mellotron pad wash** (w0.68): a Mellotron-style tape-choir/strings pad laid over the sequence for warmth and slow harmonic swells (Tangerine Dream) *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **drumless pulse** (w0.6): often NO kit at all — the 16th sequence provides the pulse; when drums enter they are a simple motorik or a slow kick, never busy *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **berlin sequence**: a locked 16th analog sequence (phase_distortion/supersaw/pluck2) through a tape-echo fx_delay (note-then-rest so echoes fill); pad_motion = the Mellotron wash; a held tonic drone; a SLOW automated fx_filter LP sweep = 'the evolution'; drums dead-simple or absent. Optional slow tempoMap drift.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
