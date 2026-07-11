---
name: speed_garage-arrangement
version: 3
kind: genre
tags: [speed_garage, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-136; set the song key (suggested: G minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - WARPED BASSLINE is non-negotiable: speed garage/bassline: the pitch-WARPED sub 'wow' (detuned reese, filter+pitch bend per note) under a 4x4 garage shuffle; organ stabs on the offbeat
  - GROOVE UKG SHUFFLE is non-negotiable: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
---
# Speed_Garage arrangement (graph-compiled)

## The pocket — speedgarage_4x4
4x4 garage shuffle, skippy ghosts  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **warped bassline** (w0.9): speed garage/bassline: the pitch-WARPED sub 'wow' (detuned reese, filter+pitch bend per note) under a 4x4 garage shuffle; organ stabs on the offbeat *(curated:claude/2026-07-03-w8)*
- **groove ukg shuffle** (w0.8): THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **four on floor** (w0.7): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **vocal chops** (w0.6): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='ukg_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (2-step: hard 16th swing, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
