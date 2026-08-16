---
name: synthpop-arrangement
version: 9
kind: genre
tags: [synthpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-130; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order lowmid>low>mid.
  - SYNTHPOP HOOK is non-negotiable: synthpop: a MONOPHONIC analog lead hook carries the song (the hook IS the chorus), big gated snare, arpeggiated 8th bass; melody over texture, always
  - VST FACTORY PRESETS is non-negotiable: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
  - GATED REVERB SNARE is non-negotiable: the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat
  - ARP 8TH is non-negotiable: relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted
---
# Synthpop arrangement (graph-compiled)

## The pocket — synthpop_four
synthpop loop DNA (wave19)  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +2 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **synthpop hook** (w0.95): synthpop: a MONOPHONIC analog lead hook carries the song (the hook IS the chorus), big gated snare, arpeggiated 8th bass; melody over texture, always *(curated:claude/2026-07-03-w11)*
- **vst factory presets** (w0.95): factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility *(verified:one-call-apply/2026-07-04 (phrasing lesson FALSIFIED: 0.857->0.857 w/ 0 usage; refined to tool-side friction fix — TAL 87-param + Surge blob applied+rendered via single calls))*
- **gated reverb snare** (w0.9): the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **arp 8th** (w0.9): relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted *(curated:claude/2026-07-02)*
- **singer songwriter schema** (w0.85): vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **doo wop schema** (w0.75): I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **sidechain unmask bass** (w0.75): sustained bass masks a percussive kick because the ear locks onto the constant voice — duck the bass only when the kick hits and both survive; the FX-side complement to rolling_offbeat_bass (where the ARRANGEMENT is the sidechain: bass written in the kick's holes needs no ducking) [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **topline first** (w0.7): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **tonal ambiguity dual tonic** (w0.7): the singer/songwriter schema carries NO authentic cadence (only plagal IV-I or stepwise VII-i), so one loop reads as major AND relative minor at once (the 'Despacito' law: Bm-G-D-A = vi-IV-I-V in D or i-VI-III-VII in Bm) — write one progression, recolor it dark/bright per section via bass root emphasis + melody tones, zero modulation cost [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **verse position law** (w0.7): pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **schema rotation** (w0.65): cyclical schemas keep their identity started ANYWHERE in the cycle (rotation) — one schema = four progressions; choose the rotation whose first chord is the section's mood anchor (IV-start = lift, vi-start = ache) [Popular music: four-chord schemas (variation laws)] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **sentence phrase** (w0.6): the 2+2+4 sentence: presentation (idea x2) then continuation/drive to cadence — THE build shape; EDM risers are sentences in disguise [Form: phrase models] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- also in this genre's DNA (lower weight): period phrase, cadence plagal IV i, axis progression, hopscotch schema, vocal space static cut, symbolic unmask, auxiliary sections law

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
