---
name: hiphop-arrangement
version: 5
kind: genre
tags: [hiphop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-100; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - BREAK LOOPING is non-negotiable: hiphop's founding move: loop the break (the drum-solo bars), cut between two copies on the 1 — then rap over it; everything else (sampling, chopping, scratching) grew from this
  - FUNK BREAK is non-negotiable: the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it
  - MUD ZONE 200 400 is non-negotiable: most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16]
---
# Hiphop arrangement (graph-compiled)

## The pocket — hiphop_break
the looped break: kick 1 & the and-of-2, backbeat Swing 0.56 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **break looping** (w0.95): hiphop's founding move: loop the break (the drum-solo bars), cut between two copies on the 1 — then rap over it; everything else (sampling, chopping, scratching) grew from this *(curated:claude/2026-07-03-w7)*
- **funk break** (w0.85): the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it *(curated:claude/2026-07-03-w5)*
- **mud zone 200 400** (w0.8): most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **structure inheritance** (w0.75): a remix/companion inherits the SOURCE'S section skeleton: its sections become the arrangement form at their real durations — same bar count, same energy arc [battery: Foote on the RENDER, blind to the JSON, found 5/6 joints within 3 bars of the source's] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **groove transfer** (w0.75): a record's timing DNA (onset phase vs grid) extracts as a named groove and applies to NEW material at ~0.9 — on-grid notes move, off-grid feel is preserved; apply to hats/snare, keep kick straight [battery: 412/429 onsets learned from a real record; 80 notes moved on the flip] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **dusty chain** (w0.7): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **acapella bridge** (w0.7): the third DJ transition (blend / echo-out / BRIDGE): the outgoing deck cuts at its phrase but its LAST SUNG PHRASE rides HP-filtered (~130Hz) over the incoming deck and fades by bar 8; find the phrase by probing the final ~24 played bars for the loudest-voiced 8-bar window — a DJ cuts where the VOICE ends, not where the file does [battery: solo render -26dB voice exactly across the swap; voiceless tails fall back honestly] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **parallel density vs emphasis** (w0.65): two parallel-comp intents, two clocks: fast attack + slow release fills DENSITY under the dry transients; moderate attack + short release EMPHASIZES the transients — decide which the dry bus lacks before touching the knobs [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **chord lane vote** (w0.65): when you OWN the symbols, vote harmony from notes, never from audio: bar-wise duration x velocity weights, bass witnesses x2.5, b7 read for dominant color; muted transcription sketches still vote on imports [battery: 9/12 exact incl. 7s on 12-bar blues where the audio HMM scored 2/12; 4/4 on triads where audio heard nothing] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **expressive performance** (w0.65): humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it *(deep-research firing 66 (GrooVAE/Magenta + GigaMIDI TISMIR 2025, adversarially verified) + firing 67-68 battery (13/13; two metrics; microtiming survives render 139ms) via curated:claude/2026-07-05 (wave36))*
- **ghost notes** (w0.6): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='boombap_56', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (56% swing + heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
