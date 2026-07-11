---
name: post_punk-arrangement
version: 1
kind: genre
tags: [post_punk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-165; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>low>mid.
  - POST PUNK BASS is non-negotiable: post-punk: the BASS is the lead — melodic driving 8ths high on the neck; scratchy staccato guitar ANSWERS in the gaps; drums dry and motorik
  - JANGLE STRUM is non-negotiable: indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed
  - HUGE SPACE is non-negotiable: bus reverb at maximum size, generous sends — the room is the instrument
---
# Post_Punk arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **post punk bass** (w0.95): post-punk: the BASS is the lead — melodic driving 8ths high on the neck; scratchy staccato guitar ANSWERS in the gaps; drums dry and motorik *(curated:claude/2026-07-03-w11)*
- **jangle strum** (w0.6): indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed *(curated:claude/2026-07-03-w9)*
- **huge space** (w0.5): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **dbeat energy** (w0.5): punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30 *(curated:claude/2026-07-03-w9)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
