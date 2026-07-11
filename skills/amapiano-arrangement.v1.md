---
name: amapiano-arrangement
version: 1
kind: genre
tags: [amapiano, afrobeats, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-118; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -16..-9, band order low>lowmid>mid.
  - LOG DRUM LEAD is non-negotiable: amapiano signature: melodic log-drum bass hits (sub_clean/pluckbass short notes) walking wide intervals, LOTS of space
  - SPARSE KICK is non-negotiable: kick on 1 and ~3.5 only; space carries the bounce
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Amapiano arrangement (graph-compiled)

Amapiano is a child of **afrobeats** — its groove laws apply unless overridden below.

## The pocket — ama_pocket
log drums lead the LOW-MID, kick whispers, shaker carries time; space is the sound  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **log drum lead** (w1.0): amapiano signature: melodic log-drum bass hits (sub_clean/pluckbass short notes) walking wide intervals, LOTS of space *(curated:claude/2026-07-03)*
- **sparse kick** (w0.93): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*
- **send reverb** (w0.86): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **shuffle swing** (w0.79): hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt *(curated:claude/2026-07-02)*

## Inherited from afrobeats
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- log drum bass: melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature
- triplet percs: 3:2 cross-rhythm percussion over a straight kick — rims/toms/shaker
- call response melody: 2-bar call, 2-bar answer; melody talks to itself

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
