---
name: boombap-arrangement
version: 6
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
snare 1&3 hard, swing 0.56-0.62, dusty kit Swing 0.58 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 (wave17 swing-grid migration; bug class from wave16 blues probe))*

## Techniques (weight order — the top ones DEFINE the genre)
- **swing 16th** (w1.0): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **ghost notes** (w0.92): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **groove dilla** (w0.9): apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **groove boombap 56** (w0.9): apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **layered snare** (w0.84): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*
- **m7 chords** (w0.76): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **snare zones**: snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; tone 0.7 + decay 1.5 = fat lo-fi snare.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*
- PREFER apply_groove(track='drums'-like tracks, name='boombap_56', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (56% swing + heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
