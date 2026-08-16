---
name: dub-arrangement
version: 4
kind: genre
tags: [dub, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-90; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - ONE DROP is non-negotiable: reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole
  - DUB DELAY RIDE is non-negotiable: the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Dub arrangement (graph-compiled)

## The pocket — one_drop_dub
dub loop DNA (wave14) Swing 0.56 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **one drop** (w0.95): reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole *(curated:claude/2026-07-03-w6)*
- **dub delay ride** (w0.95): the mixing desk is the instrument: throw single hits into tape delay / spring reverb sends and RIDE the feedback (swell, then cut before runaway) — automate sends per-hit, not per-track *(curated:claude/2026-07-03-w6)*
- **send reverb** (w0.85): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **offbeat bass** (w0.8): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **echo out cut** (w0.7): beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='reggae_lean', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (behind-the-beat lag ~8-12ms, offbeat-8th bubble accents; one-drop space))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
