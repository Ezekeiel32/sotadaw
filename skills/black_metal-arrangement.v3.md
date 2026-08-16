---
name: black_metal-arrangement
version: 3
kind: genre
tags: [black_metal, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-250; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order mid>lowmid>low.
  - TREMOLO PICKING is non-negotiable: continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing)
  - TRADITIONAL BLAST BEAT is non-negotiable: single-stroke blast: snare on every off-16th, kick on every on-16th (continuous roll), ride/crash in unison with the kick, NO backbeat pocket — felt as pure motion at 180+ BPM
  - DISSONANT TRITONE is non-negotiable: flat-fifth / minor-second interval clusters for cold, atonal dread (black & death metal)
---
# Black_Metal arrangement (graph-compiled)

Black_Metal is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — frostbite_blast
'Frostbite Blast' (~190 BPM, 4/4, 0% swing): traditional blast = snare on every off-16th, kick on every on-16th (continuous single-stroke roll), crash/ride with each kick, NO backbeat; one power-chord root tremolo-picked as unbroken 16ths, the chord changing every 1-2 bars while the picking never stops. The groove is the ABSENCE of a pocket -- pure forward blur.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tremolo picking** (w1.0): continuous fast alternate-picked single notes that blur into a sustained WALL — the wash, not the pluck (surf leads; black & death metal riffing) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **traditional blast beat** (w0.92): single-stroke blast: snare on every off-16th, kick on every on-16th (continuous roll), ride/crash in unison with the kick, NO backbeat pocket — felt as pure motion at 180+ BPM *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **dissonant tritone** (w0.84): flat-fifth / minor-second interval clusters for cold, atonal dread (black & death metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **open power chords** (w0.76): un-muted RINGING power chords (not palm-muted) so the trebly wall sustains (black metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **melodic minor riff** (w0.68): a long, mournful harmonic/natural-minor tremolo melody riding over the blast (black metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **necro lo fi** (w0.6): DELIBERATE low fidelity (4-track/cassette): thin trebly guitars, buried vocals, tape hiss as texture — the 'necro' aesthetic (black metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **rasp shriek vocal** (w0.52): a high, distorted, throat-forward black-metal shriek, mixed BACK behind the guitars *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hypnotic repetition** (w0.44): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from metal
- layered snare: sample clap + synth snare body at -12 to -18
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- palm mute chug: metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither
- wall of sustain: metal density law: loudness comes from what SUSTAINS between the chug hits — but the GUITARS are the face of the wall: doubled rhythm guitars sustain/ring on chorus chords, cymbal wash fills the top, and the bass guitar sustains UNDERNEATH at -6 or lower relative to the guitars (lowmid must stay dominant over low; a loud sustaining bass flips the balance and reads as mud, not power)
- double tracked guitar wall: 
- drop tuned riff: 
- ...and from the metal skill itself: sample reinforced drums

## Sound recipes (this palette, these moves)
- **frost tremolo**: faust highgain_guitar TREBLY (mids KEPT, not scooped -> mids slightly >0), mute=0 (open ringing wall), tremolo-picked, thin/cold; double-tracked; aesthetic is fidelity not loudness -- keep it raw + treble-forward.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
