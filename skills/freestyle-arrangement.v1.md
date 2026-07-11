---
name: freestyle-arrangement
version: 1
kind: genre
tags: [freestyle, electro, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-122; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - ELECTRO TOM PERCUSSION is non-negotiable: TR-808 electro-funk percussion: syncopated toms, claves, cowbell and rimshots dancing AROUND the backbeat — the freestyle/electro engine
  - MINOR STAB ARP HOOK is non-negotiable: minor synth-stab hooks + arpeggio runs as the instrumental identity between diva vocal lines (freestyle grammar)
  - DISCO DIVA BELT is non-negotiable: a belted diva vocal riding the top, big reverb, call-and-answer with the synth stabs
---
# Freestyle arrangement (graph-compiled)

Freestyle is a child of **electro** — its groove laws apply unless overridden below.

## The pocket — freestyle_engine
Latin freestyle (~116 BPM): 808 electro-funk percussion — kick syncopated (1, and-of-2, 4), claps 2&4, toms/claves/cowbell dancing around the backbeat; minor synth stabs + arpeggio runs hook between diva vocal lines.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **electro tom percussion** (w1.0): TR-808 electro-funk percussion: syncopated toms, claves, cowbell and rimshots dancing AROUND the backbeat — the freestyle/electro engine *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **minor stab arp hook** (w0.92): minor synth-stab hooks + arpeggio runs as the instrumental identity between diva vocal lines (freestyle grammar) *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **disco diva belt** (w0.84): a belted diva vocal riding the top, big reverb, call-and-answer with the synth stabs *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **linn clap crack** (w0.76): LinnDrum/DMX-era clap+snare stacked on 2 & 4, bone dry or short-gated — the early-80s crack *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from electro
- 808 glide: long overlapping 808 notes walking the scale; tune to key
- cowbell lead: saturated cowbell/bell riff as THE melodic hook, minor pentatonic
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- neon bass: 8th-note bass locked to the kick root, slightly saturated
- electro boogie: Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- synth param maps: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion

## Sound recipes (this palette, these moves)
- **freestyle rig**: kick_808 kit + timpani-pitched electro toms + clave ticks (hat_metal); minor supersaw stabs + chiptune_pulse arps; clap_909 crack; diva topline = the vocal rail; heartbreak in a dance record

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
