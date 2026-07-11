---
name: automotivo-arrangement
version: 1
kind: genre
tags: [automotivo, baile_funk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-180; set the song key (suggested: F minor (anti-harmonic)).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order low>lowmid>mid.
  - DOUBLE TRESILLO KICK is non-negotiable: the automotivo engine: tresillo kick doubled per bar (slots 1, 1.75, 2.5 + 3, 3.75, 4.5) — relentless 3+3+2 x2 propulsion
  - TUIN SIREN is non-negotiable: the TUIN: a piercing sliding sine/square siren blip looped as the lead hook — Brazilian funk's signature synth cry
  - VOCAL SHARD PERCUSSION is non-negotiable: chopped chipmunked vocal stabs placed AS percussion on the 16th grid — syllables become drums
---
# Automotivo arrangement (graph-compiled)

Automotivo is a child of **baile_funk** — its groove laws apply unless overridden below.

## The pocket — double_tresillo
Automotivo/bruxaria (~150 BPM): the double-tresillo kick — slots 1, 1.75, 2.5 / 3, 3.75, 4.5 (grid 0,3,6,8,11,14) — claps on 2&4; a piercing TUIN sine-siren loops the hook; chipmunked vocal shards fill 16th slots AS percussion; arrangement = whole-mix MUTES then slam-backs. Bruxaria = darker: one huge distorted kick on 1 dominates, texture driven into saturation (master stays soft-clipped, clipped_samples 0).  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **double tresillo kick** (w1.0): the automotivo engine: tresillo kick doubled per bar (slots 1, 1.75, 2.5 + 3, 3.75, 4.5) — relentless 3+3+2 x2 propulsion *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **tuin siren** (w0.92): the TUIN: a piercing sliding sine/square siren blip looped as the lead hook — Brazilian funk's signature synth cry *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **vocal shard percussion** (w0.84): chopped chipmunked vocal stabs placed AS percussion on the 16th grid — syllables become drums *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **bruxaria clip wall** (w0.76): bruxaria aesthetic: ONE huge distorted reverberated kick dominates beat 1, everything driven into clipping/saturation as a texture (keep the DAW master soft-clipped, clipped_samples 0) *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **mute slamback** (w0.68): arrangement by MUTES: whole-mix cuts for 1-2 beats then a slam-back — the drop grammar of funk DJ tools *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from baile_funk
- memphis chant: dark chopped vocal stab as rhythmic texture (sample kit / choir low)
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- sparse kick: kick on 1 and ~3.5 only; space carries the bounce
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- tamborzao: baile funk's tamborzao drum bed: syncopated 808/tom pattern under 130bpm MC chants — kick-tom dialogue, minimal melody
- hemiola 3 2: 3:2 cross-rhythm — two bars of 3 heard as three bars of 2 (or within-bar 3-against-2); the lift beneath afro-latin grooves [Rhythm & meter: hemiola]

## Sound recipes (this palette, these moves)
- **tuin**: the TUIN siren = a bare sine/square (test_sine/chiptune_pulse) sliding octave blips — pierce it through; distorted 808 kick (kick_808 + fx_saturate hard); chopped formant_vox stabs as percussion; drive the bus into fx_softclip for the bruxaria wall — NEVER hard-clip the master

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
