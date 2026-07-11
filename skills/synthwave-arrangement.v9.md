---
name: synthwave-arrangement
version: 9
kind: genre
tags: [synthwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-118; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -15..-9, band order low>lowmid~mid.
  - SUPERSAW PADS is non-negotiable: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
  - VST FACTORY PRESETS is non-negotiable: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
  - GATED REVERB SNARE is non-negotiable: big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law
  - SYNTH PARAM MAPS is non-negotiable: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
---
# Synthwave arrangement (graph-compiled)

## The pocket — synthwave_grid
kick 1&3 (or four-floor soft), BIG snare 2&4, arps drive 8ths, pads hold the sky  *(source: curated:claude/2026-07-02 + grid:curated:claude/2026-07-03 (machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **supersaw pads** (w1.0): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **vst factory presets** (w0.95): factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility *(verified:one-call-apply/2026-07-04 (phrasing lesson FALSIFIED: 0.857->0.857 w/ 0 usage; refined to tool-side friction fix — TAL 87-param + Surge blob applied+rendered via single calls))*
- **gated reverb snare** (w0.92): big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law *(curated:claude/2026-07-02)*
- **synth param maps** (w0.9): presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion *(verified:synth-maps/2026-07-04 (Odin Filter1 Frequency 400 dropped a factory lead 5121→786Hz centroid; ranges from Odin source registration))*
- **arp 8th** (w0.84): relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted *(curated:claude/2026-07-02)*
- **neon bass** (w0.76): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **width bloom** (w0.68): fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end *(skill:automation-motion@v1)*

## Sound recipes (this palette, these moves)
- **neon pad**: pad_motion chords + fx_widen 1.4 + send verb — the horizon
- **retro arp**: pluck2 16th arp + fx_delay dotted-8th feedback 0.35
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate
- **pad motion zones**: pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth 0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = motion 0.6 + drift 0.3; automate depth for evolving intros.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-9, band order low>lowmid~mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
