---
name: death_metal-arrangement
version: 3
kind: genre
tags: [death_metal, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-220; set the song key (suggested: B minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - PALM MUTE CHUG is non-negotiable: metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither
  - BOMB BLAST is non-negotiable: bomb blast: snare on every 8th over 16th-note double-kick (Cannibal Corpse) — the articulate, clicky death-metal blast
  - HM2 BUZZSAW is non-negotiable: a Boss HM-2 with EVERY knob maxed into a cranked amp = the Swedish 'buzzsaw' wall of distortion (Entombed / Sunlight Studio)
---
# Death_Metal arrangement (graph-compiled)

Death_Metal is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — bomb_blast_chug
'Bomb-Blast Chug' (~200 BPM, 4/4, straight): bomb blast = snare on every 8th, double-kick on every 16th, crash on bar-heads; guitar palm-mutes the low root (B1/C2) as 16ths with chromatic passing tones; at the section break the kit HALVES to a ~100-BPM half-time breakdown with the same riff at quarter-note weight.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **palm mute chug** (w1.0): metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither *(curated:claude/2026-07-03-w9)*
- **bomb blast** (w0.92): bomb blast: snare on every 8th over 16th-note double-kick (Cannibal Corpse) — the articulate, clicky death-metal blast *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hm2 buzzsaw** (w0.84): a Boss HM-2 with EVERY knob maxed into a cranked amp = the Swedish 'buzzsaw' wall of distortion (Entombed / Sunlight Studio) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **chromatic riff** (w0.76): semitone-crawling, key-agnostic riffing — note-collections over tonality (death metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **double bass gallop** (w0.68): fast continuous double-kick under a tremolo or galloped riff — the low-end engine of extreme metal *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **death growl** (w0.6): a guttural, false-cord low vocal roar — the death-metal voice *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **half time breakdown** (w0.52): at the breakdown the backbeat HALVES (snare to beat 3) and chug density thins — the structural payoff, not a jam *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tremolo picking** (w0.44): continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from metal
- layered snare: sample clap + synth snare body at -12 to -18
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- wall of sustain: metal density law: loudness comes from what SUSTAINS between the chug hits — but the GUITARS are the face of the wall: doubled rhythm guitars sustain/ring on chorus chords, cymbal wash fills the top, and the bass guitar sustains UNDERNEATH at -6 or lower relative to the guitars (lowmid must stay dominant over low; a loud sustaining bass flips the balance and reads as mud, not power)
- double tracked guitar wall: 
- drop tuned riff: 
- sample reinforced drums: 

## Sound recipes (this palette, these moves)
- **buzzsaw**: faust highgain_guitar high drive: mids>0 = Swedish HM-2 buzzsaw honk ~1k, mids<0 = Florida scoop; palm-mute chugs (mute~0.6) traded with tremolo; hard L/R double; loud tight low; blast_kick on the double-kick.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
