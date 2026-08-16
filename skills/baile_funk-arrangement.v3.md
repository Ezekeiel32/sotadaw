---
name: baile_funk-arrangement
version: 3
kind: genre
tags: [baile_funk, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-135; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>mid>lowmid.
  - TAMBORZAO is non-negotiable: baile funk's tamborzao drum bed: syncopated 808/tom pattern under 130bpm MC chants — kick-tom dialogue, minimal melody
  - LOUDNESS RECOVERY is non-negotiable: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Baile_Funk arrangement (graph-compiled)

## The pocket — tamborzao
baile_funk loop DNA (wave14)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tamborzao** (w0.95): baile funk's tamborzao drum bed: syncopated 808/tom pattern under 130bpm MC chants — kick-tom dialogue, minimal melody *(curated:claude/2026-07-03)*
- **loudness recovery** (w0.8): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **vocal chops** (w0.7): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **hemiola 3 2** (w0.7): 3:2 cross-rhythm — two bars of 3 heard as three bars of 2 (or within-bar 3-against-2); the lift beneath afro-latin grooves [Rhythm & meter: hemiola] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **sparse kick** (w0.6): kick on 1 and ~3.5 only; space carries the bounce *(curated:claude/2026-07-02)*
- **brickwall mastering** (w0.6): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **memphis chant** (w0.5): dark chopped vocal stab as rhythmic texture (sample kit / choir low) *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dembow_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (3-3-2 lean: pushed 'a' of 2 and 4))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
