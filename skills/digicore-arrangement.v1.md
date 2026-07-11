---
name: digicore-arrangement
version: 1
kind: genre
tags: [digicore, hyperpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-170; set the song key (suggested: A minor (emo axis)).
  - Mix: clipped_samples == 0, LUFS -9..-7, band order low>lowmid>mid.
  - GLITCH INTERRUPTION is non-negotiable: THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop
  - EMO AXIS LOOP is non-negotiable: the Aeolian emo axis i-VI-III-VII cycling under everything — pop-punk chords in trap clothes
  - DISTORTED GUMMY 808 is non-negotiable: the 808 overdriven until it 'overtakes the song' — gummy, elastic, gliding 4ths/5ths; digicore's low end IS distortion
---
# Digicore arrangement (graph-compiled)

Digicore is a child of **hyperpop** — its groove laws apply unless overridden below.

## The pocket — glitch_emo
Digicore (~145 BPM trap grid): kick on 1 + syncopated hits following 808 slides (slots 0,6,15); clap hard on 2&4 with 1/32 rolls into them; running 16th hats; the emo axis i-VI-III-VII cycles under a nightcore-pitched topline; EVERY 2-4 bars a GLITCH INTERRUPTION — stutter-retrigger the last 16th, reverse a tail in, or hard-gate a 1/4-beat silence. End on a HARD CUT.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **glitch interruption** (w1.0): THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **emo axis loop** (w0.92): the Aeolian emo axis i-VI-III-VII cycling under everything — pop-punk chords in trap clothes *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **distorted gummy 808** (w0.84): the 808 overdriven until it 'overtakes the song' — gummy, elastic, gliding 4ths/5ths; digicore's low end IS distortion *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **nightcore pitch vocal** (w0.76): toplines pitched UP +3..+7 st (or an octave) — fragile, anonymized, hyper-emotive; write in a comfortable key and shift *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **hard cut ending** (w0.68): songs end on a HARD CUT (no fade, no outro) — 1:45-2:30 total, texture-flips not harmony-changes between sections *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from hyperpop
- width bloom: fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- supersaw uplift: trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout
- pitch vox hyper: hyperpop: chipmunk vocal chops (choir kit +12st equivalents), bitcrush-bright synths, extreme widen

## Sound recipes (this palette, these moves)
- **glitch emo rig**: supersaw wash + guitar_grit lo-fi loops over a DISTORTED gummy 808 (kick_808 + fx_saturate heavy); nightcore lead = formant_vox/supersaw pitched HIGH; glitches = arrangement-level stutter (repeat the last 16th-note slice as notes) + fx_trim hard gates; loud but soft-clipped

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
