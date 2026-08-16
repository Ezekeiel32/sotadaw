---
name: boombap-arrangement
version: 11
kind: genre
tags: [boombap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 85-95; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -16..-9, band order low>lowmid>mid.
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
  - GHOST NOTES is non-negotiable: low-velocity (0.25-0.45) off-grid hits between main hits
  - GROOVE DILLA is non-negotiable: apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile.
  - GROOVE BOOMBAP 56 is non-negotiable: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
---
# Boombap arrangement (graph-compiled)

## The pocket — boombap_drums
snare 1&3 hard, swing 0.56-0.62, dusty kit Swing 0.58 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **swing 16th** (w1.0): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **ghost notes** (w0.92): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **groove dilla** (w0.9): apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **groove boombap 56** (w0.9): apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **layered snare** (w0.84): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*
- **m7 chords** (w0.76): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **groove transfer** (w0.75): a record's timing DNA (onset phase vs grid) extracts as a named groove and applies to NEW material at ~0.9 — on-grid notes move, off-grid feel is preserved; apply to hats/snare, keep kick straight [battery: 412/429 onsets learned from a real record; 80 notes moved on the flip] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **parallel thwack attack** (w0.7): on the parallel crush bus the ATTACK chooses the transient's character: 25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap — then blend under the dry until it's felt not heard [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **parallel density vs emphasis** (w0.65): two parallel-comp intents, two clocks: fast attack + slow release fills DENSITY under the dry transients; moderate attack + short release EMPHASIZES the transients — decide which the dry bus lacks before touching the knobs [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **chord lane vote** (w0.65): when you OWN the symbols, vote harmony from notes, never from audio: bar-wise duration x velocity weights, bass witnesses x2.5, b7 read for dominant color; muted transcription sketches still vote on imports [battery: 9/12 exact incl. 7s on 12-bar blues where the audio HMM scored 2/12; 4/4 on triads where audio heard nothing] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **strophic form** (w0.65): AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- **expressive performance** (w0.65): humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it *(deep-research firing 66 (GrooVAE/Magenta + GigaMIDI TISMIR 2025, adversarially verified) + firing 67-68 battery (13/13; two metrics; microtiming survives render 139ms) via curated:claude/2026-07-05 (wave36))*

## Sound recipes (this palette, these moves)
- **snare zones**: snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; tone 0.7 + decay 1.5 = fat lo-fi snare.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*
- PREFER apply_groove(track='drums'-like tracks, name='boombap_56', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (56% swing + heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
