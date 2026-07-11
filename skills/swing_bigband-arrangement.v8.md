---
name: swing_bigband-arrangement
version: 8
kind: genre
tags: [swing_bigband, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-220; set the song key (suggested: Bb major).
  - Mix: clipped_samples == 0, LUFS -16..-11, band order lowmid>mid>low.
  - SWING RIDE is non-negotiable: jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1
  - BIGBAND SHOUT is non-negotiable: big band: the SHOUT chorus — full horn soli in block harmony over walking bass + swing ride; sections converse (saxes call, brass answer), dynamics terraced not gradual
  - SPECTRAL PRESENCE is non-negotiable: the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf.
  - WALKING BASS is non-negotiable: bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1
---
# Swing_Bigband arrangement (graph-compiled)

## The pocket — bigband_ride
swung ride + feathered kick + cross-stick 2&4 Swing 0.64 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **swing ride** (w0.95): jazz time = the RIDE cymbal (ding ding-ga-ding, swing 0.62-0.68) + feathered kick + cross-stick 2&4; bass walks quarters — drums converse, never loop 1:1 *(curated:claude/2026-07-03-w7)*
- **bigband shout** (w0.95): big band: the SHOUT chorus — full horn soli in block harmony over walking bass + swing ride; sections converse (saxes call, brass answer), dynamics terraced not gradual *(curated:claude/2026-07-03-w10)*
- **spectral presence** (w0.95): the top octaves are the genre's FACE: after limiting, verify mid_500_2k >= ~8%% and himid_2k_6k >= ~1%% of band energy for horn/clav/lead genres — a passing band ORDER with collapsed magnitudes is still a dead mix. Fix at the SOURCE: brighter voicings, less lowpass, lead levels up — never a master shelf. *(lesson:judge/2026-07-03 (eval_funk 7/7 yet centroid 979Hz, himid 0.4% — horns/clav present in arrangement, buried in render; hand-written A beat it margin 4))*
- **walking bass** (w0.9): bass walks chord tones + chromatic approaches, one note per beat — funk/soul/jazz glue; syncopated pickups into the 1 *(curated:claude/2026-07-03-w5)*
- **ii V I turnaround** (w0.85): the ii-V-I engine with shell voicings (3rds+7ths): jazz's gravitational cell; chain them around the cycle for motion [Jazz: harmony fundamentals] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **call response melody** (w0.8): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **ii V quality signature** (w0.8): the cell is IDENTIFIED by fifths root motion PLUS quality sequence: mi7-7-ma7 in major, half-dim7-7-mi7 in minor (V stays dominant-quality in BOTH modes) — so distinctive that an unresolved ii-V still reads as the schema; generators must keep the quality string even when reharmonizing *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **horn stabs** (w0.7): tight unison brass hits on arrangement accents (1 and the +of-2) — call-response with the vocal; short, loud, then GONE (space is the funk) *(curated:claude/2026-07-03-w5)*
- **secondary dominant** (w0.7): V/x tonicization: any diatonic chord gets its own dominant for one beat of borrowed gravity — gospel/jazz motion fuel [Chromaticism: applied chords] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **aaba form** (w0.7): 32-bar AABA: statement, restatement, bridge ('the middle eight'), return — the standard's skeleton [Form: popular song forms] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **blues turnaround** (w0.7): bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **applied ii V cell** (w0.7): the WHOLE ii-V(-I) unit drops into foreign keys to tonicize any target (applied subdominant included — jazz extends applied chords beyond V); 'Afternoon in Paris' chains cells through bVII then bVI before coming home; an unresolved ii-V alone still creates the pull — motion without commitment, the reharmonizer's passport *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **ii V alteration tolerance** (w0.6): the schema survives alterations and stays recognizable: I-ma7 swaps for a 6 chord ('Misty'), V goes augmented ('Prelude to a Kiss') or takes a lowered fifth ('A Night in Tunisia') — variation budget for generators: color the V freely, keep roots-by-fifth and the seventh intact *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **ii V space navigation** (w0.55): all possible ii-V cells arrange on the circle of fifths into one lattice (McClimon 2017 via OMT2): each key's I is preceded by its ii-V, and cells chain by fifth-steps or slide chromatically — the routing table for jazz motion; pick a distant target, walk cells to it, every hop sounds inevitable *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*

## Sound recipes (this palette, these moves)
- **sax soli**: faust sax_section: formant-bodied reed w/ breath onset, jazz scoop, late vibrato — unison lines = the soli, block chords = the shout chorus; keep lines legato (len ~0.9 of gap)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-11, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
