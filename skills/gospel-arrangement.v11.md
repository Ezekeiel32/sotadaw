---
name: gospel-arrangement
version: 11
kind: genre
tags: [gospel, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-110; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - Harmony: 7ths/9ths plus passing diminished chords between diatonic steps.
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - GOSPEL PROGRESSION is non-negotiable: gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords
  - VST FX PRESETS is non-negotiable: the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
---
# Gospel arrangement (graph-compiled)

## The pocket — gospel_shout
gospel loop DNA (wave19) Swing 0.54 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **m7 chords** (w0.95): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **gospel progression** (w0.95): gospel harmony: I-I/3-IV climbs, 2-5-1s with 9th/13th extensions, a WALKUP into every section change; organ swells (volume pedal) under held chords *(curated:claude/2026-07-03-w7)*
- **vst fx presets** (w0.92): the pro fx rack: 291 curated factory fx presets (Surge XT Effects: 40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser) via vst_presets query='Reverb 2'|'Delay'|... -> use_as_fx {id:'vst3:Surge XT Effects', preset:...}; character spaces on BUSES via sends (one per section), utility space stays faust fx_reverb; any scanned vst3 also works bare: {'id':'vst3:Airwindows Consolidated'} = pro reverb *(verified:surgefx-rail/2026-07-03 (Large Church rings -29..-48dB over 3.5s vs -240 dry; blob = fxt+vt_float+f01))*
- **call response melody** (w0.9): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **call and response** (w0.8): antiphony: a phrase states, a second voice answers in the gap — the gap IS the invitation (our choir ad-lib lane implements this) [Popular music: texture & form] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **parsimonious retune** (w0.8): reharmonization moves each voice AS LITTLE AS POSSIBLE: chord tones map role-to-role (root->root, third->third quality-aware) taking the nearest octave; tensions keep contour via root delta — this is parsimonious voice leading (neo-Riemannian theory; OMT2 has the chapter) applied as an edit operation [battery: mean 3.0 semitones, re-vote reads the exact target] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **blues dominant color** (w0.75): the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **secondary dominant** (w0.7): V/x tonicization: any diatonic chord gets its own dominant for one beat of borrowed gravity — gospel/jazz motion fuel [Chromaticism: applied chords] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **plagal shuttle** (w0.65): I<->IV oscillation (the 'amen' motion) — harmonic warmth without dominant tension; loops forever without demanding a cadence [Popular music: harmonic schemas] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **pedal point** (w0.6): static bass under moving harmony — tension by refusal; the dominant pedal is the classic pre-drop device [Diatonic harmony: pedal/prolongation] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **cadence authentic V i** (w0.6): authentic cadence V->i: the classical resolve; rare and DELIBERATE in modal genres — flags tonal writing *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **picardy third** (w0.4): minor movement ends on the parallel MAJOR tonic — the sunrise ending; cheap to play, expensive-sounding [Chromaticism: closing devices] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*

## Sound recipes (this palette, these moves)
- **gospel organ**: faust organ_soul: drawbar stack w/ bright 2'+1' registration, Hammond one-shot percussion, 5.7Hz rotary — pads under verses, stabs with the horns
- **choir ah pad**: faust vox_pad: designed choir-ah (saws through 700/1050 formants, slow bloom) — gospel swells, trance pads, cinematic beds; the sampled choir kit is the REAL thing, this is the designed color to layer with it
- **dragonfly space**: the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
