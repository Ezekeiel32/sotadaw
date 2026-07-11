---
name: triphop-arrangement
version: 2
kind: genre
tags: [triphop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-95; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - DUSTY CHAIN is non-negotiable: fx_saturate drive 6-10 + fx_reverb small dark = lofi glue
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
---
# Triphop arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **dusty chain** (w0.9): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.8): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **m7 chords** (w0.7): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **tape saturation** (w0.7): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **groove dilla** (w0.7): apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*

## The groove (timing DNA — apply it, don't fake it)
- apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) after writing on-grid notes — the profile carries this genre's micro-timing and velocity shape. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
