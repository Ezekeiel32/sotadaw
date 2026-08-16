---
name: doo_wop-arrangement
version: 2
kind: genre
tags: [doo_wop, rnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 55-160; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order mid>lowmid>low.
  - SUNG BASS ENGINE is non-negotiable: the BASS IS A VOICE: 'bom-bom-bom / dip-da-dip' nonsense syllables on the dotted-quarter pulse with walking pickups — it replaces bass AND drums
  - FIFTIES CHANGES is non-negotiable: the 50s progression I-vi-IV-V (or I-vi-ii-V) cycling one chord per bar — the eternal loop of doo-wop
  - TRIPLET PIANO 1258 is non-negotiable: piano hammers block chords on EVERY triplet 8th (12 hits a bar in 12/8) — the ballad engine
---
# Doo_Wop arrangement (graph-compiled)

Doo_Wop is a child of **rnb** — its groove laws apply unless overridden below.

## The pocket — fifties_ballad
Doo-wop ballad (~72 BPM, 12/8 feel — swing ~0.66 on a 16-grid approximation): piano hammers the triplet 8ths; the SUNG BASS ('bom-bom-bom') walks the dotted-quarter pulse with pickups; brushed kick 1&3, snaps/snare 2&4; the I-vi-IV-V changes cycle one chord a bar; falsetto lead floats over the block-harmony stack. Swing 0.66 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **sung bass engine** (w1.0): the BASS IS A VOICE: 'bom-bom-bom / dip-da-dip' nonsense syllables on the dotted-quarter pulse with walking pickups — it replaces bass AND drums *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **fifties changes** (w0.92): the 50s progression I-vi-IV-V (or I-vi-ii-V) cycling one chord per bar — the eternal loop of doo-wop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **triplet piano 1258** (w0.84): piano hammers block chords on EVERY triplet 8th (12 hits a bar in 12/8) — the ballad engine *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **falsetto over stack** (w0.76): a falsetto lead floating over a 4-5 part block-harmony stack (triads/6ths), gospel melisma on phrase ends *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **brush snap backbeat** (w0.68): brushed snare or finger snaps on 2 & 4, kick soft on 1 & 3 — drums barely there, the voices carry *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from rnb
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- behind beat snare: snare 0.02-0.05 beats late = laid-back head-nod
- m7 chords: minor 7th / extended chords, mid register, soft velocity
- sliding 808: 808 pitch slides between roots (overlapping notes)
- finger snap beat: modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars
- mode mixture: borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture]
- doo wop schema: I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas]
- singer songwriter schema: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
- ...and from the rnb skill itself: tonal ambiguity dual tonic, functional substitution ii IV, vocal space static cut, parsimonious retune, verse position law

## Sound recipes (this palette, these moves)
- **streetcorner**: the stack = formant_vox/vox_pad block harmony; sung bass = a LOW formant_vox/bass_warm voice on the dotted pulse; jazz_piano triplets; brush_snare + soft kick; intimate room reverb, vintage warm, very dynamic — the voices ARE the record

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='shuffle_blues', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (66% shuffle — deeper than jazz_swing's 64%, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
