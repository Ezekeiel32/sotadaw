---
name: lofi-arrangement
version: 11
kind: genre
tags: [lofi, boombap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-85; set the song key (suggested: D minor).
  - Mix: clipped_samples == 0, LUFS -20..-12, band order low~lowmid>mid.
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - GROOVE DILLA is non-negotiable: apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile.
---
# Lofi arrangement (graph-compiled)

Lofi is a child of **boombap** — its groove laws apply unless overridden below.

## The pocket — lofi_pocket
loose kicks, snare late, everything soft Swing 0.56 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **behind beat snare** (w1.0): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **m7 chords** (w0.92): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **groove dilla** (w0.9): apply_groove('dilla', amount 0.6-0.9) on drums - drunk drag, late backbeat. The lofi/boombap feel IS this profile. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **ii V I turnaround** (w0.85): the ii-V-I engine with shell voicings (3rds+7ths): jazz's gravitational cell; chain them around the cycle for motion [Jazz: harmony fundamentals] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **dusty chain** (w0.84): fx_saturate drive 6-10 + fx_reverb small dark = lofi glue *(skill:lofi-arrangement@v1)*
- **mud zone 200 400** (w0.8): most instruments carry energy at 200-400 Hz, so masking concentrates there (the 'mud'); 400-600 Hz reads boxy/papery — cut in these zones but NOT on every track: pick one or two donor tracks to give the space; scooping everything (per-track smiley EQ) hollows the mix in context [EQ16] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **ii V quality signature** (w0.8): the cell is IDENTIFIED by fifths root motion PLUS quality sequence: mi7-7-ma7 in major, half-dim7-7-mi7 in minor (V stays dominant-quality in BOTH modes) — so distinctive that an unresolved ii-V still reads as the schema; generators must keep the quality string even when reharmonizing *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **swing 16th** (w0.76): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **blues turnaround** (w0.7): bars 11-12 ignition coil pulling the cycle back to bar 1: minimum a V7 in the final bar ('You Can't Do That'); maximum a full III-VI-II-V chain [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **minor blues** (w0.7): i7/iv7 become minor sevenths, V STAYS dominant; the third phrase swaps V-IV-i for ii-V-i because major-V falling to minor-iv sounds anticlimactic — the sanctioned jazz handshake inside blues form [Popular music: blues harmony] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **applied ii V cell** (w0.7): the WHOLE ii-V(-I) unit drops into foreign keys to tonicize any target (applied subdominant included — jazz extends applied chords beyond V); 'Afternoon in Paris' chains cells through bVII then bVI before coming home; an unresolved ii-V alone still creates the pull — motion without commitment, the reharmonizer's passport *(OMT2 'ii-V-I' chapter (Jazz), Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory/chapter/ii-v-i/ via curated:claude/2026-07-05 (wave31 jazz motion))*
- **chord lane vote** (w0.65): when you OWN the symbols, vote harmony from notes, never from audio: bar-wise duration x velocity weights, bass witnesses x2.5, b7 read for dominant color; muted transcription sketches still vote on imports [battery: 9/12 exact incl. 7s on 12-bar blues where the audio HMM scored 2/12; 4/4 on triads where audio heard nothing] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- also in this genre's DNA (lower weight): width by arrangement, expressive performance, symbolic unmask, functional substitution ii IV

## Inherited from boombap
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- layered snare: sample clap + synth snare body at -12 to -18
- groove boombap 56: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
- parallel thwack attack: on the parallel crush bus the ATTACK chooses the transient's character: 25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap — then blend under the dry until it's felt not heard [PARA]
- parallel density vs emphasis: two parallel-comp intents, two clocks: fast attack + slow release fills DENSITY under the dry transients; moderate attack + short release EMPHASIZES the transients — decide which the dry bus lacks before touching the knobs [PARA]
- groove transfer: a record's timing DNA (onset phase vs grid) extracts as a named groove and applies to NEW material at ~0.9 — on-grid notes move, off-grid feel is preserved; apply to hats/snare, keep kick straight [battery: 412/429 onsets learned from a real record; 80 notes moved on the flip]
- strophic form: AAA: one multi-phrase strophe repeated is the WHOLE song (Chuck Berry 'School Day'); the home form of blues, early hip hop, early rock'n'roll — verse-chorus displaced it after ~1970. Instrumental passes over the same pattern (solos) are still strophes

## Sound recipes (this palette, these moves)
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **tine kalimba**: faust kalimba: plucked tine (near-sine + inharmonic sparkle + thumb click) — lofi/afro signature; arpeggiate gently, let notes ring
- **motor vibes**: faust vibraphone: struck bar w/ 4.2Hz motor tremolo, long ring while held — jazz ballads, lofi warmth, soul interludes; sparse voicings, let the motor breathe
- **snare zones**: snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; tone 0.7 + decay 1.5 = fat lo-fi snare.
- **rhodes zones**: rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; gospel chords = sustain 0.5 + decay 2.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dilla', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -20..-12, band order low~lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
