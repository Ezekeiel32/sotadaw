---
name: lofi-arrangement
version: 3
kind: genre
tags: [lofi, boombap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-85; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -20..-12, band order low~lowmid>mid.
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - GROOVE DILLA is non-negotiable: apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile.
---
# Lofi arrangement (graph-compiled)

Lofi is a child of **boombap** — its groove laws apply unless overridden below.

## The pocket — lofi_pocket
loose kicks, snare late, everything soft  *(source: skill:lofi-arrangement@v1)*

## Techniques (weight order — the top ones DEFINE the genre)
- **behind beat snare** (w1.0): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **m7 chords** (w0.92): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **groove dilla** (w0.9): apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **dusty chain** (w0.84): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **swing 16th** (w0.76): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*

## Inherited from boombap
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- layered snare: sample clap + synth snare body at -12 to -18
- groove boombap 56: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.

## The groove (timing DNA — apply it, don't fake it)
- apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) after writing on-grid notes — the profile carries this genre's micro-timing and velocity shape. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -20..-12, band order low~lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
