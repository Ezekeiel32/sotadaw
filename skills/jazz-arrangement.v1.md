---
name: jazz-arrangement
version: 1
kind: genre
tags: [jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-220; set the song key (suggested: Bb major).
  - Mix: clipped_samples == 0, LUFS -18..-12, band order lowmid>mid>low.
  - SWING RIDE is non-negotiable: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - JAZZ COMPING is non-negotiable: piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th
---
# Jazz arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **swing ride** (w0.95): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **walking bass** (w0.9): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **jazz comping** (w0.9): piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th *(curated:claude/2026-07-03-w7)*
- **m7 chords** (w0.8): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-12, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
