---
name: dungeon_synth-arrangement
version: 1
kind: genre
tags: [dungeon_synth, ambient, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 40-110; set the song key (suggested: E minor (Dorian/Phrygian)).
  - Mix: clipped_samples == 0, LUFS -18..-14, band order lowmid>mid>low.
  - ROMPLER CHOIR BED is non-negotiable: cheap 90s ROMpler synth-choir and string patches as the main voices — the lo-fi fantasy orchestra
  - FIFTH OSTINATO RITUAL is non-negotiable: a 2-4 bar open-fifth ostinato (organ/harpsichord/harp) cycling under a chant-like modal melody — processional, unhurried
  - DUNGEON MODAL CHANT is non-negotiable: Aeolian/Dorian/Phrygian stepwise melodies, narrow range, repeated like a liturgy — melody as ritual not hook
---
# Dungeon_Synth arrangement (graph-compiled)

Dungeon_Synth is a child of **ambient** — its groove laws apply unless overridden below.

## The pocket — crypt_ritual
Dungeon synth (~72 BPM, processional, often drumless): a 2-4 bar open-FIFTH ostinato (organ/harpsichord/harp) cycles under a chant-like stepwise Aeolian/Dorian melody (ROMpler choir/strings); timpani strikes beat 1 (answer on 3) when percussion exists at all — a backbeat is FORBIDDEN; tape-hiss patina, dark low-passed master.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rompler choir bed** (w1.0): cheap 90s ROMpler synth-choir and string patches as the main voices — the lo-fi fantasy orchestra *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **fifth ostinato ritual** (w0.92): a 2-4 bar open-fifth ostinato (organ/harpsichord/harp) cycling under a chant-like modal melody — processional, unhurried *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **dungeon modal chant** (w0.84): Aeolian/Dorian/Phrygian stepwise melodies, narrow range, repeated like a liturgy — melody as ritual not hook *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **timpani processional** (w0.76): percussion only as ritual punctuation: timpani/tom on beat 1 (answer on 3) or NOTHING — a backbeat is forbidden *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **tape hiss patina** (w0.68): deliberate lo-fi: tape hiss bed, wow/flutter, dark low-passed master — the cassette-in-a-crypt aesthetic *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from ambient
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- evolving pads: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
- huge space: bus reverb at maximum size, generous sends — the room is the instrument
- slow filter drift: cutoff automation over 16+ bars, barely perceptible motion
- pentatonic bells: sparse bell notes (fmbell), pentatonic, let ring
- vst fx presets: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
- two chord vamp: two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient)
- cadence plagal IV i: plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth
- trust innate brightness: don't buy top-end per track: a slight Baxandall high shelf on ONE important bus, leave the rest alone — material is usually brighter than fear suggests; per-track brightening stacks into harshness [EQ16]
- chance operations: probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive
- mid side width control: width is DYNAMIC, not a static knob: compressing/boosting the MID makes loud center sounds read wider by contrast; side-only processing adds air that vanishes in mono (acceptable IF it only sweetens the stereo image) — treat mid and side as two mixes [mid/side processing]
- width by arrangement: the widest mixes earn it in the WRITE, not the widener: hard-pan doubled parts (two takes L/R), spread a stereo pad wide UNDER a centered lead, keep the focal element (lead/vocal/kick) center — width is contrast, and a wall of wide reads as narrow [arrangement-first width]

## Sound recipes (this palette, these moves)
- **crypt bed**: ROMpler choir = vox_pad + strings via pad_motion; organ = hammond_organ dark; harpsichord-ish = pluck2/harp arpeggios; timpani for the processional strike; a HISS bed (very quiet filtered noise track) + dark master fx_filter ~6-8kHz = the cassette patina; never loud, never bright

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-14, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
