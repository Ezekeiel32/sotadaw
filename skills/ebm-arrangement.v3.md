---
name: ebm-arrangement
version: 3
kind: genre
tags: [ebm, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 115-130; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order lowmid>low>mid.
  - EBM BASSLINE is non-negotiable: EBM: militant sequenced 16th square/saw bass, unwavering, mid-forward; stomping 4-floor + industrial claps; shouted-vocal space left in the mid band
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - MACHINE PERCUSSION is non-negotiable: industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read
---
# Ebm arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **ebm bassline** (w0.95): EBM: militant sequenced 16th square/saw bass, unwavering, mid-forward; stomping 4-floor + industrial claps; shouted-vocal space left in the mid band *(curated:claude/2026-07-03-w11)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **machine percussion** (w0.7): industrial: build the kit from METAL — clangs/hits/ratchets layered as drums, distorted 16th synth bass, EVERYTHING through drive; precision makes the aggression read *(curated:claude/2026-07-03-w10)*
- **gain staged saturation** (w0.6): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **vst factory presets** (w0.6): playing a VST like its designers intended: tal_presets.py get '<name>' returns the params dict — inline it as source {kind:'vst3', plugin:'TAL-NoiseMaker', params:{...}}; 256 factory sounds in 8 categories (54 BASS, 77 LEAD, 26 PAD...); search library.json vst_presets by category, then tweak the named params from there *(verified:tal-preset-rail/2026-07-03 (pad 448ms attack/779Hz; bass 10ms/338Hz))*

## Sound recipes (this palette, these moves)
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
