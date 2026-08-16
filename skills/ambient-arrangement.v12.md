---
name: ambient-arrangement
version: 12
kind: genre
tags: [ambient, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-85; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -26..-14, band order lowmid>mid>low.
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
---
# Ambient arrangement (graph-compiled)

## The pocket — ambient_flow
no grid tyranny: overlapping 8-16 beat pads, sparse bells, events BREATHE; drums optional/ghosted  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +2 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **evolving pads** (w1.0): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **huge space** (w0.92): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **vst fx presets** (w0.92): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **slow filter drift** (w0.84): cutoff automation over 16+ bars, barely perceptible motion *(curated:claude/2026-07-02)*
- **pentatonic bells** (w0.76): sparse bell notes (fmbell), pentatonic, let ring *(curated:claude/2026-07-02)*
- **mid side width control** (w0.7): width is DYNAMIC, not a static knob: compressing/boosting the MID makes loud center sounds read wider by contrast; side-only processing adds air that vanishes in mono (acceptable IF it only sweetens the stereo image) — treat mid and side as two mixes [mid/side processing] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **send reverb** (w0.68): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **width by arrangement** (w0.65): the widest mixes earn it in the WRITE, not the widener: hard-pan doubled parts (two takes L/R), spread a stereo pad wide UNDER a centered lead, keep the focal element (lead/vocal/kick) center — width is contrast, and a wall of wide reads as narrow [arrangement-first width] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **two chord vamp** (w0.6): two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **cadence plagal IV i** (w0.6): plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **chance operations** (w0.6): probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive *(engine-witnessed weighted follow actions (firing 49: trackNext w0.7 +1 more)*
- **trust innate brightness** (w0.5): don't buy top-end per track: a slight Baxandall high shelf on ONE important bus, leave the rest alone — material is usually brighter than fear suggests; per-track brightening stacks into harshness [EQ16] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*

## Sound recipes (this palette, these moves)
- **ambient wash**: pad_motion long notes through TWO reverb buses (one dark size 8, one bright size 4)
- **mallet marimba**: faust marimba: struck bar (fundamental + ~4x shine partial + thump), no sustain — kuduro/cinematic/ambient mallets; fast low-vel repeats = rolls
- **gliss harp**: faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb
- **pad motion zones**: pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth 0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = motion 0.6 + drift 0.3; automate depth for evolving intros.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -26..-14, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
