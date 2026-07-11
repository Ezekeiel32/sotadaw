---
name: wave-arrangement
version: 1
kind: genre
tags: [wave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-145; set the song key (suggested: F# minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - WAVE HYBRID BASS is non-negotiable: the wave signature: a hybrid reese/808 bass that SLIDES between melody notes — the bass IS the lead, dark and vocal-like, over lush pads
  - ETHEREAL PAD WASH is non-negotiable: huge detuned atmospheric pads washing behind everything — melancholy club euphoria (wave/hardwave family)
  - TRIPLET HAT ROLL is non-negotiable: trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM
---
# Wave arrangement (graph-compiled)

## The pocket — wave_glide
Wave (~138 BPM, half-time): snare on 3; sparse kick (1, and-of-3); the hybrid reese/808 bass SLIDES between melody notes — the bass IS the lead, dark and vocal-like; lush detuned pads wash behind; light triplet hat details; melancholy club euphoria. (hardwave in the graph is its harder child — edge added.)  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **wave hybrid bass** (w1.0): the wave signature: a hybrid reese/808 bass that SLIDES between melody notes — the bass IS the lead, dark and vocal-like, over lush pads *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **ethereal pad wash** (w0.92): huge detuned atmospheric pads washing behind everything — melancholy club euphoria (wave/hardwave family) *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **triplet hat roll** (w0.84): trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **sidechain menace** (w0.76): audible sidechain pump on pads/bass to a four-on-the-floor kick — breathing dread *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Sound recipes (this palette, these moves)
- **wave rig**: the hybrid bass = reese + sub_clean gliding (portamento slides between melody notes — it IS the lead); pad_motion + vox_pad huge detuned washes; soft snare 3; fx_pump gentle; melancholy, wide, deep

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
