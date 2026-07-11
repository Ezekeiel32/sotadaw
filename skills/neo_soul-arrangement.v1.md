---
name: neo_soul-arrangement
version: 1
kind: genre
tags: [neo_soul, soul, rnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-100; set the song key (suggested: D minor (Dorian)).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order low>lowmid>mid.
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
- cadence modal VII i: the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)
- doo wop schema: I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas]
- minor blues: i7/iv7 become minor sevenths, V STAYS dominant; the third phrase swaps V-IV-i for ii-V-i because major-V falling to minor-iv sounds anticlimactic — the sanctioned jazz handshake inside blues form [Popular music: blues harmony]
- mud zone 200 400: most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16]
- parallel detail pump: high ratio + fast attack AND release, blended low under dry: the original transients stay in charge while low-level detail and tone pump upward — dynamic-range control that never squashes the hit [PARA]
- refrain hook: a recurring lyric+melodic motive INSIDE the strophe — usually carrying the TITLE — is the refrain: the hook mechanism of strophic songs before choruses existed ('Faded Love'); write it once, let every strophe land it
- bridge contrast law: AABA's B section exists to DEPART (new harmony, new melodic register), which is what makes the final A's return feel amplified — write the bridge as contrast, never as variation; 32-bar proportions = 8 bars per section in the Golden-Age prototype
- expressive performance: humanize by GrooVAE two axes — MICROTIMING (correlated drift) + VELOCITY (metric accent) — verified by TWO metrics: a continuous expressiveness score (sensitive to subtle feel, rises 0->42 with amount) AND a faithful NOMML median-metric-level classifier (coarse: dead-grid=mechanical, real off-grid performance=expressive). NOT a black-box button: the metrics prove it
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- behind beat snare: snare 0.02-0.05 beats late = laid-back head-nod
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- sliding 808: 808 pitch slides between roots (overlapping notes)
- finger snap beat: modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars
- mode mixture: borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture]
- doo wop schema: I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas]
- singer songwriter schema: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
- tonal ambiguity dual tonic: the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas]
- functional substitution ii IV: ii and IV share subdominant function and swap freely inside any schema (I-vi-ii-V == I-vi-IV-V, 'Hungry Heart') — voice-leading freshness with zero schema-identity cost; ii brings the stepwise bass, IV the open fifth [Popular music: four-chord schemas (variation laws)]
- vocal space static cut: make room for a vocal with a STATIC 1-2 dB cut on the instrumental at the conflict band — start tiny, in context; the instrumental barely changes solo'd but the vocal seats [VOX]
- parsimonious retune: reharmonization moves each voice AS LITTLE AS POSSIBLE: chord tones map role-to-role (root->root, third->third quality-aware) taking the nearest octave; tensions keep contour via root delta — this is parsimonious voice leading (neo-Riemannian theory; OMT2 has the chapter) applied as an edit operation [battery: mean 3.0 semitones, re-vote reads the exact target]
- verse position law: pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally]

## Sound recipes (this palette, these moves)
- **neo soul bed**: Fender Rhodes (light chorus/phaser) comping extended chords + jazz_piano fills; foam-muted P-bass = bass_warm sitting late; loose live/MPC kit with velocity spread (dark fat snare, ghosted hats); keep it warm, round, bass-forward and un-brickwalled (DR-preserving master).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
