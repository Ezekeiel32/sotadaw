---
name: ska-arrangement
version: 6
kind: genre
tags: [ska, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-145; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - SKANK UPSTROKE is non-negotiable: ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
  - HORN STABS is non-negotiable: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
---
# Ska arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **skank upstroke** (w0.95): ska/rocksteady/reggae guitar: clean upstroke chords on EVERY offbeat 8th (the skank) — staccato, bright, no sustain; the drum kit leaves beat 1 alone so the skank IS the pulse *(curated:claude/2026-07-03-w7)*
- **spectral presence** (w0.95): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **walking bass** (w0.9): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **horn stabs** (w0.9): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **four floor disco** (w0.5): disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
