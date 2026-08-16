---
name: midwest_emo-arrangement
version: 3
kind: genre
tags: [midwest_emo, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-155; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -14..-11, band order mid>lowmid>low.
  - TWINKLY ARPEGGIO is non-negotiable: fingerpicked cascading OPEN-string arpeggios that ring and overlap — the twinkle (midwest emo)
  - OPEN TUNING CHIME is non-negotiable: open tunings (FACGCE, DADGAD) so strummed shapes ring as lush extended chords with droning open strings (midwest emo)
  - UNCONVENTIONAL VOICING is non-negotiable: maj7 / add9 / sus2 recolorings in place of plain triads — one note changes everything (emo, math rock)
---
# Midwest_Emo arrangement (graph-compiled)

Midwest_Emo is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — twinkle_cell
The twinkly arpeggio cycle: a fingerpicked open-tuning (FACGCE) maj7/add9 arpeggio in 6/8 (~140 BPM, light swing ~55%); notes RING and overlap (long lengths, no muting), ascending then cascading, one guitar's cycle displaced against the other's for a 2-against-3 hemiola. Swing 0.55 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **twinkly arpeggio** (w1.0): fingerpicked cascading OPEN-string arpeggios that ring and overlap — the twinkle (midwest emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **open tuning chime** (w0.92): open tunings (FACGCE, DADGAD) so strummed shapes ring as lush extended chords with droning open strings (midwest emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **unconventional voicing** (w0.84): maj7 / add9 / sus2 recolorings in place of plain triads — one note changes everything (emo, math rock) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **hemiola pattern** (w0.76): 2-against-3 overlapping guitar phrases — dreamy but math-y (midwest emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **quiet loud dynamics** (w0.68): the Pixies grammar: a restrained clean/ambient valley ERUPTS into a distorted wall, then recedes — the dynamics are the hook (grunge, post-metal, emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **tapped arpeggio** (w0.6): bright, clean two-hand TAPPED arpeggio cascades — every note articulate (math rock, emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **untrained earnest vocal** (w0.52): a heartfelt, imperfect, slightly off-key confessional delivery — the imperfection IS the point (midwest emo) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Inherited from rock
- layered snare: sample clap + synth snare body at -12 to -18
- huge space: bus reverb at maximum size, generous sends — the room is the instrument
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- quick change blues: 12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness installed at the very top of the form; the single most common blues alteration [Popular music: blues harmony]
- blues turnaround: bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony]
- sixteen bar blues: four 4-bar phrases — tonic stated twice, then subdominant, then dominant phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock [Popular music: blues harmony]
- blues dominant color: the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony]
- ...and from the rock skill itself: mud zone 200 400, parallel detail pump, strophic form, refrain hook

## Sound recipes (this palette, these moves)
- **twinkle guitar**: faust clean_chime_guitar: fingerpicked OPEN-tuning arpeggios, high sustain so notes ring/overlap, gentle chorus shimmer; medium plate + triplet delay; hard-panned pair; intimate high-crest master.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-11, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
