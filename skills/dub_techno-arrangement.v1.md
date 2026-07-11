---
name: dub_techno-arrangement
version: 1
kind: genre
tags: [dub_techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 115-125; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - DUB TECHNO CHORD is non-negotiable: dub techno: ONE bandpassed minor chord stab fed to an endless echo (feedback 0.7+, dotted delay), detuned slightly per repeat; the track is the chord's decay riding a soft 4-floor
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
  - DUB DELAY RIDE is non-negotiable: the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track
---
# Dub_Techno arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **dub techno chord** (w0.95): dub techno: ONE bandpassed minor chord stab fed to an endless echo (feedback 0.7+, dotted delay), detuned slightly per repeat; the track is the chord's decay riding a soft 4-floor *(curated:claude/2026-07-03-w11)*
- **huge space** (w0.8): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **dub delay ride** (w0.8): the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track *(curated:claude/2026-07-03-w6)*
- **four on floor** (w0.7): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
