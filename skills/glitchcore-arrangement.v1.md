---
name: glitchcore-arrangement
version: 1
kind: genre
tags: [glitchcore, hyperpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-180; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order mid>low>lowmid.
  - STUTTER CHOP LEAD is non-negotiable: glitchcore law: the pitched vocal chop is STUTTERED into the lead instrument — constant micro-edit retriggers as melody, not occasional glitches
  - SENSORY OVERLOAD STACK is non-negotiable: dense bright synth stacks + breakneck switch-ups every 2-4 bars — maximal density as the aesthetic (glitchcore/dariacore kinship)
  - GLITCH INTERRUPTION is non-negotiable: THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop
---
# Glitchcore arrangement (graph-compiled)

Glitchcore is a child of **hyperpop** — its groove laws apply unless overridden below.

## The pocket — stutter_engine
Glitchcore (~165 BPM): breakneck trap grid (kick 1 + slides, clap 2&4, 16th hats with roll bursts); the pitched vocal chop is STUTTERED into the lead — constant micro-edit retriggers AS melody (write repeated 16th/32nd note clusters); dense bright synth stacks; switch-ups every 2-4 bars; hard-cut ending.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **stutter chop lead** (w1.0): glitchcore law: the pitched vocal chop is STUTTERED into the lead instrument — constant micro-edit retriggers as melody, not occasional glitches *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **sensory overload stack** (w0.92): dense bright synth stacks + breakneck switch-ups every 2-4 bars — maximal density as the aesthetic (glitchcore/dariacore kinship) *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **glitch interruption** (w0.84): THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **distorted gummy 808** (w0.76): the 808 overdriven until it 'overtakes the song' — gummy, elastic, gliding 4ths/5ths; digicore's low end IS distortion *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **hard cut ending** (w0.68): songs end on a HARD CUT (no fade, no outro) — 1:45-2:30 total, texture-flips not harmony-changes between sections *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from hyperpop
- width bloom: fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- supersaw uplift: trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout
- pitch vox hyper: hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen

## Sound recipes (this palette, these moves)
- **stutter rig**: stutter lead = chiptune_pulse/supersaw repeated micro-notes (the retrigger written as note clusters) + fx_crush hard (bits 6-10); distorted 808; fx_stutter-style edits = arrangement law (repeat last-16th clusters); louder and busier than digicore — overload IS the aesthetic

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order mid>low>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
