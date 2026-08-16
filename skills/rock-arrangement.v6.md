---
name: rock-arrangement
version: 6
kind: genre
tags: [rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-150; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order lowmid>low>mid.
  - POWER CHORDS is non-negotiable: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
  - MUD ZONE 200 400 is non-negotiable: most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16]
  - BLUES DOMINANT COLOR is non-negotiable: the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony]
---
# Rock arrangement (graph-compiled)

## The pocket — rock_backbeat
rock loop DNA (wave16)  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **power chords** (w0.95): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*
- **mud zone 200 400** (w0.8): most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **blues dominant color** (w0.75): the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **layered snare** (w0.7): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*
- **gain staged saturation** (w0.7): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **blues turnaround** (w0.7): bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **strophic form** (w0.65): AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- **quick change blues** (w0.6): 12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness installed at the very top of the form; the single most common blues alteration [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **parallel detail pump** (w0.6): high ratio + fast attack AND release, blended low under dry: the original transients stay in charge while low-level detail and tone pump upward — dynamic-range control that never squashes the hit [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **refrain hook** (w0.6): a recurring lyric+melodic motive INSIDE the strophe — usually carrying the TITLE — is the refrain: the hook mechanism of strophic songs before choruses existed ('Faded Love'); write it once, let every strophe land it *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- **huge space** (w0.5): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **sixteen bar blues** (w0.45): four 4-bar phrases — tonic stated twice, then subdominant, then dominant phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
