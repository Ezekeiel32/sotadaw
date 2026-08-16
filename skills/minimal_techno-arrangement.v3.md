---
name: minimal_techno-arrangement
version: 3
kind: genre
tags: [minimal_techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-132; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - MINIMAL PULSE is non-negotiable: minimal: microscopic elements (a click, a tick, a one-note bass), ONE change per 16-32 bars; the groove emerges from what is NOT there — resist every urge to add
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Minimal_Techno arrangement (graph-compiled)

## The pocket — minimal_skeleton
minimal_techno loop DNA (wave15)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **minimal pulse** (w0.95): minimal: microscopic elements (a click, a tick, a one-note bass), ONE change per 16-32 bars; the groove emerges from what is NOT there — resist every urge to add *(curated:claude/2026-07-03-w11)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **huge space** (w0.6): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **filter transition** (w0.5): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
