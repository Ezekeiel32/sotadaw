---
name: 3step-arrangement
version: 1
kind: genre
tags: [3step, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-116; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order low>lowmid>mid.
  - 3STEP PULSE is non-negotiable: 3-step: amapiano stripped to a 3-hit kick cell per bar (x..x..x.) with huge negative space; log drum answers the kick in the holes; keep everything else whisper-quiet
  - LOG DRUM BASS is non-negotiable: melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# 3Step arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **3step pulse** (w0.95): 3-step: amapiano stripped to a 3-hit kick cell per bar (x..x..x.) with huge negative space; log drum answers the kick in the holes; keep everything else whisper-quiet *(curated:claude/2026-07-03-w8)*
- **log drum bass** (w0.85): melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature *(curated:claude/2026-07-02)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **evolving pads** (w0.7): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
