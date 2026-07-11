---
name: tech_house-arrangement
version: 1
kind: genre
tags: [tech_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 124-128; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order low>lowmid>mid.
  - ROLLING OFFBEAT BASS is non-negotiable: THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Tech_House arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **rolling offbeat bass** (w0.95): THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key *(curated:claude/2026-07-02)*
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **vocal chops** (w0.75): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **pump sidechain** (w0.7): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **filter transition** (w0.6): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
