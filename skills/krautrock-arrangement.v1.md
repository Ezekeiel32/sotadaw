---
name: krautrock-arrangement
version: 1
kind: genre
tags: [krautrock, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-150; set the song key (suggested: A major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - MOTORIK PULSE is non-negotiable: the MOTORIK beat: kick on the downbeat (often 1 & 3), snare backbeat on 2 & 4, unbroken even 8th-notes on the hats, and NO fills — linear 'autobahn' propulsion (krautrock)
  - HARMONIC STASIS is non-negotiable: one or two chords held as a drone; the tension comes from repetition, not changes (krautrock)
  - HYPNOTIC REPETITION is non-negotiable: an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom)
---
# Krautrock arrangement (graph-compiled)

Krautrock is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — motorik_beat
THE MOTORIK BEAT (~140 BPM, 4/4, 0% swing): kick on 1 (&3), snare on 2&4, unbroken even-8th hats, NO fills; bass = constant 8th root pedal; one droning chord held. Every bar identical — the variation lives only in slowly-morphing texture on top.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **motorik pulse** (w1.0): the MOTORIK beat: kick on the downbeat (often 1 & 3), snare backbeat on 2 & 4, unbroken even 8th-notes on the hats, and NO fills — linear 'autobahn' propulsion (krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **harmonic stasis** (w0.92): one or two chords held as a drone; the tension comes from repetition, not changes (krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hypnotic repetition** (w0.84): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **analog sequencer arp** (w0.76): a locked analog-synth arpeggio riding the steady pulse (krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **additive arrangement** (w0.68): the piece evolves by LAYERS entering and exiting over long spans, not by verse/chorus (krautrock, post-metal, spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tape echo space** (w0.6): tape-echo, phasing and spatial treatment used AS an instrument (Conny Plank; krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pedal drone** (w0.52): a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from rock
- layered snare: sample clap + synth snare body at -12 to -18
- huge space: bus reverb at maximum size, generous sends — the room is the instrument
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- quick change blues: 12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness installed at the very top of the form; the single most common blues alteration [Popular music: blues harmony]
- blues turnaround: bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony]
- sixteen bar blues: four 4-bar phrases — tonic stated twice, then subdominant, then dominant phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock [Popular music: blues harmony]
- blues dominant color: the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony]
- mud zone 200 400: most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16]
- parallel detail pump: high ratio + fast attack AND release, blended low under dry: the original transients stay in charge while low-level detail and tone pump upward — dynamic-range control that never squashes the hit [PARA]
- strophic form: AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes
- refrain hook: a recurring lyric+melodic motive INSIDE the strophe — usually carrying the TITLE — is the refrain: the hook mechanism of strophic songs before choruses existed ('Faded Love'); write it once, let every strophe land it

## Sound recipes (this palette, these moves)
- **motorik drone**: a held saw drone + a locked analog_sequencer_arp; tape-echo fx_delay, a SLOW automated fx_filter LP sweep = 'the evolution'; drums dead-straight, no fills; optional slow tempoMap accelerando as the build

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
