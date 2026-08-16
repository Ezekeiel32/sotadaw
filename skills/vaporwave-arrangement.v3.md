---
name: vaporwave-arrangement
version: 3
kind: genre
tags: [vaporwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-85; set the song key (suggested: E major).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>low>mid.
  - VAPOR SLOW is non-negotiable: vaporwave: slow the source 20-40% and pitch it down 3-5 semitones, drench in reverb+chorus, let the loop hypnotize — tape warble and imperfection ARE the aesthetic
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
  - TAPE SATURATION is non-negotiable: heavy fx_saturate drive 8-14 over the whole beat bus = grit
---
# Vaporwave arrangement (graph-compiled)

## The pocket — slowed_quarters
vaporwave loop DNA (wave16)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **vapor slow** (w0.95): vaporwave: slow the source 20-40% and pitch it down 3-5 semitones, drench in reverb+chorus, let the loop hypnotize — tape warble and imperfection ARE the aesthetic *(curated:claude/2026-07-03-w12)*
- **send reverb** (w0.8): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **tape saturation** (w0.7): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **huge space** (w0.6): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='halftime_drag', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (phonk/memphis/doom drag: uniform lag, backbeat extra late))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
