---
name: soul-arrangement
version: 9
kind: genre
tags: [soul, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-95; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -16..-10, band order lowmid>low>mid.
  - Harmony: min7/maj7 voicings on keys and horn pads.
  - TAMBOURINE BACKBEAT is non-negotiable: (see technique node)
  - MELODIC BASS LINES is non-negotiable: (see technique node)
  - HORN STABS BACKBEAT is non-negotiable: (see technique node)
---
# Soul arrangement (graph-compiled)

## The pocket — soul_pocket
soul loop DNA (wave16) Swing 0.55 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **tambourine backbeat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **melodic bass lines** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **horn stabs backbeat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **organ bed** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **walking bass** (w0.8): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **spectral presence** (w0.8): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **mud zone 200 400** (w0.8): most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **behind beat snare** (w0.75): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **doo wop schema** (w0.75): I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **mode mixture** (w0.7): borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **minor blues** (w0.7): i7/iv7 become minor sevenths, V STAYS dominant; the third phrase swaps V-IV-i for ii-V-i because major-V falling to minor-iv sounds anticlimactic — the sanctioned jazz handshake inside blues form [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- also in this genre's DNA (lower weight): bridge contrast law, plagal shuttle, expressive performance, send reverb, horn stabs, cadence modal VII i, parallel detail pump, refrain hook

## Sound recipes (this palette, these moves)
- **brass section**: faust brass_stab: detuned saw pair + filter env faster than amp (the blat) + 50ms pitch scoop; stabs on the +of-2, swells for choruses
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns
- **solina strings**: faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)
- **motor vibes**: faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.
- **rhodes zones**: rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; gospel chords = sustain 0.5 + decay 2.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='funk_pocket', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (16th funk: leans forward on the a's, audible ghosts, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-10, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
