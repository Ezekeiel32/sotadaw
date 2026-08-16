---
name: synthwave-arrangement
version: 12
kind: genre
tags: [synthwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-118; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -15..-9, band order low>lowmid~mid.
  - SUPERSAW PADS is non-negotiable: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
  - VST FACTORY PRESETS is non-negotiable: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
  - GATED REVERB SNARE is non-negotiable: the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat
  - SYNTH PARAM MAPS is non-negotiable: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
---
# Synthwave arrangement (graph-compiled)

## The pocket — synthwave_grid
kick 1&3 (or four-floor soft), BIG snare 2&4, arps drive 8ths, pads hold the sky  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **supersaw pads** (w1.0): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **vst factory presets** (w0.95): factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility *(verified:one-call-apply/2026-07-04 (phrasing lesson FALSIFIED: 0.857->0.857 w/ 0 usage; refined to tool-side friction fix — TAL 87-param + Surge blob applied+rendered via single calls))*
- **gated reverb snare** (w0.92): the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **synth param maps** (w0.9): presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion *(verified:synth-maps/2026-07-04 (Odin Filter1 Frequency 400 dropped a factory lead 5121→786Hz centroid; ranges from Odin source registration))*
- **arp 8th** (w0.84): relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted *(curated:claude/2026-07-02)*
- **neon bass** (w0.76): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **mid side width control** (w0.7): width is DYNAMIC, not a static knob: compressing/boosting the MID makes loud center sounds read wider by contrast; side-only processing adds air that vanishes in mono (acceptable IF it only sweetens the stereo image) — treat mid and side as two mixes [mid/side processing] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **width bloom** (w0.68): fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end *(skill:automation-motion@v1)*
- **width by arrangement** (w0.65): the widest mixes earn it in the WRITE, not the widener: hard-pan doubled parts (two takes L/R), spread a stereo pad wide UNDER a centered lead, keep the focal element (lead/vocal/kick) center — width is contrast, and a wall of wide reads as narrow [arrangement-first width] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **cadence modal VII i** (w0.6): the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **riser into drop** (w0.6): the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop *(engine-witnessed transitions.py (firing 58: solo-render -33->-17->-13dB late-bloom into the drop) via curated:claude/2026-07-05 (wave35 glue))*
- **impact downbeat** (w0.6): a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note *(engine-witnessed transitions.py (firing 58: solo-render -33->-17->-13dB late-bloom into the drop) via curated:claude/2026-07-05 (wave35 glue))*
- also in this genre's DNA (lower weight): seam connects law, haas caution

## Sound recipes (this palette, these moves)
- **neon pad**: pad_motion chords + fx_widen 1.4 + send verb — the horizon
- **retro arp**: pluck2 16th arp + fx_delay dotted-8th feedback 0.35
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate
- **pad motion zones**: pad_motion knobs: detune 0-0.03 (stack spread), motion 0.02-1Hz (sweep rate), depth 0-4000 (sweep range), drift 0-0.5Hz (auto-pan). Frozen pad = depth 0; seasick = motion 0.6 + drift 0.3; automate depth for evolving intros.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-9, band order low>lowmid~mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
