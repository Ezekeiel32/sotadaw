---
name: bossanova-arrangement
version: 6
kind: genre
tags: [bossanova, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-132; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -20..-13, band order lowmid>mid>low.
  - Harmony: maj7/9 and altered dominants — the Jobim/Gilberto harmony floor.
  - BOSSA CLAVE is non-negotiable: bossa: son-clave-ish rim pattern, walking soft bass 1&3, m9/M7 comping off-beats, brushes feel (low vel)
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Bossanova arrangement (graph-compiled)

## The pocket — bossa_sway
rim clave + brush-soft kit, walking bass 1&3, M7/m9 comping offbeats; NOTHING loud  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **bossa clave** (w1.0): bossa: son-clave-ish rim pattern, walking soft bass 1&3, m9/M7 comping off-beats, brushes feel (low vel) *(curated:claude/2026-07-03)*
- **m7 chords** (w0.93): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.86): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **ii V quality signature** (w0.8): the cell is IDENTIFIED by fifths root motion PLUS quality sequence: mi7-7-ma7 in major, half-dim7-7-mi7 in minor (V stays dominant-quality in BOTH modes) — so distinctive that an unresolved ii-V still reads as the schema; generators must keep the quality string even when reharmonizing *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **applied ii V cell** (w0.7): the WHOLE ii-V(-I) unit drops into foreign keys to tonicize any target (applied subdominant included — jazz extends applied chords beyond V); 'Afternoon in Paris' chains cells through bVII then bVI before coming home; an unresolved ii-V alone still creates the pull — motion without commitment, the reharmonizer's passport *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **ii V alteration tolerance** (w0.6): the schema survives alterations and stays recognizable: I-ma7 swaps for a 6 chord ('Misty'), V goes augmented ('Prelude to a Kiss') or takes a lowered fifth ('A Night in Tunisia') — variation budget for generators: color the V freely, keep roots-by-fifth and the seventh intact *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **functional substitution ii IV** (w0.55): ii and IV share subdominant function and swap freely inside any schema (I-vi-ii-V == I-vi-IV-V, 'Hungry Heart') — voice-leading freshness with zero schema-identity cost; ii brings the stepwise bass, IV the open fifth [Popular music: four-chord schemas (variation laws)] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **ii V space navigation** (w0.55): all possible ii-V cells arrange on the circle of fifths into one lattice (McClimon 2017 via OMT2): each key's I is preceded by its ii-V, and cells chain by fifth-steps or slide chromatically — the routing table for jazz motion; pick a distant target, walk cells to it, every hop sounds inevitable *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **motor vibes**: faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -20..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
