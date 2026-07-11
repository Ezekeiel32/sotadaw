---
name: swing_bigband-arrangement
version: 1
kind: genre
tags: [swing_bigband, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-220; set the song key (suggested: Bb major).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - BIGBAND SHOUT is non-negotiable: big band: the SHOUT chorus — full horn soli in block harmony over walking bass + swing ride; sections converse (saxes call, brass answer), dynamics terraced not gradual
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - SWING RIDE is non-negotiable: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
---
# Swing_Bigband arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **bigband shout** (w0.95): big band: the SHOUT chorus — full horn soli in block harmony over walking bass + swing ride; sections converse (saxes call, brass answer), dynamics terraced not gradual *(curated:claude/2026-07-03-w10)*
- **walking bass** (w0.9): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **swing ride** (w0.9): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **horn stabs** (w0.7): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
