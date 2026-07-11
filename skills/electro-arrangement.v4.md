---
name: electro-arrangement
version: 4
kind: genre
tags: [electro, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-135; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>mid>lowmid.
  - SYNTH PARAM MAPS is non-negotiable: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
  - ELECTRO BOOGIE is non-negotiable: Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor
  - 808 GLIDE is non-negotiable: long overlapping 808 notes walking the scale; tune to key
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Electro arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **synth param maps** (wNone): presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion *(verified:synth-maps/2026-07-04 (Odin Filter1 Frequency 400 dropped a factory lead 5121→786Hz centroid; ranges from Odin source registration))*
- **electro boogie** (w0.95): Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor *(curated:claude/2026-07-03)*
- **808 glide** (w0.6): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **neon bass** (w0.6): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **vst factory presets** (w0.6): factory sounds FIRST for synth-genre leads/pads/basses: call vst_presets(query='PAD'|'BASS'|'LEAD'|'Atmospheres'..., mode='list') to browse 4,366 sounds, then mode='get' — TAL/Odin return a params dict to inline as source {kind:'vst3', plugin:..., params:{...}}; Surge returns a 'use' dict with a preset blob path. Then reshape 2-5 named knobs per synth-maps (natural units). Faust voices are for drums/percussion/utility — the SYNTH SOUNDS live in the preset rail *(verified:preset-rails/2026-07-04 (synthwave eval exposed stale CLI phrasing — agent-facing tool is vst_presets; re-taught MCP-first))*
- **cowbell lead** (w0.5): saturated cowbell/bell riff as THE melodic hook, minor pentatonic *(curated:claude/2026-07-02)*
- **vocal chops** (w0.4): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate
- **clap 909 zones**: clap_909 knobs: decay 0.08-0.8s (main burst), tone 600-4000 (bp centre), spread 0.3-2.5 (pre-burst roll tightness). tone 2800 = brighter electro clap; spread 2 = loose human clap.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
