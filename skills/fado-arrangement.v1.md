---
name: fado-arrangement
version: 1
kind: genre
tags: [fado, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-140; set the song key (suggested: A minor (fado menor)).
  - Mix: clipped_samples == 0, LUFS -18..-13, band order lowmid>mid>low.
  - GUITARRA TREMOLO is non-negotiable: the guitarra portuguesa (12-string, teardrop): bright cascading tremolo and turn ornaments answering the voice in the gaps — the sound of fado
  - SAUDADE RUBATO is non-negotiable: the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom
  - FADO MENOR CADENCE is non-negotiable: the fado-menor minor mood: a i - V(7) harmonic-minor pull with the raised leading tone, resolving with a heavy final V-i 'full stop'
---
# Fado arrangement (graph-compiled)

## The pocket — fado_menor
Fado (percussionless, ~88 BPM but RUBATO): voice + two guitars only. Viola (classical guitar) lays a steady fingered strum + bass line; the guitarra portuguesa (12-string) answers with bright cascading tremolo filigree in the vocal gaps; harmonic-minor i - V(7) - i with a heavy final full-stop cadence. The voice pulls and pushes the tempo (saudade). Intimate, dynamic, no drums.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **guitarra tremolo** (w1.0): the guitarra portuguesa (12-string, teardrop): bright cascading tremolo and turn ornaments answering the voice in the gaps — the sound of fado *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **saudade rubato** (w0.92): the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **fado menor cadence** (w0.84): the fado-menor minor mood: a i - V(7) harmonic-minor pull with the raised leading tone, resolving with a heavy final V-i 'full stop' *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **viola strum** (w0.76): the viola (classical guitar) lays a steady fingered strum + bass line under the guitarra's filigree — the harmonic and rhythmic anchor *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **percussionless intimacy** (w0.68): NO drums: the pulse lives entirely in the strummed viola and the singer's phrasing; arrangement is voice + two guitars, intimate and dynamic *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **fado guitars**: guitarra portuguesa = pluck2 (bright 12-string tremolo cascades) answering the voice; viola = pluck (fingered strum + bassline); viola baixo / upright_bass for the low. NO percussion. A short intimate room reverb; keep it very dynamic (high crest). Real vocal via tune_vocal with rubato preserved.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
