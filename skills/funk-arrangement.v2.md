---
name: funk-arrangement
version: 2
kind: genre
tags: [funk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-115; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - FUNK BREAK is non-negotiable: the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it
  - GHOST NOTES is non-negotiable: low-velocity (0.25-0.45) off-grid hits between main hits
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Funk arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **funk break** (w0.95): the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it *(curated:claude/2026-07-03-w5)*
- **ghost notes** (w0.85): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **walking bass** (w0.85): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **horn stabs** (w0.8): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **tape saturation** (w0.6): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses
- **clav comp**: faust clav_funk: narrow pulse + snap transient, fast decay — 16th staccato comping with ghost velocities (0.2-0.4)
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
