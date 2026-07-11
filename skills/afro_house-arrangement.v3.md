---
name: afro_house-arrangement
version: 3
kind: genre
tags: [afro_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 118-124; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - AFRO HOUSE PERC is non-negotiable: afro house engine: layered ORGANIC percussion loops (shaker+conga+wood) with one lead drum voice doing the call, deep sub swells underneath — percussion is the melody
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
---
# Afro_House arrangement (graph-compiled)

## The pocket — afrohouse_organic
4-floor under organic rim/shaker conversation Swing 0.53 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 (wave17 swing-grid migration; bug class from wave16 blues probe))*

## Techniques (weight order — the top ones DEFINE the genre)
- **afro house perc** (w0.95): afro house engine: layered ORGANIC percussion loops (shaker+conga+wood) with one lead drum voice doing the call, deep sub swells underneath — percussion is the melody *(curated:claude/2026-07-03-w6)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **evolving pads** (w0.7): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **call response melody** (w0.65): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **journey structure** (w0.6): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
