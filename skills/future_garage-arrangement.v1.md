---
name: future_garage-arrangement
version: 1
kind: genre
tags: [future_garage, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-140; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - HAUNTED 2STEP is non-negotiable: future garage: 2-step shuffle with the ghosts turned up — pitch-shifted vocal wisps, sub SWELLS (not hits), vinyl crackle as glue, empty space as the lead
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Future_Garage arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **haunted 2step** (w0.95): future garage: 2-step shuffle with the ghosts turned up — pitch-shifted vocal wisps, sub SWELLS (not hits), vinyl crackle as glue, empty space as the lead *(curated:claude/2026-07-03-w10)*
- **send reverb** (w0.8): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **groove ukg shuffle** (w0.7): THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **reese bass** (w0.5): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
