---
name: chaabi-arrangement
version: 2
kind: genre
tags: [chaabi, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-120; set the song key (suggested: D Phrygian (Andalusi)).
  - Mix: clipped_samples == 0, LUFS -14..-11, band order lowmid>mid>low.
  - MANDOLE TREMOLO is non-negotiable: the chaabi mandole: double-course tremolo lead in Andalusi-derived modes, answered by banjo and violin unison
  - ISTIKHBAR RUBATO is non-negotiable: a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead
  - DERBOUKA DUM TEK is non-negotiable: derbouka engine: deep DUM on 1 and the and-of-2, dry TEK splashes on the offbeats, bendir frame-drum roll under — the Maghreb pocket
---
# Chaabi arrangement (graph-compiled)

## The pocket — chaabi_groove
Chaâbi (~104 BPM): free istikhbar intro, then the groove — derbouka dum on 1 + and-of-2, bendir under; mandole tremolo leads Andalusi modes answered by banjo/violin unison; storytelling vocal with melisma. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **mandole tremolo** (w1.0): the chaabi mandole: double-course tremolo lead in Andalusi-derived modes, answered by banjo and violin unison *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **istikhbar rubato** (w0.92): a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **derbouka dum tek** (w0.84): derbouka engine: deep DUM on 1 and the and-of-2, dry TEK splashes on the offbeats, bendir frame-drum roll under — the Maghreb pocket *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **melisma maqam vocal** (w0.76): melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **chaabi band**: mandole = pluck2 double-course tremolo; banjo = pluck bright; violin unison = strings_stacc; derbouka = dhol tight + tick lane; open FREE (istikhbar) before the groove

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
