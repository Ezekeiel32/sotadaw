---
name: bounce-arrangement
version: 1
kind: genre
tags: [bounce, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-105; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - TRIGGERMAN BOUNCE is non-negotiable: NOLA bounce: the Triggerman cell (bells + claps) looped relentlessly ~100bpm, call-and-response party shouts, dance-command vocals — the loop IS the song
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Bounce arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **triggerman bounce** (w0.95): NOLA bounce: the Triggerman cell (bells + claps) looped relentlessly ~100bpm, call-and-response party shouts, dance-command vocals — the loop IS the song *(curated:claude/2026-07-03-w12)*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **hat rolls** (w0.5): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
