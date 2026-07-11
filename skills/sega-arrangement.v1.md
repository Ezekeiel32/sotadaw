---
name: sega-arrangement
version: 1
kind: genre
tags: [sega, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-125; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -13..-10, band order lowmid>mid>low.
  - RAVANNE ROLL is non-negotiable: the sega ravanne: a frame-drum roll figure leaning into beat 1 of each 6/8 group, maravanne shaker washing, triangle ticking the pulse
  - SODADE BALLAD LILT is non-negotiable: morna's habanera-leaning lilt: the bass leans on 1 and the and-of-2, arpeggios fill — unhurried, the voice sits BEHIND the beat
  - BOLIYAN CALL RESPONSE is non-negotiable: call-and-response folk vocals (boliyan) traded over the groove; hooky, chant-like, energetic
---
# Sega arrangement (graph-compiled)

## The pocket — sega_sway
Sega (~112 BPM, 6/8 — swing .66): the ravanne frame-drum roll leans into each group head, maravanne shaker washes, triangle ticks; major-leaning creole melody sways call-response; no stomp — a sway. ⚠BPM flagged (model-knowledge). Swing 0.66 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **ravanne roll** (w1.0): the sega ravanne: a frame-drum roll figure leaning into beat 1 of each 6/8 group, maravanne shaker washing, triangle ticking the pulse *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **sodade ballad lilt** (w0.92): morna's habanera-leaning lilt: the bass leans on 1 and the and-of-2, arpeggios fill — unhurried, the voice sits BEHIND the beat *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **boliyan call response** (w0.84): call-and-response folk vocals (boliyan) traded over the groove; hooky, chant-like, energetic *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **sega kit**: ravanne = dhol low with a roll lean (write grace notes into velocities); triangle = hat_metal tick; maravanne = hat wash; bright pluck melodies; sunny island sway, dynamic

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
