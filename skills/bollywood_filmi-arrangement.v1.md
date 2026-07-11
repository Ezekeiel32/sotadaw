---
name: bollywood_filmi-arrangement
version: 1
kind: genre
tags: [bollywood_filmi, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-140; set the song key (suggested: C harmonic minor (Bhairavi)).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - KEHERWA THEKA is non-negotiable: the 8-beat Keherwa taal on dholak/tabla: Bhari (full, weighted) across beats 1-4 and the KHALI (empty, marked) on beat 5 — the default filmi dance groove with its rolling bounce
  - PLAYBACK VOCAL STACK is non-negotiable: big, up-front lead 'playback' vocals (often doubled/harmonized male+female) are the star — everything is arranged to frame the sung melody
  - BANSURI RAGA LEAD is non-negotiable: a bamboo bansuri flute (or sitar) carries a raga-flavored melodic hook — Bhairavi / harmonic-minor color and gamak ornament over the groove
---
# Bollywood_Filmi arrangement (graph-compiled)

## The pocket — keherwa_filmi
Modern filmi (Keherwa 8-beat, ~100 BPM): dholak/tabla lay the theka — weighted Bhari across beats 1-4, KHALI marked on beat 5 — with a rolling bounce; a bansuri/sitar raga hook (Bhairavi/harmonic-minor) over lush strings + brass, a tanpura tonic drone grounding it, and a modern 808 / four-on-the-floor dance layer under big doubled playback vocals. Max BPM ~140 for dance numbers.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **keherwa theka** (w1.0): the 8-beat Keherwa taal on dholak/tabla: Bhari (full, weighted) across beats 1-4 and the KHALI (empty, marked) on beat 5 — the default filmi dance groove with its rolling bounce *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **playback vocal stack** (w0.92): big, up-front lead 'playback' vocals (often doubled/harmonized male+female) are the star — everything is arranged to frame the sung melody *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **bansuri raga lead** (w0.84): a bamboo bansuri flute (or sitar) carries a raga-flavored melodic hook — Bhairavi / harmonic-minor color and gamak ornament over the groove *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **filmi orchestral hybrid** (w0.76): lush strings + brass + tabla/dholak fused with modern 808s, four-on-the-floor or trap layers — cinematic maximalism, genres stacked in one song *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **tanpura tonic drone** (w0.68): a sustained tanpura/tambura tonic-fifth drone underpins the tonality, grounding the modal/raga melody *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **filmi bed**: bansuri = flute_lead (raga hook + gamak); cine_brass + strings_disco/strings_stacc for the orchestral maximalism; tanpura_drone under everything; dholak/tabla (kick_punch/timpani + tight snare) for Keherwa; kick_808 for the modern layer.
- **playback vox**: big doubled/harmonized lead vocals up front (formant_vox/vox_pad as synth stand-in; real vocal via tune_vocal) — the song frames the sung melody

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
