---
name: synthwave-arrangement
version: 4
kind: genre
tags: [synthwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-118; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -15..-9, band order low>lowmid~mid.
  - SUPERSAW PADS is non-negotiable: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
  - GATED REVERB SNARE is non-negotiable: big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law
  - ARP 8TH is non-negotiable: relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted
---
# Synthwave arrangement (graph-compiled)

## The pocket — synthwave_grid
kick 1&3 (or four-floor soft), BIG snare 2&4, arps drive 8ths, pads hold the sky  *(source: curated:claude/2026-07-02 + grid:curated:claude/2026-07-03 (machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **supersaw pads** (w1.0): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **gated reverb snare** (w0.92): big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law *(curated:claude/2026-07-02)*
- **arp 8th** (w0.84): relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted *(curated:claude/2026-07-02)*
- **neon bass** (w0.76): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **width bloom** (w0.68): fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end *(skill:automation-motion@v1)*
- **vst factory presets** (w0.6): playing VSTs like their designers intended: 516 factory sounds — tal_presets.py get '<name>' (256: 54 BASS/77 LEAD/26 PAD...) or odin_presets.py get '<name>' (260: Atmospheres/Drones/Chiptune/Stabs/...) returns a params dict; inline as source {kind:'vst3', plugin:'TAL-NoiseMaker'|'Odin2', params:{...}}, then tweak named params from there — values are natural units, the engine converts per-param *(verified:preset-rails/2026-07-03 (TAL pad 448ms/779Hz + bass 10ms/338Hz; Odin analog-bass 1ms/157Hz))*

## Sound recipes (this palette, these moves)
- **neon pad**: pad_motion chords + fx_widen 1.4 + send verb — the horizon
- **retro arp**: pluck2 16th arp + fx_delay dotted-8th feedback 0.35
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-9, band order low>lowmid~mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
