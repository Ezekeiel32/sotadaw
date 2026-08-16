---
name: progressive_house-arrangement
version: 4
kind: genre
tags: [progressive_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 122-128; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -9..-7, band order low>lowmid>mid.
  - PROG LAYER BUILD is non-negotiable: progressive house: additive 16-32 bar builds (one element per 8), rolling offbeat bass, ONE breakdown to near-silence mid-track, then the full arrangement drop
  - ROLLING OFFBEAT BASS is non-negotiable: bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing
  - JOURNEY STRUCTURE is non-negotiable: 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown
---
# Progressive_House arrangement (graph-compiled)

## The pocket — prog_roll
progressive_house loop DNA (wave15)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **prog layer build** (w0.95): progressive house: additive 16-32 bar builds (one element per 8), rolling offbeat bass, ONE breakdown to near-silence mid-track, then the full arrangement drop *(curated:claude/2026-07-03-w10)*
- **rolling offbeat bass** (w0.8): bass SILENT on the kick, galloping the three 16ths after (null,x,x,x) — kick and bass never collide, so the mix pumps with ZERO sidechain: the arrangement IS the sidechain | lore-verified: 16th-pulse rolling bass, fundamentals 40-80Hz; the pump comes from the kick-hole OR sidechain - both canon, the hole needs zero processing *(chezy-prototype forensics 2026-07-05 (song_editor goa act, 346 bars))*
- **journey structure** (w0.8): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **evolving pads** (w0.7): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **riser throws** (w0.7): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **odin modular lead**: Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette
- **pluck zones**: pluck knobs: decay 0.05-2s (squared env - snappy), color 1-12 (pitch-tracking LP multiple: 2 = dark koto, 10 = open). Dance plucks = color 6-8 decay 0.3; automate color rising into a drop.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
