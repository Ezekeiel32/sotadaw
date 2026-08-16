---
name: eurobeat-arrangement
version: 2
kind: genre
tags: [eurobeat, italo_disco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-160; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>mid>lowmid.
  - OCTAVE FIFTH BASS DRIVE is non-negotiable: eurobeat engine: synth bass hammering octave/fifth 16ths nonstop under a four-floor kick — faster and busier than Hi-NRG's octave 8ths
  - KEY LIFT CHORUS is non-negotiable: the eurobeat chorus LIFTS — modulate up (often +1 semitone or relative-major jump) at the hook for the para-para surge
  - FOURFLOOR HINRG is non-negotiable: kick 1-2-3-4, clap+snare on 2 & 4, open hat on every off-8th — the relentless 130 BPM engine
---
# Eurobeat arrangement (graph-compiled)

Eurobeat is a child of **italo_disco** — its groove laws apply unless overridden below.

## The pocket — parapara_engine
Eurobeat (~155 BPM): four-floor kick, claps 2&4, open-hat off-8ths; the synth bass HAMMERS octave/fifth 16ths nonstop (busier than Hi-NRG); sax/synth riff hooks answer the verse; the chorus LIFTS a key (+1 st) — the Initial D surge.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **octave fifth bass drive** (w1.0): eurobeat engine: synth bass hammering octave/fifth 16ths nonstop under a four-floor kick — faster and busier than Hi-NRG's octave 8ths *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **key lift chorus** (w0.92): the eurobeat chorus LIFTS — modulate up (often +1 semitone or relative-major jump) at the hook for the para-para surge *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **fourfloor hinrg** (w0.84): kick 1-2-3-4, clap+snare on 2 & 4, open hat on every off-8th — the relentless 130 BPM engine *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **minor arp stab** (w0.76): natural-minor arpeggio stabs and octave lead lines (Prophet/Juno) — energetic, campy, melodramatic *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from italo_disco
- offbeat bass: bass hits on the 8th between kicks
- supersaw pads: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
- gated reverb snare: the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat
- italo arp: italo disco: octave-jump bass 8ths + bright polysynth arps + gated snare at 115-125; romantic minor melodies sung earnestly — drama over cool
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- synth param maps: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
- cadence VI i fall: VI->i fall: subdominant slide home — melancholic loop-closer (trance/dnb/phonk)
- andalusian descent: stepwise minor descent (i-VII-VI-...): the andalusian/lament lineage

## Sound recipes (this palette, these moves)
- **parapara rig**: chip_bass hammering octave/fifth 16ths (write them in); supersaw riff hooks; clap_909; the CHORUS KEY-LIFT is law (sections up a semitone); relentless, campy, joyful

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
