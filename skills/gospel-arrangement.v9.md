---
name: gospel-arrangement
version: 9
kind: genre
tags: [gospel, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-110; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - GOSPEL PROGRESSION is non-negotiable: gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Gospel arrangement (graph-compiled)

## The pocket — gospel_shout
gospel loop DNA (wave19) Swing 0.54 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 (wave24 leads+fills — world/roots))*

## Techniques (weight order — the top ones DEFINE the genre)
- **m7 chords** (w0.95): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **gospel progression** (w0.95): gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords *(curated:claude/2026-07-03-w7)*
- **vst fx presets** (w0.92): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **call response melody** (w0.9): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns
- **choir ah pad**: faust vox_pad: designed choir-ah (saws through 700/1050 formants, slow bloom) — gospel swells, trance pads, cinematic beds; the sampled choir kit is the REAL thing, this is the designed color to layer with it
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
