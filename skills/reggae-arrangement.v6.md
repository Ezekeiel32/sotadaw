---
name: reggae-arrangement
version: 6
kind: genre
tags: [reggae, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-90; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order low>lowmid>mid.
  - ONE DROP is non-negotiable: reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole
  - SKANK UPSTROKE is non-negotiable: ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Reggae arrangement (graph-compiled)

## The pocket — reggae_onedrop
one drop: beat 1 EMPTY, kick+snare together on 3, hat 8ths Swing 0.52 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **one drop** (w0.95): reggae/dub drum LAW: kick+snare land TOGETHER on beat 3, beat 1 stays EMPTY (the drop); guitar/keys skank the offbeat 8ths — the groove is the hole *(curated:claude/2026-07-03-w6)*
- **skank upstroke** (w0.95): ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse *(curated:claude/2026-07-03-w7)*
- **offbeat bass** (w0.7): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **two chord vamp** (w0.6): two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **cadence modal VII i** (w0.6): the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='reggae_lean', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (behind-the-beat lag ~8-12ms, offbeat-8th bubble accents; one-drop space))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
