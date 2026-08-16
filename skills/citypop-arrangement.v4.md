---
name: citypop-arrangement
version: 4
kind: genre
tags: [citypop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-115; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - RHODES CHORDS is non-negotiable: (see technique node)
  - SLAP BASS 16BEAT is non-negotiable: (see technique node)
  - FUNK GUITAR CHANK is non-negotiable: (see technique node)
  - MAJ7 GLOSS is non-negotiable: citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ
---
# Citypop arrangement (graph-compiled)

## The pocket — citypop_gloss
citypop loop DNA (wave16)  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **rhodes chords** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **slap bass 16beat** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **funk guitar chank** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **synth brass stabs** (wNone):  *(r-23 instrumentation whitelists w78 (2026-07-16))*
- **maj7 gloss** (w0.95): citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ *(curated:claude/2026-07-03)*
- **ii V quality signature** (w0.8): the cell is IDENTIFIED by fifths root motion PLUS quality sequence: mi7-7-ma7 in major, half-dim7-7-mi7 in minor (V stays dominant-quality in BOTH modes) — so distinctive that an unresolved ii-V still reads as the schema; generators must keep the quality string even when reharmonizing *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **parsimonious retune** (w0.8): reharmonization moves each voice AS LITTLE AS POSSIBLE: chord tones map role-to-role (root->root, third->third quality-aware) taking the nearest octave; tensions keep contour via root delta — this is parsimonious voice leading (neo-Riemannian theory; OMT2 has the chapter) applied as an edit operation [battery: mean 3.0 semitones, re-vote reads the exact target] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **doo wop schema** (w0.75): I-vi-IV-V cyclical schema (C-Am-F-G): the 50s/60s ballad engine, never left; variations: I-vi-ii-V (ii subs IV, same function) and rotation IV-V-I-vi ('Viva la Vida' enters the cycle on IV) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **mono check law** (w0.75): AUDITION IN MONO with and without your width moves: side-channel content disappears completely in the fold, and aggressive M/S EQ (the classic +8dB-lows-on-sides) can make a track barely audible summed — if the mix collapses, the width was borrowed, not earned [the fold test] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **mode mixture** (w0.7): borrowed iv / bVI / bVII inside major — instant bittersweet color; the borrowed iv on the pre-cadence is the classic tearjerker [Chromaticism: mode mixture] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **aaba form** (w0.7): 32-bar AABA: statement, restatement, bridge ('the middle eight'), return — the standard's skeleton [Form: popular song forms] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **bridge contrast law** (w0.7): AABA's B section exists to DEPART (new harmony, new melodic register), which is what makes the final A's return feel amplified — write the bridge as contrast, never as variation; 32-bar proportions = 8 bars per section in the Golden-Age prototype *(OMT2 'AABA Form and Strophic Form' (Open Music Theory v2, CC BY-SA) via curated:claude/2026-07-05 (wave32 form families))*
- also in this genre's DNA (lower weight): mid side width control, schema rotation, width by arrangement, dotted8 delay, offbeat bass, period phrase, vocal space static cut, ii V alteration tolerance, symbolic unmask, functional substitution ii IV, tape saturation, gated reverb snare, trust innate brightness

## Sound recipes (this palette, these moves)
- **solina strings**: faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='disco_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (subtle ~53% swing, offbeat-8th hat barks, strong quarter pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
