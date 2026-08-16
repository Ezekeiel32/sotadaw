---
name: post_punk-arrangement
version: 3
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

## The pocket — motorik_drive
post_punk loop DNA (wave16)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **post punk bass** (w0.95): post-punk: the BASS is the lead — melodic driving 8ths high on the neck; scratchy staccato guitar ANSWERS in the gaps; drums dry and motorik *(curated:claude/2026-07-03-w11)*
- **jangle strum** (w0.6): indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed *(curated:claude/2026-07-03-w9)*
- **huge space** (w0.5): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **dbeat energy** (w0.5): punk: 8th-note downstroke wall at 160-190, d-beat drums (kick-snare gallop), two chords are plenty, nothing longer than 2:30 *(curated:claude/2026-07-03-w9)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
