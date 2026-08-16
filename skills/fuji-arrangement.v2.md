---
name: fuji-arrangement
version: 2
kind: genre
tags: [fuji, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-135; set the song key (suggested: C major (vocal-modal)).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order lowmid>low>mid.
  - PERCUSSION ONLY ENSEMBLE is non-negotiable: fuji law: NO harmony instruments — layered talking drums, shekere and bells ARE the arrangement; melody lives in the voice and the drum bends
  - LAYERED TALKING DRUMS is non-negotiable: multiple talking-drum voices at different registers converse (lead drum speaks, others answer) — write 2-3 bending drum tracks in dialogue
  - PRAISE CALL RESPONSE is non-negotiable: leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping
---
# Fuji arrangement (graph-compiled)

## The pocket — fuji_orchestra
Fuji (~116 BPM, 12/8 undercurrent — swing .58): NO harmony instruments — layered talking drums converse (lead drum speaks slots 0/3/6/11, answers at 8/14), shekere rides 8ths, agogo bell ticks; Islamic-tinged praise melisma leads, chorus answers; the drums ARE the arrangement. Swing 0.58 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **percussion only ensemble** (w1.0): fuji law: NO harmony instruments — layered talking drums, shekere and bells ARE the arrangement; melody lives in the voice and the drum bends *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **layered talking drums** (w0.92): multiple talking-drum voices at different registers converse (lead drum speaks, others answer) — write 2-3 bending drum tracks in dialogue *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **praise call response** (w0.84): leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **shekere eighths** (w0.76): shekere/beaded-gourd rides straight 8ths with hand accents — the juju timekeeper *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **fuji drums**: 2-3 dhol tracks at different pitches IN DIALOGUE (ride the bend zone — they speak); log_drum accents; shekere = hat 8ths; agogo = hat_metal; lead = formant_vox melisma + chorus answers; NO chords, no bass guitar — percussion carries everything

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='afro_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
