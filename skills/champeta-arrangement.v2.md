---
name: champeta-arrangement
version: 2
kind: genre
tags: [champeta, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-170; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - PICO GUITAR LOOP is non-negotiable: a looping bright soukous-style guitar riff (2-4 bars) carries the whole track — the pico soundsystem inheritance
  - ESPELUQUE BREAK is non-negotiable: el espeluque: the percussion-and-vocal breakdown where the beat strips to perc + chant — champeta's drop
  - DEMBOW PERC BED is non-negotiable: a dembow-leaning perc bed (boom-ch-boom-chick) under the guitar loop; modern urbana adds the reggaeton kit outright
---
# Champeta arrangement (graph-compiled)

## The pocket — pico_loop
Champeta (~130 BPM): a looping bright soukous-style guitar riff (2-4 bars) over a dembow-leaning perc bed (kick 0/3/8/11 boom-ch-boom-chick), chanted costeño vocals; EL ESPELUQUE = strip to percussion + chant, then slam the loop back; urbana variant adds the reggaeton kit. [BPM verified inline 2026-07-06, see doc addendum.] Swing 0.53 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **pico guitar loop** (w1.0): a looping bright soukous-style guitar riff (2-4 bars) carries the whole track — the pico soundsystem inheritance *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **espeluque break** (w0.92): el espeluque: the percussion-and-vocal breakdown where the beat strips to perc + chant — champeta's drop *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **dembow perc bed** (w0.84): a dembow-leaning perc bed (boom-ch-boom-chick) under the guitar loop; modern urbana adds the reggaeton kit outright *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **atalaku shout lead** (w0.76): chanted shouts and crowd commands lead the track (the atalaku lineage from soukous) — vocals as percussion *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **pico rig**: the guitar loop = pluck bright cycling (soukous inheritance, graph edge); dembow perc bed; bass_warm simple; espeluque = arrangement mute-to-perc; urbana = swap kit to kick_808 + reggaeton snare

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
