---
name: khaleeji-arrangement
version: 2
kind: genre
tags: [khaleeji, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-125; set the song key (suggested: C Bayati (maqam)).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order lowmid>mid>low.
  - SAWT KHALEEJI LIMP is non-negotiable: the khaleeji 6/8-over-2 sawt lilt: layered hand percussion (tabla + duff frame drums) with a distinctive limping accent — the Gulf pocket
  - MASSED UNISON STRINGS is non-negotiable: a large string section playing the vocal melody in UNISON (no harmony) with heavy melisma — the arabesk/filmi orchestral cry
  - MELISMA MAQAM VOCAL is non-negotiable: melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line
---
# Khaleeji arrangement (graph-compiled)

## The pocket — sawt_limp
Khaleeji (~118 BPM): the sawt 6/8-over-2 LIMP — layered hand percussion (tabla + duff frames) accenting the lopsided pocket (kick 1 & 4th-triplet, claps answer); oud + massed strings state the maqam melody in unison; ornamented vocal above. [BPM verified inline: typ ~120, 6/12-beat iqa'at confirmed.] Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sawt khaleeji limp** (w1.0): the khaleeji 6/8-over-2 sawt lilt: layered hand percussion (tabla + duff frame drums) with a distinctive limping accent — the Gulf pocket *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **massed unison strings** (w0.92): a large string section playing the vocal melody in UNISON (no harmony) with heavy melisma — the arabesk/filmi orchestral cry *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **melisma maqam vocal** (w0.84): melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **istikhbar rubato** (w0.76): a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Sound recipes (this palette, these moves)
- **gulf ensemble**: oud = pluck2 warm; massed strings = strings_stacc unison doubling the melody; tabla+duff = dhol + frame ticks layered (the limp lives in the velocities); ornament the lead heavily

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
