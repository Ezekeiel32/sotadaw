---
name: tech_house-arrangement
version: 3
kind: genre
tags: [tech_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 124-128; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order low>lowmid>mid.
  - ROLLING OFFBEAT BASS is non-negotiable: bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
---
# Tech_House arrangement (graph-compiled)

## The pocket — techhouse_roll
4-floor + rolling offbeat, shuffled 16ths Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rolling offbeat bass** (w0.95): bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **vocal chops** (w0.75): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **pump sidechain** (w0.7): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **filter transition** (w0.6): fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter *(skill:dj-blend@v1 (2026-07-03, engine-verified warp primitive))*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
