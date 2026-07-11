---
name: surf_rock-arrangement
version: 1
kind: genre
tags: [surf_rock, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-180; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order mid>lowmid>low.
  - TREMOLO PICKING is non-negotiable: continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing)
  - SPRING REVERB WASH is non-negotiable: the drippy, bright, LONG outboard spring-tank splash — surf's actual fingerprint (distinct from plate/hall)
  - PHRYGIAN DOMINANT RUN is non-negotiable: a hijaz / double-harmonic exotic melodic run (the Misirlou lick) tremolo-picked on a low string (surf)
---
# Surf_Rock arrangement (graph-compiled)

Surf_Rock is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — surf_beat
Tremolo-picked hijaz lead over the driving surf beat (~160 BPM, 4/4 straight): kick 1&3, snare 2&4, 8th ride, bass drives root 8ths; the lead is a continuous 16th tremolo line drenched in a long bright spring tank.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tremolo picking** (w1.0): continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **spring reverb wash** (w0.92): the drippy, bright, LONG outboard spring-tank splash — surf's actual fingerprint (distinct from plate/hall) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **phrygian dominant run** (w0.84): a hijaz / double-harmonic exotic melodic run (the Misirlou lick) tremolo-picked on a low string (surf) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **whammy dive** (w0.76): a vibrato-arm downward pitch-bend — a pitch-automation dip on the lead (surf) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **bridge pickup twang** (w0.68): a bright, close-to-the-bridge single-coil pick attack — maximum twang (surf) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **surf beat tom roll** (w0.6): the tom-forward surf drum beat with rimshots and rolls (Wipe Out) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pentatonic minor riff** (w0.52): a minor-pentatonic (root-b3-4-5-b7) bluesy riff — the desert/grunge/doom lick *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

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
- **surf twang**: bright single-coil pluck, tremolo-picked, into a LONG bright spring-tank fx_reverb + short slap fx_delay; light amp-breakup fx_saturate only, NEVER fuzz

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
