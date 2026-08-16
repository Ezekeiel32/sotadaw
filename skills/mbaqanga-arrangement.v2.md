---
name: mbaqanga-arrangement
version: 2
kind: genre
tags: [mbaqanga, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-130; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order lowmid>low>mid.
  - MARABI CYCLE is non-negotiable: the marabi harmonic engine: I - IV - I6/4 - V cycling FOREVER (no bridge, no key change) — South African township perpetual motion
  - GROANER BASS VOCAL is non-negotiable: the GROANER: a huge gravel bass voice answering the sweet girl-group hook — register contrast as arrangement
  - JANGLY CYCLE GUITAR is non-negotiable: a bright clean lead guitar picks short cyclic lines over the cycle, more riff than solo
---
# Mbaqanga arrangement (graph-compiled)

## The pocket — township_jive
Mbaqanga (~118 BPM): four-square stomp — kick all four, snare cracks 2&4, organ/sax stabs offbeats; the marabi cycle I-IV-I6/4-V loops FOREVER; jangly clean guitar picks cyclic lines; the groaner bass voice answers the girl-group hook (register contrast = the arrangement). Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **marabi cycle** (w1.0): the marabi harmonic engine: I - IV - I6/4 - V cycling FOREVER (no bridge, no key change) — South African township perpetual motion *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **groaner bass vocal** (w0.92): the GROANER: a huge gravel bass voice answering the sweet girl-group hook — register contrast as arrangement *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **jangly cycle guitar** (w0.84): a bright clean lead guitar picks short cyclic lines over the cycle, more riff than solo *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **township foursquare** (w0.76): four-square stomp: kick on all four, snare cracking 2 & 4, organ/sax stabs on the offbeats — dance-floor steady, never busy *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **township band**: jangly lead = pluck bright cyclic; organ_soul offbeat stabs + sax_section riffs; the groaner = a LOW bass_warm/formant_vox counter-voice; four-square kit, warm and danceable — the direct ancestor of kwaito (edge in graph)

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='afro_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
