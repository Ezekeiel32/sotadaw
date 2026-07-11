---
name: grunge-arrangement
version: 1
kind: genre
tags: [grunge, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-160; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order lowmid>low>mid.
  - QUIET LOUD DYNAMICS is non-negotiable: the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo)
  - FUZZ WALL is non-negotiable: stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom)
  - DROP D POWERCHORD is non-negotiable: one-finger low-D (drop-D) power-chord riffing (grunge, metalcore)
---
# Grunge arrangement (graph-compiled)

Grunge is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — quiet_loud
Quiet clean verse -> loud fuzz chorus (~117 BPM, 4/4 straight). VERSE: clean/lightly-driven guitar, restrained backbeat, bass carries motion. CHORUS: fuzz power chords on the downbeats, crash-forward drums, doubled panned guitars. The defining event is the dynamic JUMP (a gain/saturation automation step), not one note grid.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **quiet loud dynamics** (w1.0): the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **fuzz wall** (w0.92): stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **drop d powerchord** (w0.84): one-finger low-D (drop-D) power-chord riffing (grunge, metalcore) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pentatonic minor riff** (w0.76): a minor-pentatonic (root-b3-4-5-b7) bluesy riff — the desert/grunge/doom lick *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **eb standard detune** (w0.68): tune a half-step down (Eb standard) for thickness and weight (grunge) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **vocal harmony dread** (w0.6): stacked minor two-part vocal harmonies (Layne Staley + Jerry Cantrell) — dread as melody (grunge) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **palm mute chug** (w0.52): metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither *(curated:claude/2026-07-03-w9)*

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
- **grunge fuzz**: guitar_grit into HEAVY fx_saturate (Big-Muff character) + mid-focused fx_filter for the chorus; near-BYPASS saturation for the clean verse -- the verse->chorus GAIN AUTOMATION (curve <0, early-jump) is the song. Preserve dynamics at master (DR11-12 feel, NOT a -8 brickwall).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
