---
name: arabesk-arrangement
version: 1
kind: genre
tags: [arabesk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-110; set the song key (suggested: A Kurdi (Phrygian)).
  - Mix: clipped_samples == 0, LUFS -13..-10, band order lowmid>mid>low.
  - MASSED UNISON STRINGS is non-negotiable: a large string section playing the vocal melody in UNISON (no harmony) with heavy melisma — the arabesk/filmi orchestral cry
  - SAZ BAGLAMA ORNAMENT is non-negotiable: bağlama saz picks ornamented makam lines (Kurdi/Hicaz), answering the voice — Anatolian steel-string filigree
  - ISTIKHBAR RUBATO is non-negotiable: a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead
---
# Arabesk arrangement (graph-compiled)

## The pocket — arabesk_ballad
Arabesk (~88 BPM, düyek feel): darbuka lays dum-tek under massed strings playing the Kurdi/Hicaz melody in UNISON melisma; bağlama saz answers with ornamented filigree; sorrowful vocal pulls the tempo (rubato); free taksim intro. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **massed unison strings** (w1.0): a large string section playing the vocal melody in UNISON (no harmony) with heavy melisma — the arabesk/filmi orchestral cry *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **saz baglama ornament** (w0.92): bağlama saz picks ornamented makam lines (Kurdi/Hicaz), answering the voice — Anatolian steel-string filigree *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **istikhbar rubato** (w0.84): a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **saudade rubato** (w0.76): the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **arabesk orchestra**: massed strings = strings_stacc + strings_disco unison (NO harmony — one line, many voices); saz = pluck2 ornamented answers; darbuka = dhol + ticks; sorrow first: rubato intros, heavy melisma (neighbor-bend the lead)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
