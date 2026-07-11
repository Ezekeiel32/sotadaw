---
name: rnb-arrangement
version: 4
kind: genre
tags: [rnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-95; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - Harmony: min7/maj7 and 9th voicings are the default color, not the exception.
  - FINGER SNAP BEAT is non-negotiable: modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - SINGER SONGWRITER SCHEMA is non-negotiable: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
---
# Rnb arrangement (graph-compiled)

## The pocket — rnb_snap
halftime snap: space is the pocket Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: OMT2 'Four-Chord Schemas' degrees -> archetype chord DNA via curated:claude/2026-07-05 (wave29b))*

## Techniques (weight order — the top ones DEFINE the genre)
- **finger snap beat** (w0.9): modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars *(curated:claude/2026-07-03-w6)*
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **singer songwriter schema** (w0.85): vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **parsimonious retune** (w0.8): reharmonization moves each voice AS LITTLE AS POSSIBLE: chord tones map role-to-role (root->root, third->third quality-aware) taking the nearest octave; tensions keep contour via root delta — this is parsimonious voice leading (neo-Riemannian theory; OMT2 has the chapter) applied as an edit operation [battery: mean 3.0 semitones, re-vote reads the exact target] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **doo wop schema** (w0.75): I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **mode mixture** (w0.7): borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **tonal ambiguity dual tonic** (w0.7): the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **verse position law** (w0.7): pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **vocal space static cut** (w0.6): make room for a vocal with a STATIC 1-2 dB cut on the instrumental at the conflict band — start tiny, in context; the instrumental barely changes solo'd but the vocal seats [VOX] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **functional substitution ii IV** (w0.55): ii and IV share subdominant function and swap freely inside any schema (I-vi-ii-V == I-vi-IV-V, 'Hungry Heart') — voice-leading freshness with zero schema-identity cost; ii brings the stepwise bass, IV the open fifth [Popular music: four-chord schemas (variation laws)] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*

## Sound recipes (this palette, these moves)
- **gliss harp**: faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.
- **rhodes zones**: rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; gospel chords = sustain 0.5 + decay 2.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
