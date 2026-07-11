---
name: soca-arrangement
version: 1
kind: genre
tags: [soca, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 155-165; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -9..-7, band order low>lowmid>mid.
  - SOCA ENGINE is non-negotiable: power soca: 4-floor at 155-165 + the IRON section (brake-drum/cowbell straight 8ths), steel pan riffs, jab-jab chant hooks — carnival velocity, no half-time anywhere
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Soca arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **soca engine** (w0.95): power soca: 4-floor at 155-165 + the IRON section (brake-drum/cowbell straight 8ths), steel pan riffs, jab-jab chant hooks — carnival velocity, no half-time anywhere *(curated:claude/2026-07-03-w13)*
- **four on floor** (w0.85): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **hat rolls** (w0.5): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **pan lead**: faust steel_pan: struck pan w/ octave halo + ping — soca/calypso riffs and leads; roll = fast low-vel repeats

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
