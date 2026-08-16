---
name: memphis_rap-arrangement
version: 3
kind: genre
tags: [memphis_rap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-80; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - MEMPHIS CHANT is non-negotiable: dark chopped vocal stab as rhythmic texture (sample kit / choir low)
  - DUSTY CHAIN is non-negotiable: fx_saturate drive 6-10 + fx_reverb small dark = lofi glue
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Memphis_Rap arrangement (graph-compiled)

## The pocket — memphis_knock
memphis_rap loop DNA (wave15) Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **memphis chant** (w0.95): dark chopped vocal stab as rhythmic texture (sample kit / choir low) *(curated:claude/2026-07-02)*
- **dusty chain** (w0.85): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **kick 808 zones**: kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 (tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for verse/drop contrast.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='halftime_drag', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (phonk/memphis/doom drag: uniform lag, backbeat extra late))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
