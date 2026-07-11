---
name: soukous-arrangement
version: 1
kind: genre
tags: [soukous, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-145; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order mid>lowmid>low.
  - SEBENE SECTION is non-negotiable: the SEBENE: the fast, euphoric instrumental peak where interlocking lead guitars cycle a bright major riff over a driving groove while an atalaku shouts animations — the payoff of the song
  - CAVACHA CHURN is non-negotiable: the cavacha drum pattern: a continuous ghosted-16th snare/hi-hat churn with the backbeat on 2 & 4 and a near-every-beat kick — the rolling engine of Congolese dance music
  - INTERLOCKING GUITARS is non-negotiable: three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony
---
# Soukous arrangement (graph-compiled)

## The pocket — sebene
Soukous SEBENE (~128 BPM, 4/4, light triplet-vs-16th lilt ~54%): the cavacha churn (ghosted-16th snare/hat + backbeat 2&4 + near-every-beat kick) drives three interlocking guitars in different registers cycling a bright major riff; static I-IV-V or one-chord vamp; atalaku shouts punctuate. Euphoric, fast, guitar-led. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sebene section** (w1.0): the SEBENE: the fast, euphoric instrumental peak where interlocking lead guitars cycle a bright major riff over a driving groove while an atalaku shouts animations — the payoff of the song *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **cavacha churn** (w0.92): the cavacha drum pattern: a continuous ghosted-16th snare/hi-hat churn with the backbeat on 2 & 4 and a near-every-beat kick — the rolling engine of Congolese dance music *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **interlocking guitars** (w0.84): three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **atalaku animation** (w0.76): an animateur's rhythmic shouts and crowd-cries punctuate the sebene, cueing the dancers and lifting the energy *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **static major harmony** (w0.68): a bright, static major (Ionian) I-IV-V or single-chord vamp — harmony stays put so the guitar interlock and groove carry everything *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **soukous guitars**: three CLEAN interlocking guitars: bright lead (pluck octave 5), mid mi-solo (pluck2), rhythm (pluck octave 4) — light fx_delay + small reverb, NO fuzz; bass_warm; cavacha kit (snare/hat churn). The interlock is the harmony.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
