---
name: miami_bass-arrangement
version: 2
kind: genre
tags: [miami_bass, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-135; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>lowmid>mid.
  - BOOTY 808 is non-negotiable: miami bass: the TR-808 kick IS the bassline — tuned kick call-response with sub drops, 130bpm 16th hats, electro claps; rap call-and-response on top
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - HAT ROLLS is non-negotiable: 16th->32nd bursts at phrase ends; velocity ramps
---
# Miami_Bass arrangement (graph-compiled)

## The pocket — mia_electro
miami_bass loop DNA (wave14)  *(source: curated:claude/2026-07-04 + grid:curated (wave14 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **booty 808** (w0.95): miami bass: the TR-808 kick IS the bassline — tuned kick call-response with sub drops, 130bpm 16th hats, electro claps; rap call-and-response on top *(curated:claude/2026-07-03-w6)*
- **call response melody** (w0.75): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **hat rolls** (w0.7): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **electro boogie** (w0.7): Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor *(curated:claude/2026-07-03)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
