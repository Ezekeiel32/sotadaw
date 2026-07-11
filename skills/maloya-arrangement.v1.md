---
name: maloya-arrangement
version: 1
kind: genre
tags: [maloya, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-135; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -13..-10, band order low>lowmid>mid.
  - ROULEUR TRANCE PULSE is non-negotiable: the maloya rouleur: a deep drum pulse on the 6/8 groups with kayamb shaker wash — hypnotic minor call-response chant over cycles (island trance)
  - PRAISE CALL RESPONSE is non-negotiable: leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping
  - HYPNOTIC REPETITION is non-negotiable: an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom)
---
# Maloya arrangement (graph-compiled)

## The pocket — maloya_trance
Maloya (~118 BPM, 6/8 trance — swing .66): the rouleur bass drum pulses the group heads, kayamb flat-shaker washes every pulse, pikér ticks; minor call-response chant cycles hypnotically; percussion + voices only (the banned island blues) — build by adding voices, never chords. Swing 0.66 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rouleur trance pulse** (w1.0): the maloya rouleur: a deep drum pulse on the 6/8 groups with kayamb shaker wash — hypnotic minor call-response chant over cycles (island trance) *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **praise call response** (w0.92): leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **hypnotic repetition** (w0.84): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **percussion only ensemble** (w0.76): fuji law: NO harmony instruments — layered talking drums, shekere and bells ARE the arrangement; melody lives in the voice and the drum bends *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Sound recipes (this palette, these moves)
- **maloya circle**: rouleur = dhol DEEP pulse; kayamb = hat 16th wash (loose vel); chant lead = formant_vox + chorus answers; darker minor cousin of sega; hypnotic — let it cycle, add voices as the build

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
