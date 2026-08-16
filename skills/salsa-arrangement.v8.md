---
name: salsa-arrangement
version: 8
kind: genre
tags: [salsa, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 160-200; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>mid>low.
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - CLAVE 23 is non-negotiable: the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
  - MONTUNO is non-negotiable: salsa piano montuno: syncopated arpeggiated vamp locking the 2-3 or 3-2 clave; never on the downbeat grid
---
# Salsa arrangement (graph-compiled)

## The pocket — tumbao_cascara
salsa loop DNA (wave14)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons) +2 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **horn stabs** (w0.95): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **clave 23** (w0.95): the clave (2-3 / 3-2) is the LAW of afro-cuban time — every part either marks it or leaves space for it *(curated:claude/2026-07-03-w5)*
- **spectral presence** (w0.95): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **montuno** (w0.9): salsa piano montuno: syncopated arpeggiated vamp locking the 2-3 or 3-2 clave; never on the downbeat grid *(curated:claude/2026-07-03-w5)*
- **hemiola 3 2** (w0.7): 3:2 cross-rhythm — two bars of 3 heard as three bars of 2 (or within-bar 3-against-2); the lift beneath afro-latin grooves [Rhythm & meter: hemiola] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **walking bass** (w0.6): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
