---
name: country-arrangement
version: 1
kind: genre
tags: [country, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-130; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>mid>low.
  - TRAIN BEAT is non-negotiable: country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - TAPE SATURATION is non-negotiable: heavy fx_saturate drive 8-14 over the whole beat bus = grit
---
# Country arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **train beat** (w0.95): country train beat: brushed snare 16th chug (accent 2&4), boom-chick alternating bass (root-5th), ~0 swing — momentum from the chug, not from fills *(curated:claude/2026-07-03-w7)*
- **walking bass** (w0.7): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **tape saturation** (w0.5): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **twelve bar blues** (w0.5): the 12-bar form is the LAW: I-I-I-I / IV-IV-I-I / V-IV-I-V(turnaround), shuffle triplet feel (swing ~0.66), melody answers itself every 2 bars *(curated:claude/2026-07-03-w7)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
