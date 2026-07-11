---
name: psychill-arrangement
version: 1
kind: genre
tags: [psychill, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-95; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -15..-12, band order low>lowmid>mid.
  - DUB SPACE BLOOM is non-negotiable: psybient space law: long dark delays + a huge damped hall bloom behind everything — the SPACE is an instrument; sends run hot on pads/leads, the sub stays bone dry
  - WORLD PERC CONVERSATION is non-negotiable: hand percussion (dhol/duduk-adjacent voices) converses in the midground — sparse call-answer hits, never a loop wall
---
# Psychill arrangement (graph-compiled)

## The pocket — psychill_drift
Psychill (~88 BPM): softer than psybient — halftime kick, warm dark keys answering the pads, sub in long notes, percs barely there; the drift between ambient and groove.  *(source: curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dub space bloom** (w1.0): psybient space law: long dark delays + a huge damped hall bloom behind everything — the SPACE is an instrument; sends run hot on pads/leads, the sub stays bone dry *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*
- **world perc conversation** (w0.92): hand percussion (dhol/duduk-adjacent voices) converses in the midground — sparse call-answer hits, never a loop wall *(curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, session fable-gen; reference class = his Entheogenic imports))*

## Sound recipes (this palette, these moves)
- **psychill warmth**: dark keys bed + a rhodes line drifting over sustained sub; halftime pulse; everything swims in the hall except the sub

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-12, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
