---
name: metalcore-arrangement
version: 3
kind: genre
tags: [metalcore, metal, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-200; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - BREAKDOWN CHUG is non-negotiable: half-time palm-muted low-open-string staccato hits with RESTS for mosh weight — the space IS the heaviness (metalcore)
  - SCREAM CLEAN DYNAMIC is non-negotiable: a harsh-scream verse alternating with a big SUNG melodic chorus — built-in tension (metalcore)
  - HALF TIME BREAKDOWN is non-negotiable: at the breakdown the backbeat HALVES (snare to beat 3) and chug density thins — the structural payoff, not a jam
---
# Metalcore arrangement (graph-compiled)

Metalcore is a child of **metal** — its groove laws apply unless overridden below.

## The pocket — breakdown
'The Breakdown' (~130 BPM, 4/4, half-time feel): palm-muted low-open-string (Drop-C) chugs on a syncopated grid WITH RESTS for weight, crash+kick accent the downbeat of each 2-bar cycle, snare pinned to beat 3 (the half-time backbeat), double-kick filling the chug gaps. The verse gallops; the CHORUS is a wide sung melody; the breakdown is the payoff.  *(source: curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **breakdown chug** (w1.0): half-time palm-muted low-open-string staccato hits with RESTS for mosh weight — the space IS the heaviness (metalcore) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **scream clean dynamic** (w0.92): a harsh-scream verse alternating with a big SUNG melodic chorus — built-in tension (metalcore) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **half time breakdown** (w0.84): at the breakdown the backbeat HALVES (snare to beat 3) and chug density thins — the structural payoff, not a jam *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **gallop rhythm** (w0.76): d-U-d-d 16th gallop palm-muted on the low string — driving verse propulsion (metalcore, thrash lineage) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **harmonized lead** (w0.68): twin-guitar thirds/sixths harmony lines lifted from melodic death metal (metalcore, death metal) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **drop d powerchord** (w0.6): one-finger low-D (drop-D) power-chord riffing (grunge, metalcore) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **palm mute chug** (w0.52): metal rhythm: down-tuned palm-muted 8th/16th chugs locked SAMPLE-TIGHT with double-kick; the guitar and kick are ONE instrument — quantize both or neither *(curated:claude/2026-07-03-w9)*

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
- **core chug**: faust highgain_guitar drop-tuned: mute~0.6 for the chug, mute=0 for leads; hard L/R double; the breakdown is an ARRANGEMENT half-time (thin density + snare-to-beat-3); blast_kick under gallops; fx_djfilter riser + fx_trim lift into the drop.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
