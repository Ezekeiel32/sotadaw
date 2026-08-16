---
name: dariacore-arrangement
version: 3
kind: genre
tags: [dariacore, jerseyclub, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-200; set the song key (suggested: C major (sample-dictated)).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order mid>low>lowmid.
  - SAMPLE SWITCHUP WALL is non-negotiable: a NEW chipmunked pop-sample chop every 4-8 bars — key and subgenre can change at every switch; maximalist collage as form
  - JERSEY KICK AT 170 is non-negotiable: the Jersey 5-kick figure (0,4,8,11,14) sped to ~170 BPM as the constant under the chaos
  - CHIPMUNK CHOP LEAD is non-negotiable: pop vocals pitched way up and re-chopped into melodic stabs — the lead instrument is a mangled hook you almost recognize
---
# Dariacore arrangement (graph-compiled)

Dariacore is a child of **jerseyclub** — its groove laws apply unless overridden below.

## The pocket — collage_engine
Dariacore (~170 BPM): the Jersey 5-kick (0,4,8,11,14) clipped and relentless; claps 2&4; a NEW chipmunked pop-vocal chop every 4-8 bars (key/subgenre can flip at every switch); meme SFX placed as drums; supersaw + growl bass underneath; maximalist, exhausting, gleeful.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sample switchup wall** (w1.0): a NEW chipmunked pop-sample chop every 4-8 bars — key and subgenre can change at every switch; maximalist collage as form *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **jersey kick at 170** (w0.92): the Jersey 5-kick figure (0,4,8,11,14) sped to ~170 BPM as the constant under the chaos *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **chipmunk chop lead** (w0.84): pop vocals pitched way up and re-chopped into melodic stabs — the lead instrument is a mangled hook you almost recognize *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **meme sfx percussion** (w0.76): meme SFX (airhorns, vine booms, notification pings) placed AS drums on the grid *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **glitch interruption** (w0.68): THE digicore move: every 2-4 bars sabotage the grid — stutter-retrigger the last 16th (4-8 accelerating repeats), reverse a tail into the downbeat, or hard-gate a 1/4-beat silence pre-drop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from jerseyclub
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- club kick pattern: THE jersey 5-kick: 1, 1.5, 2.5, 3, 3.5 — dance instructions in kick form
- bed squeak chops: chopped vocal/stab on straight 8ths riding the kick pattern
- triplet break: bar-4 triplet kick fill (hands-up moment) before the pattern restarts
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- ...and from the jerseyclub skill itself: phrase aligned blend, bass swap, filter transition

## Sound recipes (this palette, these moves)
- **collage rig**: chipmunk chop stand-in = supersaw/formant_vox stabs pitched high re-sequenced; clipped Jersey kick (kick_punch + fx_saturate, or fx_crush bits 8 for digital edge); switch-up law: change the lead sample/key every 4-8 bars via sections; meme SFX = short pitched noise/vox hits on the grid

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='bounce_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (jersey/NOLA/new-jack hard 16th swing ~60%, triplet lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order mid>low>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
