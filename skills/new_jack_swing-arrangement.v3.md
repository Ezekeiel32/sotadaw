---
name: new_jack_swing-arrangement
version: 3
kind: genre
tags: [new_jack_swing, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-115; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>low>mid.
  - SWINGBEAT MACHINE is non-negotiable: new jack swing: hard-quantized swung 16ths (SP-1200/MPC60 feel, swing ~0.58) + gated reverb snare + James Brown-lineage stab samples over R&B chords
  - GATED REVERB SNARE is non-negotiable: the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
---
# New_Jack_Swing arrangement (graph-compiled)

## The pocket — njs_swingbeat
swung machine 16ths + gated backbeat Swing 0.58 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **swingbeat machine** (w0.95): new jack swing: hard-quantized swung 16ths (SP-1200/MPC60 feel, swing ~0.58) + gated reverb snare + James Brown-lineage stab samples over R&B chords *(curated:claude/2026-07-03-w6)*
- **gated reverb snare** (w0.85): the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **swing 16th** (w0.8): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **m7 chords** (w0.7): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **horn stabs** (w0.6): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='bounce_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (jersey/NOLA/new-jack hard 16th swing ~60%, triplet lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
