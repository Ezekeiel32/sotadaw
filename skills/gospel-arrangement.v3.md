---
name: gospel-arrangement
version: 3
kind: genre
tags: [gospel, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-110; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - GOSPEL PROGRESSION is non-negotiable: gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
---
# Gospel arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **gospel progression** (w0.95): gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords *(curated:claude/2026-07-03-w7)*
- **call response melody** (w0.85): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **m7 chords** (w0.8): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns
- **choir ah pad**: faust vox_pad: designed choir-ah (saws through 700/1050 formants, slow bloom) — gospel swells, trance pads, cinematic beds; the sampled choir kit is the REAL thing, this is the designed color to layer with it
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
