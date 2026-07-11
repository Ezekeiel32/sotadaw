---
name: ebm-arrangement
version: 5
kind: genre
tags: [ebm, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 115-130; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order lowmid>low>mid.
  - SYNTH PARAM MAPS is non-negotiable: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
  - EBM BASSLINE is non-negotiable: EBM: militant sequenced 16th square/saw bass, unwavering, mid-forward; stomping 4-floor + industrial claps; shouted-vocal space left in the mid band
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
---
# Ebm arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **synth param maps** (wNone): presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion *(verified:synth-maps/2026-07-04 (Odin Filter1 Frequency 400 dropped a factory lead 5121→786Hz centroid; ranges from Odin source registration))*
- **ebm bassline** (w0.95): EBM: militant sequenced 16th square/saw bass, unwavering, mid-forward; stomping 4-floor + industrial claps; shouted-vocal space left in the mid band *(curated:claude/2026-07-03-w11)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **machine percussion** (w0.7): industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read *(curated:claude/2026-07-03-w10)*
- **gain staged saturation** (w0.6): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **vst factory presets** (w0.6): factory sounds FIRST for synth-genre leads/pads/basses: call vst_presets(query='PAD'|'BASS'|'LEAD'|'Atmospheres'..., mode='list') to browse 4,366 sounds, then mode='get' — TAL/Odin return a params dict to inline as source {kind:'vst3', plugin:..., params:{...}}; Surge returns a 'use' dict with a preset blob path. Then reshape 2-5 named knobs per synth-maps (natural units). Faust voices are for drums/percussion/utility — the SYNTH SOUNDS live in the preset rail *(verified:preset-rails/2026-07-04 (synthwave eval exposed stale CLI phrasing — agent-facing tool is vst_presets; re-taught MCP-first))*

## Sound recipes (this palette, these moves)
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
