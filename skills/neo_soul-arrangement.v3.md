---
name: neo_soul-arrangement
version: 3
kind: genre
tags: [neo_soul, soul, rnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-100; set the song key (suggested: D minor (Dorian)).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
  - Harmony: 7ths/9ths with added 2nds/4ths and cluster voicings (the Scott/Glasper keyboard grammar).
  - DILLA DRUNK SWING is non-negotiable: the J Dilla 'drunk' pocket: the snare dragged ~20-50 ms LATE and hats pushed/pulled OFF the grid so the beat lurches — deliberately un-quantized, the wobble is the feel
  - EXTENDED JAZZ CHORDS is non-negotiable: m9, m11, maj9, 13 and dominant-alt voicings (rootless, close) replacing plain triads — Dorian/lush harmony borrowed from jazz
  - BEHIND BEAT BASS is non-negotiable: the bass sits slightly BEHIND the kick (fingered/foam-muted P-bass, rounded), locking to the late snare for the laid-back drag
---
# Neo_Soul arrangement (graph-compiled)

Neo_Soul is a child of **soul, rnb** — its groove laws apply unless overridden below.

## The pocket — dilla_pocket
Neo-soul (~85 BPM, half-time, Dilla 'drunk' pocket): backbeat on 3 but the snare is dragged ~20-50 ms LATE and the hats push/pull OFF the grid so the beat lurches; a foam-muted bass sits BEHIND the kick; Fender Rhodes comps lush m9/m11/maj9 (Dorian) chords with chorus. Never quantize — the wobble IS the feel. Swing 0.56 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dilla drunk swing** (w1.0): the J Dilla 'drunk' pocket: the snare dragged ~20-50 ms LATE and hats pushed/pulled OFF the grid so the beat lurches — deliberately un-quantized, the wobble is the feel *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **extended jazz chords** (w0.92): m9, m11, maj9, 13 and dominant-alt voicings (rootless, close) replacing plain triads — Dorian/lush harmony borrowed from jazz *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **behind beat bass** (w0.84): the bass sits slightly BEHIND the kick (fingered/foam-muted P-bass, rounded), locking to the late snare for the laid-back drag *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **rhodes comp neo** (w0.76): warm Fender Rhodes (or Wurlitzer) comps the extended chords with light chorus/phaser — the harmonic bed of neo-soul *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **unquantized live kit** (w0.68): a loose live/MPC-chopped kit with real velocity spread and timing slop — hats ghosted, snare fat and dark; never grid-locked *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **chromatic mediant move** (w0.6): surprise chord shifts by third (e.g. a bIII or VI borrowed) for the bittersweet neo-soul lift — reharm over a simple loop *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from soul, rnb
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- behind beat snare: snare 0.02-0.05 beats late = laid-back head-nod
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- walking bass: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
- horn stabs: tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk)
- spectral presence: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
- plagal shuttle: I<->IV oscillation (the 'amen' motion) — harmonic warmth without dominant tension; loops forever without demanding a cadence [Popular music: harmonic schemas]
- mode mixture: borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture]
- ...and from the soul skill itself: cadence modal VII i, doo wop schema, minor blues, mud zone 200 400, parallel detail pump, refrain hook, bridge contrast law, expressive performance, tambourine backbeat, melodic bass lines, horn stabs backbeat, organ bed, send reverb, behind beat snare, m7 chords, sliding 808, finger snap beat, mode mixture, doo wop schema, singer songwriter schema, tonal ambiguity dual tonic, functional substitution ii IV, vocal space static cut, parsimonious retune, verse position law

## Sound recipes (this palette, these moves)
- **neo soul bed**: Fender Rhodes (light chorus/phaser) comping extended chords + jazz_piano fills; foam-muted P-bass = bass_warm sitting late; loose live/MPC kit with velocity spread (dark fat snare, ghosted hats); keep it warm, round, bass-forward and un-brickwalled (DR-preserving master).

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
