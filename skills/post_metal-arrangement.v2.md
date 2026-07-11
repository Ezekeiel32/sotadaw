---
name: post_metal-arrangement
version: 2
kind: genre
tags: [post_metal, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 40-160; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - LONG CRESCENDO is non-negotiable: a multi-minute dynamic build from one sparse layer to an overwhelming/ecstatic climax — AUTOMATE it (late-bloom curve), never jump-cut it (post-metal, spiritual jazz)
  - QUIET LOUD DYNAMICS is non-negotiable: the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo)
  - PEDAL DRONE is non-negotiable: a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock)
---
# Post_Metal arrangement (graph-compiled)

Post_Metal is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — crescendo
'The Crescendo' (~70 BPM, 4/4 or 6/8): a 4-8-bar pedal-tone/power-chord motif repeated 8-16x; movement is VERTICAL not horizontal -- start with a single clean tremolo note + brushed cymbal, each repeat adds a layer (2nd guitar -> distortion engages -> bass sub -> double-bass + crash wall) so the SAME motif detonates as a full distorted climax by the last cycle. The 'hit' is the payoff downbeat where the wall lands.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **long crescendo** (w1.0): a multi-minute dynamic build from one sparse layer to an overwhelming/ecstatic climax — AUTOMATE it (late-bloom curve), never jump-cut it (post-metal, spiritual jazz) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **quiet loud dynamics** (w0.92): the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **pedal drone** (w0.84): a sustained pedal/drone tone held UNDER shifting harmony above — the still center (post-metal, modal & spiritual jazz, krautrock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tremolo wall** (w0.76): a fast-picked distorted chord wash detonating at the climax (post-metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hypnotic repetition** (w0.68): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tectonic lowend** (w0.6): downtuned bass and guitar in UNISON for physical sub weight (post-metal, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **ambient interlude** (w0.52): a clean/effected/orchestral breather between heavy movements (post-metal, black metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **layered tuning stack** (w0.44): several differently-tuned guitars stacked for a dense harmonic haze (post-metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from metal
- layered snare: sample clap + synth snare body at -12 to -18
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- palm mute chug: metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither
- wall of sustain: metal density law: loudness comes from what SUSTAINS between the chug hits — but the GUITARS are the face of the wall: doubled rhythm guitars sustain/ring on chorus chords, cymbal wash fills the top, and the bass guitar sustains UNDERNEATH at -6 or lower relative to the guitars (lowmid must stay dominant over low; a loud sustaining bass flips the balance and reads as mud, not power)

## Sound recipes (this palette, these moves)
- **tectonic layers**: faust highgain_guitar in 2-3 layers (octaves/detunes) feeding a SHARED reverb bus for the wall; clean valleys = keys_dark/pad_motion + big reverb; THE CRESCENDO IS AUTOMATION (fx_trim + drive + reverb-send + layer mute-ins, late-bloom curve >0); do NOT brickwall.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
