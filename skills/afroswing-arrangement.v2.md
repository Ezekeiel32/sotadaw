---
name: afroswing-arrangement
version: 2
kind: genre
tags: [afroswing, afrobeats, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-115; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-8, band order low>lowmid>mid.
  - AFROSWING BOUNCE is non-negotiable: kick on 1 + the 'a' of 2 (slot 2.75), rim/snare on 3 (often dragged late), swung shakers/hats ~55-64% — the UK afrobeats lilt under rap-sung melody
  - MELODIC 808 SUB is non-negotiable: a warm, round, MELODIC 808 sub playing the bassline (not just roots) — kick+bass anchored while everything else swings
  - MALLET PLUCK HOOK is non-negotiable: marimba/mallet/steel-ish FM plucks play the instrumental hook — sunny, bouncing, West-African-tinged
---
# Afroswing arrangement (graph-compiled)

Afroswing is a child of **afrobeats** — its groove laws apply unless overridden below.

## The pocket — afroswing_bounce
Afroswing (~102 BPM, hats swung ~58%): kick on 1 + the 'a' of 2 (slot 7), rim/snare on 3 (dragged a touch late), swung shakers and offbeat hats; a warm MELODIC 808 sub plays the bassline; marimba/mallet FM plucks bounce the hook; rap-sung melodic topline. Swing 0.58 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **afroswing bounce** (w1.0): kick on 1 + the 'a' of 2 (slot 2.75), rim/snare on 3 (often dragged late), swung shakers/hats ~55-64% — the UK afrobeats lilt under rap-sung melody *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **melodic 808 sub** (w0.92): a warm, round, MELODIC 808 sub playing the bassline (not just roots) — kick+bass anchored while everything else swings *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **mallet pluck hook** (w0.84): marimba/mallet/steel-ish FM plucks play the instrumental hook — sunny, bouncing, West-African-tinged *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **pitched vocal topline** (w0.76): Auto-Tuned melodic rap-sung topline, often pitched up, doubled in octaves — the voice is an instrument riding the loop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from afrobeats
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- log drum bass: melodic percussive bass hits (short sub notes walking the scale) — the amapiano/afro signature
- triplet percs: 3:2 cross-rhythm percussion over a straight kick — rims/toms/shaker
- sparse kick: kick on 1 and ~3.5 only; space carries the bounce
- call response melody: 2-bar call, 2-bar answer; melody talks to itself
- groove dembow lilt: apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean.

## Sound recipes (this palette, these moves)
- **afroswing kit**: marimba/kalimba mallet plucks for the hook; warm melodic sub (sub_clean/bass_warm) NOT aggressive; rimshot snare + shaker hats swung; sunny, bouncing, space between hits

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='afro_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
