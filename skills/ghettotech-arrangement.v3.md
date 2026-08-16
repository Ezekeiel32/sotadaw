---
name: ghettotech-arrangement
version: 3
kind: genre
tags: [ghettotech, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 145-155; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - GHETTOTECH TALK is non-negotiable: ghettotech: miami-bass vocal chants at detroit speed (~150), 808 toms, jittery 16th machine programming — booty electro at techno velocity
  - ELECTRO BOOGIE is non-negotiable: Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Ghettotech arrangement (graph-compiled)

## The pocket — ghetto_twitch
ghettotech loop DNA (wave15)  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **ghettotech talk** (w0.95): ghettotech: miami-bass vocal chants at detroit speed (~150), 808 toms, jittery 16th machine programming — booty electro at techno velocity *(curated:claude/2026-07-03-w12)*
- **electro boogie** (w0.7): Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor *(curated:claude/2026-07-03)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **four on floor** (w0.6): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
