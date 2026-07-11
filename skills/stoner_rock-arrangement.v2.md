---
name: stoner_rock-arrangement
version: 2
kind: genre
tags: [stoner_rock, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-120; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order lowmid>low>mid.
  - DOWNTUNED GROOVE is non-negotiable: a syncopated downtuned power-chord riff with air between the hits — the space between IS the groove (stoner)
  - FUZZ WALL is non-negotiable: stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom)
  - PENTATONIC MINOR RIFF is non-negotiable: a minor-pentatonic (root-b3-4-5-b7) bluesy riff — the desert/grunge/doom lick
---
# Stoner_Rock arrangement (graph-compiled)

Stoner_Rock is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — desert_groove
The downtuned fuzz groove riff (~90 BPM, 4/4, straight-to-slightly-behind ~53%): a syncopated root-fifth power-chord figure on the low strings (Drop C/D), kick locks the riff hits, snare cracks 2&4, riff cycles every 1-2 bars ending on a ringing sustained chord. Swing 0.53 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **downtuned groove** (w1.0): a syncopated downtuned power-chord riff with air between the hits — the space between IS the groove (stoner) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **fuzz wall** (w0.92): stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pentatonic minor riff** (w0.84): a minor-pentatonic (root-b3-4-5-b7) bluesy riff — the desert/grunge/doom lick *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **syncopated power chord** (w0.76): a power-chord riff built on space and sustain, hits placed OFF the grid (stoner) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hypnotic repetition** (w0.68): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **wah lead sweep** (w0.6): a Cry Baby wah realized as a filter-automation sweep on the solo (stoner) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **bluesy bend** (w0.52): slow pentatonic/blues string bends and heavy vibrato — the Southern lean (doom, stoner) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

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
- **desert fuzz**: faust fuzz_guitar downtuned + thick: high drive, sub-octave girth, low-mid wall; bass_warm doubles near-lead; wah = an fx_djfilter/fx_filter sweep automated on leads; analog-warm, not brickwalled.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
