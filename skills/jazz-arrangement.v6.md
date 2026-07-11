---
name: jazz-arrangement
version: 6
kind: genre
tags: [jazz, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-220; set the song key (suggested: Bb major).
  - Mix: clipped_samples == 0, LUFS -18..-12, band order lowmid>mid>low.
  - SWING RIDE is non-negotiable: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Jazz arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **swing ride** (w0.95): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **spectral presence** (w0.95): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **walking bass** (w0.9): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **jazz comping** (w0.9): piano/guitar comping: rootless 3-7-9 voicings stabbed BETWEEN melody phrases (the holes), never on every beat; anticipate chord changes by an 8th *(curated:claude/2026-07-03-w7)*
- **m7 chords** (w0.8): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **gliss harp**: faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color
- **motor vibes**: faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe
- **rhodes zones**: rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; gospel chords = sustain 0.5 + decay 2.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-12, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
