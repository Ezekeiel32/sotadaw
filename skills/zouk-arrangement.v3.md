---
name: zouk-arrangement
version: 3
kind: genre
tags: [zouk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-110; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - ZOUK BEAT is non-negotiable: zouk: compas-derived machine beat ~95-110 (tight kick cell + rimshot pattern), glossy synth chords, romance pacing — the pocket is polite but insistent
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Zouk arrangement (graph-compiled)

## The pocket — zouk_machine
zouk loop DNA (wave18)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **zouk beat** (w0.95): zouk: compas-derived machine beat ~95-110 (tight kick cell + rimshot pattern), glossy synth chords, romance pacing — the pocket is polite but insistent *(curated:claude/2026-07-03-w13)*
- **m7 chords** (w0.7): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **send reverb** (w0.5): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Sound recipes (this palette, these moves)
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='afro_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
