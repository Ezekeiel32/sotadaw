---
name: coupe_decale-arrangement
version: 1
kind: genre
tags: [coupe_decale, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-135; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - ROLLING TOM DECALE is non-negotiable: four-floor kick + ROLLING tom/perc figures filling the offbeats — the percussion IS the melody hook
  - ATALAKU SHOUT LEAD is non-negotiable: chanted shouts and crowd commands lead the track (the atalaku lineage from soukous) — vocals as percussion
  - DROP TO DRUMS is non-negotiable: the decale drop: everything mutes except drums + shout, then slams back — arrangement by subtraction
---
# Coupe_Decale arrangement (graph-compiled)

## The pocket — decale_roll
Coupé-décalé (~128 BPM): four-floor kick + ROLLING tom/perc figures filling the offbeats (slots 2/5/10/13) — the percussion IS the hook; one-chord major harmony; chanted shouts lead; the drop strips to drums + shout then slams back. ⚠BPM range flagged for eval verification. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rolling tom decale** (w1.0): four-floor kick + ROLLING tom/perc figures filling the offbeats — the percussion IS the melody hook *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **atalaku shout lead** (w0.92): chanted shouts and crowd commands lead the track (the atalaku lineage from soukous) — vocals as percussion *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **drop to drums** (w0.84): the decale drop: everything mutes except drums + shout, then slams back — arrangement by subtraction *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **static major harmony** (w0.76): a bright, static major (Ionian) I-IV-V or single-chord vamp — harmony stays put so the guitar interlock and groove carry everything *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **decale kit**: rolling toms = timpani pitched mid + log_drum accents; marimba perc-melody hook; shouts = formant_vox stabs; synth-brass = brass_stab; the DROP = mute all but drums+shout (arrangement law)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
