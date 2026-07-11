---
name: doom_metal-arrangement
version: 2
kind: genre
tags: [doom_metal, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 40-110; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - DOWNTUNED POWER CHORD is non-negotiable: slow, sustained root-fifth chords rung across whole bars, heavily downtuned — the Sabbath/Iommi trudge (doom)
  - DOOM CRAWL is non-negotiable: a half-time / sub-60-BPM trudging pulse, huge spaced hits ringing across the whole bar
  - FEEDBACK DRONE is non-negotiable: sustained amp feedback held over and between chords as texture — doom's connective tissue
---
# Doom_Metal arrangement (graph-compiled)

Doom_Metal is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — iommi_crawl
'Iommi Crawl' (~65 BPM, 4/4, straight-to-behind): kick on 1, snare on 3 (a HUGE half-time backbeat, heavy room reverb), sparse fills; a single downtuned power chord struck on beat 1 and left to RING and decay across the bar, moving every 1-2 bars through a minor riff; feedback bleeds in the gaps; bass doubles the guitar an octave-fat. (Sludge variant = same skeleton ~85 BPM, dirtier, screamed, occasional d-beat burst.) Swing 0.53 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **downtuned power chord** (w1.0): slow, sustained root-fifth chords rung across whole bars, heavily downtuned — the Sabbath/Iommi trudge (doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **doom crawl** (w0.92): a half-time / sub-60-BPM trudging pulse, huge spaced hits ringing across the whole bar *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **feedback drone** (w0.84): sustained amp feedback held over and between chords as texture — doom's connective tissue *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **fuzz wall** (w0.76): stacked fuzz/overdrive into loud sustaining amps = a WALL of sound; doubled and panned for width (grunge, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **bluesy bend** (w0.68): slow pentatonic/blues string bends and heavy vibrato — the Southern lean (doom, stoner) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **dissonant tritone** (w0.6): flat-fifth / minor-second interval clusters for cold, atonal dread (black & death metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **epic clean vocal** (w0.52): an operatic, sustained CLEAN vocal melody soaring over the crawl (epic doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **sludge stomp** (w0.44): a dragged, dirty, hardcore-inflected mid-tempo groove with screamed vocals and feedback bleed (sludge) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from metal
- layered snare: sample clap + synth snare body at -12 to -18
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- palm mute chug: metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither
- wall of sustain: metal density law: loudness comes from what SUSTAINS between the chug hits — but the GUITARS are the face of the wall: doubled rhythm guitars sustain/ring on chorus chords, cymbal wash fills the top, and the bass guitar sustains UNDERNEATH at -6 or lower relative to the guitars (lowmid must stay dominant over low; a loud sustaining bass flips the balance and reads as mud, not power)

## Sound recipes (this palette, these moves)
- **iommi wall**: faust fuzz_guitar downtuned + WARM (heavy sustain, sub-octave): long ringing power chords + a low held drone track for feedback; huge low + PRESENT mids (Sabbath tone isn't scooped); large room reverb; let the slow hits BREATHE.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
