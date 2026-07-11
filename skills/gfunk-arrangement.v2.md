---
name: gfunk-arrangement
version: 2
kind: genre
tags: [gfunk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-96; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - NEON BASS is non-negotiable: 8th-note bass locked to the kick root, slightly saturated
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
  - FUNK BREAK is non-negotiable: the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it
---
# Gfunk arrangement (graph-compiled)

## The pocket — gfunk_bounce
gfunk loop DNA (wave14) Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 + grid:curated (wave14 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **neon bass** (w0.75): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **funk break** (w0.7): the one-bar drum break (Clyde Stubblefield lineage): ghost-note 16th snare chatter around a fat backbeat — THE most sampled material in music; chop it, don't quantize it *(curated:claude/2026-07-03-w5)*
- **m7 chords** (w0.6): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **clav comp**: faust clav_funk: narrow pulse + snap transient, fast decay — 16th staccato comping with ghost velocities (0.2-0.4)
- **clav funk zones**: clav_funk knobs: duty 0.1-0.45 (pulse width - hollowness of the bark), snap 0-1.5, decay 0.1-1s, tone 2000-12000 (resonant LP). Wah-clav = automate tone with the groove; darker funk comp = tone 4000.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
