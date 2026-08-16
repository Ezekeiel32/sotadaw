---
name: dub_techno-arrangement
version: 10
kind: genre
tags: [dub_techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-125; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - DUB TECHNO CHORD is non-negotiable: dub techno: ONE bandpassed minor chord stab fed to an endless echo (feedback 0.7+, dotted delay), detuned slightly per repeat; the track is the chord's decay riding a soft 4-floor
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Dub_Techno arrangement (graph-compiled)

## The pocket — dubtech_pulse
dub_techno loop DNA (wave15) Swing 0.52 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dub techno chord** (w0.95): dub techno: ONE bandpassed minor chord stab fed to an endless echo (feedback 0.7+, dotted delay), detuned slightly per repeat; the track is the chord's decay riding a soft 4-floor *(curated:claude/2026-07-03-w11)*
- **vst fx presets** (w0.92): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **dub delay ride** (w0.8): the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track *(curated:claude/2026-07-03-w6)*
- **four on floor** (w0.7): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb
- **pad motion zones**: pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth 0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = motion 0.6 + drift 0.3; automate depth for evolving intros.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
