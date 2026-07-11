---
name: post_rock-arrangement
version: 1
kind: genre
tags: [post_rock, rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-140; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -15..-11, band order low>lowmid>mid.
  - POSTROCK CRESCENDO is non-negotiable: a multi-minute build from one sparse clean tremolo/arpeggio to an overwhelming distorted climax — AUTOMATE it (late-bloom curve, layers entering), never jump-cut it
  - DELAY REPEAT GROOVE is non-negotiable: the 'groove' is a delay-drenched clean-guitar arpeggio whose synced echoes weave a shimmering ostinato — the repeats form the rhythmic bed
  - POSTROCK QUIET LOUD is non-negotiable: the Mogwai/EITS grammar: a restrained clean valley ERUPTS into a full distorted wall, then recedes — the dynamic swing is the hook
---
# Post_Rock arrangement (graph-compiled)

Post_Rock is a child of **rock** — its groove laws apply unless overridden below.

## The pocket — crescendo_arp
Post-rock (~110 BPM, 4/4 + odd meters): a delay-drenched clean-guitar arpeggio whose synced echoes weave the ostinato; drums sparse-to-huge; the piece BUILDS vertically over minutes — start with one clean tremolo + brushed ride, each cycle adds a layer (2nd guitar -> EBow swell -> distortion engages -> bass sub -> crash wall) so the same motif detonates as a distorted climax that resolves onto a bright major-lift chord. AUTOMATE the crescendo (late-bloom curve).  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **postrock crescendo** (w1.0): a multi-minute build from one sparse clean tremolo/arpeggio to an overwhelming distorted climax — AUTOMATE it (late-bloom curve, layers entering), never jump-cut it *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **delay repeat groove** (w0.92): the 'groove' is a delay-drenched clean-guitar arpeggio whose synced echoes weave a shimmering ostinato — the repeats form the rhythmic bed *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **postrock quiet loud** (w0.84): the Mogwai/EITS grammar: a restrained clean valley ERUPTS into a full distorted wall, then recedes — the dynamic swing is the hook *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **ebow swell** (w0.76): sustained EBow / volume-swell guitar lines with no pick attack, blooming in like strings over the arpeggios *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **major lift climax** (w0.68): the climax resolves an Aeolian-minor build onto a bright IV or bVI/major-lift chord for the cathartic, hopeful peak *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **layered guitar wash** (w0.6): multiple reverbed/delayed clean guitars stacked at octaves feeding a shared reverb bus into a wide, weightless wash *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from rock
- layered snare: sample clap + synth snare body at -12 to -18
- huge space: bus reverb at maximum size, generous sends — the room is the instrument
- gain staged saturation: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
- power chords: rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density
- quick change blues: 12-bar variation: bar 2 jumps to IV, bar 3 returns to I — restlessness installed at the very top of the form; the single most common blues alteration [Popular music: blues harmony]
- blues turnaround: bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony]
- sixteen bar blues: four 4-bar phrases — tonic stated twice, then subdominant, then dominant phrase ('Hoochie Coochie Man'); notably frequent in blues-based rock [Popular music: blues harmony]
- blues dominant color: the blues color laws in one node: ALL chords dominant sevenths and any of them can be tonic/subdominant/dominant in function; major and minor thirds coexist (the sharp-9 sound); structural closure is PLAGAL (IV-I), not authentic — tonal-harmony truisms do not apply here [Popular music: blues harmony]
- mud zone 200 400: most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16]
- parallel detail pump: high ratio + fast attack AND release, blended low under dry: the original transients stay in charge while low-level detail and tone pump upward — dynamic-range control that never squashes the hit [PARA]
- strophic form: AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes
- refrain hook: a recurring lyric+melodic motive INSIDE the strophe — usually carrying the TITLE — is the refrain: the hook mechanism of strophic songs before choruses existed ('Faded Love'); write it once, let every strophe land it

## Sound recipes (this palette, these moves)
- **postrock wash**: layered clean_chime_guitar arpeggios (dotted/triplet fx_delay -> shimmer fx_reverb bus) for the wash; guitar_grit engages ONLY at the climax; EBow swells = pad_motion/vox_pad; drone bass. THE CRESCENDO IS AUTOMATION — fx_trim gain + fx_saturate drive + reverb-send + layer mute-ins over 60-120 s with a LATE-BLOOM curve (>0). Do NOT brickwall (preserve the arc).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-11, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
