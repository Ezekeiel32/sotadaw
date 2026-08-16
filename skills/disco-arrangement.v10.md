---
name: disco-arrangement
version: 10
kind: genre
tags: [disco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-125; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - Harmony: maj7/min7 string and rhodes beds under straight-16 rhythm.
  - FOUR FLOOR DISCO is non-negotiable: disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
---
# Disco arrangement (graph-compiled)

## The pocket — disco_four
disco loop DNA (wave14)  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **four floor disco** (w0.95): disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria *(curated:claude/2026-07-03-w5)*
- **offbeat bass** (w0.8): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **spectral presence** (w0.8): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **walking bass** (w0.7): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **horn stabs** (w0.65): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **two chord vamp** (w0.6): two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **cadence plagal IV i** (w0.6): plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **tape saturation** (w0.5): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses
- **solina strings**: faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses
- **string ostinato**: faust strings_stacc: spiccato section, bow bite + no sustain — THE ostinato engine: 8th/16th cells (same 1-2 pitches per bar) under cine_brass swells + timpani hits; also disco/funk stabs
- **hat zones**: hat knobs: decay 0.01-0.6 (0.05 closed default; 0.25-0.4 = OPEN HAT — same voice, one knob), tone 4k-16k (bp centre), sizzle 0.5-8 (Q). Automate decay for open/closed patterns on ONE track.
- **clav funk zones**: clav_funk knobs: duty 0.1-0.45 (pulse width - hollowness of the bark), snap 0-1.5, decay 0.1-1s, tone 2000-12000 (resonant LP). Wah-clav = automate tone with the groove; darker funk comp = tone 4000.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='disco_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (subtle ~53% swing, offbeat-8th hat barks, strong quarter pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
