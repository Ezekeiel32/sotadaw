---
name: dangdut-arrangement
version: 1
kind: genre
tags: [dangdut, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-140; set the song key (suggested: A minor (Hijaz color)).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - GENDANG DANGDUT FIGURE is non-negotiable: THE dangdut signature: the gendang plays a low pickup 'dang' late in the bar into the high 'DUT' on the downbeat (slots ~12/14 -> 0) — the sway lives in that pickup
  - CENGKOK VIBRATO VOCAL is non-negotiable: wailing melismatic vocal with heavy slow vibrato and note-bends (cengkok) — the melody is 70% ornament
  - SULING ANSWER is non-negotiable: a breathy suling flute answers every vocal phrase in the gaps
---
# Dangdut arrangement (graph-compiled)

## The pocket — dang_dut
Dangdut (~112 BPM): THE gendang figure — low 'dang' pickup at slots 12/14 rolling into the high 'DUT' on the downbeat; kick anchors 1&3, offbeat hats sway; suling flute answers the wailing cengkok vocal; minor/Hijaz-tinged Melayu melody; koplo variant runs hotter with busier gendang rolls. Swing 0.53 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gendang dangdut figure** (w1.0): THE dangdut signature: the gendang plays a low pickup 'dang' late in the bar into the high 'DUT' on the downbeat (slots ~12/14 -> 0) — the sway lives in that pickup *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **cengkok vibrato vocal** (w0.92): wailing melismatic vocal with heavy slow vibrato and note-bends (cengkok) — the melody is 70% ornament *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **suling answer** (w0.84): a breathy suling flute answers every vocal phrase in the gaps *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **four on floor club layer** (w0.76): modern UK/club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol/tumbi — folk on a dancefloor engine *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **dangdut kit**: suling = flute_lead breathy answers; gendang = dhol two-voiced (low bend 'dang' + tight high 'dut'); modern koplo layer = kick_808 four-floor under the acoustic figure; vocal melody 70% ornament (write neighbor bends)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
