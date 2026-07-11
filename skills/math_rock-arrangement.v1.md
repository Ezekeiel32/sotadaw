---
name: math_rock-arrangement
version: 1
kind: genre
tags: [math_rock, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-170; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order mid>lowmid>low.
  - ODD METER RIFF is non-negotiable: a riff in 5/4, 7/8, 11/8 or 13/8 with additive groupings (e.g. 2+2+3) — the meter IS the hook (math rock)
  - POLYMETER is non-negotiable: a fixed-length melodic cell cycled over a differently-lengthed drum bar so the accents walk and re-sync (math rock)
  - TAPPED ARPEGGIO is non-negotiable: bright, clean two-hand TAPPED arpeggio cascades — every note articulate (math rock, emo)
---
# Math_Rock arrangement (graph-compiled)

Math_Rock is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — odd_meter_cell
The odd-meter cell: 7/8 grouped 2+2+3 (~150 BPM, clean tone). Accents on the group heads (8th-slots 1,3,5); drums lock the 2+2+3 while the bass runs a contrapuntal line -- or flip to POLYMETER (a 4-note guitar cell over the 7/8 bar so the downbeat drifts and re-syncs every 8 bars). [16-slot grid approximates the 4/4 read; encode the true 7/8 in section time-sigs via tempoMap.]  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **odd meter riff** (w1.0): a riff in 5/4, 7/8, 11/8 or 13/8 with additive groupings (e.g. 2+2+3) — the meter IS the hook (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **polymeter** (w0.92): a fixed-length melodic cell cycled over a differently-lengthed drum bar so the accents walk and re-sync (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tapped arpeggio** (w0.84): bright, clean two-hand TAPPED arpeggio cascades — every note articulate (math rock, emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **angular riff** (w0.76): wide-interval, disjunct, stop-start melodic lines (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **start stop dynamics** (w0.68): abrupt full-band CUTS and re-entries as structural seams (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **counterpoint interplay** (w0.6): independent contrapuntal guitar and bass lines rather than root-support (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **unconventional voicing** (w0.52): maj7 / add9 / sus2 recolorings in place of plain triads — one note changes everything (emo, math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **metric modulation** (w0.44): the tempo re-pivots by reinterpreting the note value — a felt gear-change (math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

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
- **clean chime**: bright CLEAN pluck arpeggios, minimal saturation, light fx_delay for tapped cascades + a small fx_reverb; two tracks panned L/R for counterpoint legibility; tempoMap drives the meter/tempo pivots; preserve transient crest at master (do NOT limit hard)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
