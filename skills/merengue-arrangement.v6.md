---
name: merengue-arrangement
version: 6
kind: genre
tags: [merengue, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: F major).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order lowmid>mid>low.
  - MERENGUE DRIVE is non-negotiable: merengue: tambora roll-slap pattern + guira SIXTEENTH sprint at 130-160 2/4 feel, saxophone jaleo riffs in unison octaves — relentless forward drive, no half-time ever
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
---
# Merengue arrangement (graph-compiled)

## The pocket — tambora_gallop
merengue loop DNA (wave18)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **merengue drive** (w0.95): merengue: tambora roll-slap pattern + guira SIXTEENTH sprint at 130-160 2/4 feel, saxophone jaleo riffs in unison octaves — relentless forward drive, no half-time ever *(curated:claude/2026-07-03-w9)*
- **horn stabs** (w0.8): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **spectral presence** (w0.8): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='latin_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
