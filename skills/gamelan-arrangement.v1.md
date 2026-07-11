---
name: gamelan-arrangement
version: 1
kind: genre
tags: [gamelan, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-200; set the song key (suggested: D pentatonic (slendro approx.)).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order mid>lowmid>low.
  - KOTEKAN INTERLOCK is non-negotiable: two parts (POLOS mostly on-beat + SANGSIH mostly off-beat) interlock into one stream twice as fast as either — Balinese kilitan-telu 3-note figures; neither player states the whole melody
  - COLOTOMIC CYCLE is non-negotiable: the structure is a nested gong cycle, NOT a backbeat: gong ageng marks the cycle END, kenong quarters it, kempul halves those, ketuk ticks the subdivisions — the strongest point is the cycle's last beat, not beat 1
  - OMBAK DETUNE is non-negotiable: voice every pitch as a PAIR a few Hz apart (pengumbang + pengisep) so the sum beats and shimmers — ~5 Hz gender, ~7 Hz gong kebyar, ~8-9 Hz angklung; the beating IS the sound, do not tune it out
---
# Gamelan arrangement (graph-compiled)

## The pocket — colotomic_kotekan
Cyclic colotomic gamelan (felt 4/4, 16-beat gongan, 0 swing): the low gong marks the CYCLE END (last slot), a mid gong quarters it; over it two metallophone parts INTERLOCK (polos + sangsih) into one fast cascade twice their individual speed; core-melody tones ring underneath. No chord changes, no backbeat pocket — momentum from repetition + ombak shimmer. [encode 16/32-beat cycles + slendro/pelog via microtuning; the grid approximates.]  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **kotekan interlock** (w1.0): two parts (POLOS mostly on-beat + SANGSIH mostly off-beat) interlock into one stream twice as fast as either — Balinese kilitan-telu 3-note figures; neither player states the whole melody *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **colotomic cycle** (w0.92): the structure is a nested gong cycle, NOT a backbeat: gong ageng marks the cycle END, kenong quarters it, kempul halves those, ketuk ticks the subdivisions — the strongest point is the cycle's last beat, not beat 1 *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **ombak detune** (w0.84): voice every pitch as a PAIR a few Hz apart (pengumbang + pengisep) so the sum beats and shimmers — ~5 Hz gender, ~7 Hz gong kebyar, ~8-9 Hz angklung; the beating IS the sound, do not tune it out *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **slendro pelog tuning** (w0.76): non-12-TET tuning: SLENDRO (5 near-equal ~240-cent steps) or PELOG (7 uneven steps played as 5-tone subsets); each ensemble tuned uniquely, no fixed reference pitch *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **irama density shift** (w0.68): tempo is a DENSITY level not a fixed pulse: as the drum slows the pulse, the elaborating instruments double their note-density to keep the surface busy (irama) *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **kendang cue** (w0.6): the hand-drum pair (lanang high + wadon low) LEADS — all tempo, transitions and the final ritard (suwuk) are cued by the drum, never a click *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **gamelan metallophone**: INHARMONIC struck bronze: use vibraphone/marimba/steel_pan as stand-ins, but voice every pitch as an OMBAK PAIR (two copies detuned ~5-9 Hz) for the shimmer; sharp attack, long ring. ELEVATE with new `gamelan_saron.dsp` (impulse -> 4-8 stretched-ratio resonant bandpasses ~1:2.76:5.40:8.93) + `ombak_pair.dsp` + `gamelan_gong.dsp` (low fundamental + partials + downward pitch-glide + long tail). Do NOT compress — the amplitude beating IS the sound.
- **gamelan gong**: the gong ageng at each cycle end: a deep slowly-beating sub fundamental + a downward pitch-glide; use sub_clean/timpani until gamelan_gong.dsp exists

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
