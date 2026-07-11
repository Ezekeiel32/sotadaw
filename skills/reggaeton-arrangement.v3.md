---
name: reggaeton-arrangement
version: 3
kind: genre
tags: [reggaeton, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-98; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-6, band order low>lowmid>mid.
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
  - PERREO BASS is non-negotiable: sub doubling the kick roots, short, dark
  - GROOVE DEMBOW LILT is non-negotiable: apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean.
---
# Reggaeton arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **dembow rhythm** (w0.95): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **perreo bass** (w0.85): sub doubling the kick roots, short, dark *(curated:claude/2026-07-02)*
- **groove dembow lilt** (w0.8): apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **brickwall mastering** (w0.6): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **vocal chops** (w0.5): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dembow_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (3-3-2 lean: pushed 'a' of 2 and 4))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
