---
name: blues-arrangement
version: 7
kind: genre
tags: [blues, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-120; set the song key (suggested: E major).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - TWELVE BAR BLUES is non-negotiable: the 12-bar blues as head and blowing form — central to hard bop
  - BLUES BENDS is non-negotiable: melody lives on the blue notes: b3, b5, b7 approached by bend/slide (pitch scoop 30-80ms) — never land ON the major 3rd while the band plays dominant chords
  - SHUFFLE SWING is non-negotiable: hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt
---
# Blues arrangement (graph-compiled)

## The pocket — blues_shuffle
blues loop DNA (wave16) Swing 0.66 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **twelve bar blues** (w0.9): the 12-bar blues as head and blowing form — central to hard bop *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*
- **blues bends** (w0.9): melody lives on the blue notes: b3, b5, b7 approached by bend/slide (pitch scoop 30-80ms) — never land ON the major 3rd while the band plays dominant chords *(curated:claude/2026-07-03-w7)*
- **shuffle swing** (w0.8): hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt *(curated:claude/2026-07-02)*
- **call and response** (w0.8): antiphony: a phrase states, a second voice answers in the gap — the gap IS the invitation (our choir ad-lib lane implements this) [Popular music: texture & form] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **blues dominant color** (w0.75): the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **blues turnaround** (w0.7): bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **minor blues** (w0.7): i7/iv7 become minor sevenths, V STAYS dominant; the third phrase swaps V-IV-i for ii-V-i because major-V falling to minor-iv sounds anticlimactic — the sanctioned jazz handshake inside blues form [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **strophic form** (w0.65): AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- **ghost notes** (w0.6): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **quick change blues** (w0.6): 12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness installed at the very top of the form; the single most common blues alteration [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **refrain hook** (w0.6): a recurring lyric+melodic motive INSIDE the strophe — usually carrying the TITLE — is the refrain: the hook mechanism of strophic songs before choruses existed ('Faded Love'); write it once, let every strophe land it *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- **sixteen bar blues** (w0.45): four 4-bar phrases — tonic stated twice, then subdominant, then dominant phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='jazz_swing', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
