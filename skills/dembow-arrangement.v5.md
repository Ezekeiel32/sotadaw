---
name: dembow-arrangement
version: 5
kind: genre
tags: [dembow, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 88-100; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - DEMBOW RHYTHM is non-negotiable: kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine
  - PERREO BASS is non-negotiable: sub doubling the kick roots, short, dark
  - GROOVE DEMBOW LILT is non-negotiable: apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean.
  - WARP BEATMATCH is non-negotiable: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
  - FORBIDDEN: echo out cut — beyond ~16% tempo distance: echo-out/cut transition (fx_delay feedback tail on the outgoing deck), not a long blend
---
# Dembow arrangement (graph-compiled)

## The pocket — dembow_grid
reggaeton loop DNA (wave14)  *(source: curated:claude/2026-07-04 + grid:curated (wave14 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dembow rhythm** (w1.0): kick 1/2/3/4 + snare-rim on the 3-3-2 lilt (~1.75 and ~3.75) — the perreo engine *(curated:claude/2026-07-02)*
- **perreo bass** (w0.92): sub doubling the kick roots, short, dark *(curated:claude/2026-07-02)*
- **groove dembow lilt** (w0.9): apply_groove('dembow_lilt', amount 0.7-1.0) on percs - the 3-3-2 lean. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **warp beatmatch** (w0.9): beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **phrase aligned blend** (w0.85): transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **vocal chops** (w0.84): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **bass swap** (w0.8): ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*
- **call response melody** (w0.76): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **filter transition** (w0.75): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*

## Sound recipes (this palette, these moves)
- **dembow rim**: gm_drums rim/snare key at low velocity for the offbeat lilt
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dembow_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (3-3-2 lean: pushed 'a' of 2 and 4))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
