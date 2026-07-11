---
name: orchestral_cinematic-arrangement
version: 2
kind: genre
tags: [orchestral_cinematic, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-140; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -16..-10, band order lowmid>low>mid.
  - TRAILER BUILD is non-negotiable: cinematic: ostinato strings (8th cells) + brass swells + a percussion HIT every 4 bars, riser into tutti-plus-choir; silence right before the biggest hit
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - JOURNEY STRUCTURE is non-negotiable: 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown
---
# Orchestral_Cinematic arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **trailer build** (w0.9): cinematic: ostinato strings (8th cells) + brass swells + a percussion HIT every 4 bars, riser into tutti-plus-choir; silence right before the biggest hit *(curated:claude/2026-07-03-w10)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **journey structure** (w0.7): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **evolving pads** (w0.6): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **cine timpani**: faust timpani: tuned orchestral drum, strike pitch-drop + mallet noise, long boom; fast low-vel repeats = rolls under trailer builds

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
