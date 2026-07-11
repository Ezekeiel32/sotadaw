---
name: solo-orchestral
version: 1
kind: sound-design
tags: [faust, orchestral, strings, winds, brass, physical-modeling, legato, articulation, expression, cookbook]
hard_constraints:
  - Voices wrap pm.lib waveguides; expose zones freq/gain/gate PLUS expression zones. End `<: _,_`. Build via write_instrument (instant JIT).
  - The nonlinear friction/reed/lip loop is HARD to keep stable -- schedule bow force / breath pressure with pitch so the tone does not break up (Schelleng wedge for strings).
  - These pm.* surrogates are PLAYABLE + inspectable, not photoreal; a sampled layer is the optional top-realism tier. The EXPRESSION recipe is the durable reusable win.
  - pm.lib bow/reed/lip tables here are verified verbatim against physmodels.lib (docs/research_sound_foundry_ii.md).
---
# Solo orchestral & folk (Slice C) -- strings · winds/brass · sympathetic-string folk

Exposed solo lines as pm.lib waveguides + a reusable EXPRESSION/ARTICULATION layer any melodic voice
borrows. Assume `import("stdfaust.lib");`. Full DNA + sources: docs/research_sound_foundry_ii.md.

## Solo strings (violin/viola/cello/bass -- pm.violinModel)
```
// wrap pm.violinModel(stringLength, bowPressure, bowVelocity, bowPosition)
// zones: freq gain gate + bowForce bowSpeed bowPos vibDepth vibRate vibDelay porta
```
- Map note freq -> stringLength INVERSELY from a reference (L proportional to refFreq/freq; the model changes pitch by LENGTH, not fingering). Drive the length line through `si.smooth`.
- **TRUE LEGATO** = keep the bow ENGAGED (gate stays HIGH) and GLIDE the delay length -- the `porta` time-constant is both your portamento/glissando AND your slur. A long constant while gate is high = legato; short = separate bows.
- DELAYED CC VIBRATO = an LFO on freq whose depth ramps in after `vibDelay` (body-coupled AM comes free from the model). Dynamic bow swell = CC-driven bowVelocity crescendo.
- Bow position `~0.08-0.13`; sul tasto (toward fingerboard, hollow) vs sul ponticello (toward bridge, glassy/tense) = sweep bowPos. Articulations: detache, legato, spiccato, martele, staccato, tremolo, col legno, harmonics, pizzicato.
- Verified verbatim: bowTable=`pow(abs(sample)+0.75,-4):min(1)`, violinBowTable slope=`5-4*bowPressure`, bridgeFilter(320, t60=(1-absorption)*20, ...), body=`fi.resonbp(500,2,1)`, stringTuning=0.08.
- Unlocks: film-score solo violin/cello, tango nuevo (pairs with the shipped bandoneon), gypsy-jazz swing fiddle, Celtic fiddle, Indian/Arabic microtonal bowed lines, horror (sul-pont trem / col legno -- Herrmann/Penderecki).

## Solo winds & brass (pm.clarinetModel / pm.brassLipsTable + pm.blower + brass-mute rack)
- CLARINET: `pm.clarinetModel(pm.f2l(freq), pressure, reedStiffness, bellOpening)`, reedStiffness~0.5; drive `pressure` from `pm.blower(dyn, 0.05, 2000, vibFreq, vibDepth)` where dyn = env * CC-scaled breath.
- Double-reed OBOE/BASSOON = clarinetModel with reedStiffness 0.8-0.95 + a parallel formant `fi.resonbp` (oboe fc~1.1-1.4kHz nasal buzz; bassoon add ~450Hz). Force OCTAVE (not 12th) register logic.
- BRASS = `pm.brassLipsTable` lip nonlinearity -> square -> clip (freq = l2f(L)*4^(2*lipsTension-1)); breath from pm.blower. Legato slurs vs tongued attacks; flutter-tongue = fast AM; growl.
- **BRASS-MUTE RACK (reusable, mutes ANY brass incl. sampled):** straight / cup / harmon / plunger (wah) / stopped = a biquad formant/notch profile per mute. Harmon = the cool-jazz Miles trumpet; plunger = manual wah automation.
- Breath dynamics via CC1 (dynamics) / CC11 (expression) / CC2 (breath); MPE-friendly. Unlocks cinematic winds, big-band/jazz muted brass, klezmer clarinet.

## Bowed & folk (bowed_symp.dsp -- sympathetic-string / drone / buzzing-bridge)
ONE reusable engine; each instrument = same engine + a sympathetic-tuning table + body formants:
- STRING + BOW = pm.violinModel core (or `pm.terminations(pm.violinNuts, pm.chain(stringSegment : pm.violinBow : stringSegment), pm.violinBridge)`). Bowed voices = gate-driven bowVelocity; DRONE voices (hurdy-gurdy) = velocity HELD constant + a wow/flutter LFO from the tape-wow block.
- SYMPATHETIC STRINGS = `par()` of UNDAMPED resonators tuned to a resonance table, excited by the melody string's output (nyckelharpa, hardanger, sitar, sarangi).
- BUZZING BRIDGE (jawari / hurdy-gurdy "dog/trompette") = an amplitude-modulated moving-boundary delay length = spectral-enrichment buzz.
- Instruments: morin khuur (flat bridge, horsehair bundles, rich overtones), nyckelharpa (keyed + sympathetic), hardanger (4 melody + 4-5 understrings + drone), hurdy-gurdy (continuous wheel-bow + drones + buzz), viola da gamba, kokle/kantele.
- **RELIABILITY: MEDIUM (2 refuted bow-table specifics) -- verify the bow-table math against the LIVE physmodels.lib before coding.** Confirmed-safe: bowTable(offset,slope)=`pow(abs((_+offset)*slope)+0.75,-4):min(1)`, violinBowTable slope=`5-4*bowPressure`, defaults pressure 0.5/velocity 0/position 0.7; violinModel is SINGLE-string -> use `par()` for polyphony.
- Unlocks Nordic/steppe/medieval/neofolk/dungeon-synth + reuses for sitar/tanpura/sarangi.

## The reusable EXPRESSION SoundRecipe (any melodic voice borrows)
delayed-vibrato template · CC-bow/breath-swell automation curve · portamento-glide · true-legato flag ·
articulation macro dictionary (which articulation per phrase). This is the part that generalizes.

Companions: faust-reusable-blocks (Karplus-Strong/waveguide + tape-wow), sound-palette (which voice
when), automation-motion (CC swell / vibrato-onset / portamento curves), faust-writing (voice skeleton).
