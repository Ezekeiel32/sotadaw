---
name: pluggnb-arrangement
version: 2
kind: genre
tags: [pluggnb, plugg, cloud_rap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-78; set the song key (suggested: Eb major (min9 loops)).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - RNB GOSPEL LOOP is non-negotiable: maj9/min9/add9 gospel-R&B keyboard loops (DX7 tine e-piano, glassy bells) — pluggnb's harmonic bed, 2-4 chords cycling
  - PLUGG BELL PALETTE is non-negotiable: airy FM glass bells, synth flutes and soft plucks carry the melody — spacey, toy-like, LOW-PASSED soft; the beat feels weightless over hard 808s
  - GLIDING 808 MELODY is non-negotiable: the 808 voice-leads (root -> third/fifth glides) under the chords — bass as the counter-melody, portamento audible
---
# Pluggnb arrangement (graph-compiled)

Pluggnb is a child of **plugg, cloud_rap** — its groove laws apply unless overridden below.

## The pocket — pluggnb_loop
PluggnB (~138 BPM, half-time, hats swung ~60%): a maj9/min9 gospel-R&B keys loop (DX tine e-piano + glassy bells) cycles 2-4 chords; octave-skip kicks + denser 32nd hat rolls than plugg; 808 voice-leads root->third; clap tucked on 3; pitched vocal topline melody. Swing 0.6 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rnb gospel loop** (w1.0): maj9/min9/add9 gospel-R&B keyboard loops (DX7 tine e-piano, glassy bells) — pluggnb's harmonic bed, 2-4 chords cycling *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **plugg bell palette** (w0.92): airy FM glass bells, synth flutes and soft plucks carry the melody — spacey, toy-like, LOW-PASSED soft; the beat feels weightless over hard 808s *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **gliding 808 melody** (w0.84): the 808 voice-leads (root -> third/fifth glides) under the chords — bass as the counter-melody, portamento audible *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **muffled clap 3** (w0.76): the plugg backbeat: ONE muffled, low-passed clap/snare on beat 3 (half-time), tucked under the melody instead of cracking over it *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **pitched vocal topline** (w0.68): Auto-Tuned melodic rap-sung topline, often pitched up, doubled in octaves — the voice is an instrument riding the loop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from plugg, cloud_rap
- beat skip dropout: whole-beat DROPOUTS: the kick/808 skips a beat (or a whole bar goes drumless) so the loop breathes — the skip IS the hook

## Sound recipes (this palette, these moves)
- **pluggnb keys**: DX7-tine e-piano (rhodes) playing maj9/min9 gospel loops + fmbell glass on top; kick_808 gliding; soft muffled clap; keep it GLOSSY and warm — R&B in plugg clothes

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
