---
name: boogie-arrangement
version: 1
kind: genre
tags: [boogie, disco, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-120; set the song key (suggested: D minor (Dorian)).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order low>lowmid>mid.
  - OCTAVE BOUNCE BASS is non-negotiable: the boogie engine: synth bass bouncing root-octave 16ths (Minimoog/DX), locking the kick pickups — the low end IS the timekeeper
  - NO FOUR FLOOR KICK is non-negotiable: kick on 1 + pickups (and-of-2, and-of-3) — NOT four-on-the-floor; the space between kicks makes the bounce
  - LINN CLAP CRACK is non-negotiable: LinnDrum/DMX-era clap+snare stacked on 2 & 4, bone dry or short-gated — the early-80s crack
---
# Boogie arrangement (graph-compiled)

Boogie is a child of **disco** — its groove laws apply unless overridden below.

## The pocket — roller_bounce
Boogie (~112 BPM, light 16th shuffle ~54%): NO four-on-the-floor — kick on 1 + pickups (and-of-2 = slot 6, and-of-3 = slot 10); LinnDrum clap+snare crack 2&4; the synth bass bounces root-octave 16ths locking the kick; min7/min9 Dorian two-chord vamps; talkbox hook on top; open hats off-8ths. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **octave bounce bass** (w1.0): the boogie engine: synth bass bouncing root-octave 16ths (Minimoog/DX), locking the kick pickups — the low end IS the timekeeper *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **no four floor kick** (w0.92): kick on 1 + pickups (and-of-2, and-of-3) — NOT four-on-the-floor; the space between kicks makes the bounce *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **linn clap crack** (w0.84): LinnDrum/DMX-era clap+snare stacked on 2 & 4, bone dry or short-gated — the early-80s crack *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **talkbox hook** (w0.76): a talkbox/vocoder lead singing the hook (Zapp grammar) — synthesized voice as the star *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **dorian min7 vamp** (w0.68): Dorian min7/min9 two-chord vamps (i7-IV7) — funk harmony smoothed for the roller rink *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from disco
- offbeat bass: bass hits on the 8th between kicks
- tape saturation: heavy fx_saturate drive 8-14 over the whole beat bus = grit
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- horn stabs: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
- four floor disco: disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- two chord vamp: two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient)
- cadence plagal IV i: plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth

## Sound recipes (this palette, these moves)
- **roller rig**: Minimoog octave bass = bass_warm/chip_bass playing R-r' 16ths (write the octave bounce INTO the notes); clav_funk + rhodes stabs; talkbox hook = formant_vox riding the melody; clap_909 dry crack; strings_disco sweetener; punchy but dynamic

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
