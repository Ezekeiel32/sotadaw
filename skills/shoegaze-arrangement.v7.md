---
name: shoegaze-arrangement
version: 7
kind: genre
tags: [shoegaze, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-120; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - WALL OF BLUR is non-negotiable: shoegaze: stack fuzz + reverse-reverb + pitch-glide guitar layers until individual notes blur into a WALL; vocals mixed INTO the wall (a texture, not a lead), tempos slow
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Shoegaze arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **wall of blur** (w0.95): shoegaze: stack fuzz + reverse-reverb + pitch-glide guitar layers until individual notes blur into a WALL; vocals mixed INTO the wall (a texture, not a lead), tempos slow *(curated:claude/2026-07-03-w9)*
- **vst fx presets** (w0.92): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **send reverb** (w0.8): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **evolving pads** (w0.6): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
