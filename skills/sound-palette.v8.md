---
name: sound-palette
version: 8
kind: sound-design
tags: [always, palette, samples, vst, layering]
hard_constraints:
  - Sub bass / 808 is ALWAYS a faust source (kick_808 for glides/trap, sub_clean for static bass, reese for dnb growl).
  - Real drums from sample kits; DESIGNED drums from faust (kick_punch, clap_909, hat_metal) — layering both is the pro move.
  - Pitched sample kits (piano/epiano/strings/warmpad/pluckbass/choir) repitch full-range.
  - vst3 must exist in scan cache (Dexed installed). One vst3 track max until presets land.
  - WORLD WINDS/BOWED (duduk/ney/shakuhachi/pan_flute/zurna/bagpipes/harmonica/bandoneon/erhu) + EXOTIC SYNTHS (chiptune_pulse/chip_bass/chip_noise/phase_distortion/formant_vox/additive_harm) are FAUST voices — pitched, tweakable, and play INSTANTLY via JIT. Reach for them by name; don't force a VST or a generic saw when a real-world voice fits.
---
# The palette (samples x designed-faust x vst — hybrid is what sounds REAL)

FAUST instruments (designed, ours):
- Low end: kick_808 (glide sub, trap), kick_punch (tight click+body, house/techno), sub_clean (static sub), reese (dnb growl), hardkick (distorted).
- Drums: clap_909 (designed clap), hat_metal (metallic 808-style hat w/ decay param), snare (body layer), hat (filtered-noise).
- Melodic: pluck2 (karplus string), keys_dark (dark EP), pad_motion (evolving pad w/ autopan), fmbell, rhodes, supersaw, acid303, wobble.
- FOUNDATIONS (battery-verified f0/centroid/tail): brass_stab (horn section: filter-env blat + pitch scoop — stabs short, swells held; `bite` zone = aggression), clav_funk (Stevie clav: 16th staccato comping, ghost velocities 0.2-0.4), organ_soul (drawbar organ w/ Hammond percussion + rotary — gospel/soul glue), strings_disco (Solina ensemble: chorused saw stack, slow attack — disco octave pads).
- RHYTHM SECTION (battery-verified): guitar_grit (Karplus-Strong -> tanh drive -> cab presence; play power chords as NOTES root-5-oct, `drive` 0..1 twang->grit — rock/metal/punk/indie/blues/country), log_drum (THE amapiano bass: woody pitch-drop knock + sub tail — sequence as the bassline in the kick's holes), timpani (tuned cinematic drum: strike drop + long boom; fast low-vel repeats = rolls).
- SECTIONS & LEADS (battery-verified): sax_section (formant reed w/ breath + late vibrato — bigband soli/shout, merengue jaleos; legato), cine_brass (dark saw wall, filter blooms SLOWER than amp, `swell` 0..1 — hold whole notes for trailer swells; brass_stab stays the funk stab), flute_lead (breathy topline — jazz/bossa heads, trap flute, highlife runs), strings_stacc (spiccato ostinato engine: 8th/16th cells under cine_brass+timpani = the trailer trio; also disco stabs).
- WORLD WINDS & BOWED (foundry-o48, JIT render-proven — the biggest acoustic gap, filled): duduk (Armenian apricot double-reed LAMENT: dark warm cry + slow deep vibrato + attack pitch-`scoop`; automate pitch for portamento — cinematic sorrow, Armenian/folk), ney (breath-forward end-blown Sufi flute — the air IS the tone, warm/reedy), shakuhachi (Japanese bamboo: breathy, meri/kari `bend`, muraiki noisy attack — meditative/Japanese), pan_flute (stopped-pipe Andean: bright chiff, quick — folk/pop hook), zurna/shehnai (conical double-reed shawm: PIERCING nasal `buzz`, loud, sustained — Balkan wedding / Anatolian / Indian-oboe lead that cuts through anything), bagpipes (reedy chanter over a CONSTANT `drone` you set to the tune's tonic Hz — Celtic; play gapless/legato), harmonica (beating reed pair + cupped `cup` wah + draw-`bend` — blues/folk/roots), bandoneon (3 musette reed banks + bellows tremolo + chiff — tango/nuevo/chanson/folk), erhu (Chinese BOWED 2-string, no fingerboard: nasal snakeskin formant + wide blooming vibrato; automate pitch for its glissando — the crying "Chinese violin").
- EXOTIC / RETRO SYNTH ENGINES (foundry-o48, JIT): chiptune_pulse (8-bit lead — `duty` 0.5=square/0.25=reedy/0.125=nasal + PWM breathe + NES `drop` attack-blip), chip_bass (NES stepped-triangle bass, `steps`=16 = the 4-bit stairstep), chip_noise (LFSR chip drums/hats — `freq`=band center, `metal` narrows white->pitched), phase_distortion (Casio-CZ voice — `dcw` 0.5=sine -> lower=buzzy resonant; glassy/digital, NOT FM or subtractive), formant_vox (the SINGING synth / talkbox — `vowel` morphs Ah->Ee->Oo; AUTOMATE `vowel` to make it TALK; vocoder source, robot vox, synth-choir), additive_harm (Kawai drawbar-additive — `bright` upper-partial tilt + `odd`/even balance; glassy bell -> full organ -> pad by release length).
- WORLD RHYTHM & STRING BAND (2026-07-31, register-court certified): trumpet_lead (melodic SOLO trumpet: lip-settle, late vibrato, `bright` bloom — balkan/salsa/ska/mariachi lines; brass_stab stays the stab), tuba (wind bass, `bark` edge — oompah = staccato root-fifth quarters; held = swell), darbuka (goblet drum, PITCH = STROKE: low DUM / high TEK — write maqsum as a two-pitch line; arabesk/dabke), banjo (KS string into head-pot resonator — articulate 16th rolls, `pick`/`pot`), guira (metal scraper: low chick / high open sweep — bachata 8ths, sweep on the 4th), tumbi (choked nasal ostinato lute, G4-C5 — bhangra), saz (doubled-course `shimmer` chorus — arabesk lead, UNISON melody + fast grace notes), mbira (machachara `buzz` rides each tine — chimurenga; interlock two lanes an octave apart).
- VELOCITY = BREATH/PICK FORCE on the world band: filter cut follows vel — soft plays DARK, 1.0 = full blare/bite. Write real dynamics (leads 0.75-0.95, phrase peaks 1.0); flat vel-1.0 lines sound like a machine.
- NEW VOICES PLAY INSTANTLY (JIT): write_instrument compiles + validates, and the engine plays UNREGISTERED .dsp via the libfaust interpreter with zero rebuilds — design a sound mid-session and sequence it immediately (all the WORLD + EXOTIC voices above landed this way).
FX (set_track_fx): fx_reverb, fx_delay, fx_saturate, fx_widen, fx_pump — see fx-usage skill.

SAMPLE kits: gm_drums (36 kick, 38/40 snare, 39 clap, 42/44/46 hats, 49 crash, 51 ride, toms, perc),
piano, epiano, strings, warmpad, pluckbass, choir (full-range multisampled).
VST3: Dexed (DX7 FM) — FM keys/bells; optional params fuzzy-match.

Layer recipes:
- Trap kick: kick_808 (sub, loudest) + gm_drums 36 (attack, -5) — stagger.
- Fat clap: gm_drums 39 + clap_909 at -6 same hits; add faust snare body -12 for weight.
- Hats groove: gm_drums 42 grid + hat_metal accents (decay 0.08) on key hits.
- House kick: kick_punch alone (it's designed for it).
- Lush pad: pad_motion + strings kit same chords, one octave apart, both quiet.
- Funk horns: brass_stab unison hits on the +of-2 (short len 0.15-0.25, vel 0.9) answered by clav_funk 16th chatter (vel 0.25-0.45); organ_soul holds pads underneath at -8.
- Disco lift: strings_disco octave pads + four-floor kick_punch + offbeat open hats; strings swell (gainDb automation curve 0.7) into every chorus.
- SELF-SAMPLED melodic: sota_keys (rhodes zones) / sota_bass (warm zones) — OUR multisampled instruments; prefer over piano/pluckbass kits when warmth matters.
- Rock wall: guitar_grit power-chord 8ths (drive 0.8) doubled L/R with pan -0.4/+0.4 and 10ms offset; bass_warm roots; layered_snare backbeat.
- Amapiano engine: log_drum bassline answering a sparse kick (x..x..x. cell), shaker 16ths at vel 0.3, huge pad space.
- Trailer hits: timpani + kick_punch same downbeats every 4 bars; strings_disco ostinato 8ths; brass_stab swells (bite 0.9).
- Cinematic lament (film/trailer/world): duduk lead (long legato, pitch automated for portamento) + erhu counter-line answering in the gaps + additive_harm pad (odd 0.4, long release) underneath; one character reverb on a bus.
- Chiptune / 8-bit-hyperpop: chiptune_pulse lead (duty 0.25) + chip_bass (steps 16) + chip_noise hats (metal 0.2) + chip_noise snare (freq ~200, metal 0.5) — keep it DRY, let the aliasing bite.
- Vocal-synth hook: formant_vox with a `vowel` automation curve (Ah on downbeats -> Ee on lifts) doubling the melody an octave down = a "talking" synth-choir; add fx_delay dotted-8th.
- Middle-Eastern / Balkan lead: zurna melody (loud, nasal) over a bagpipes/drone bed (drone = tonic Hz) + hand percussion — the wedding-band cut.
- World-fusion pad: ney or shakuhachi sustained (breath high) + additive_harm (bright 0.7) an octave up, both quiet = an exotic, breathing bed.
- Balkan brass band: trumpet_lead melody (grace-note pickups) + brass_stab answers + tuba oompah (root 1/3, fifth 2/4) + snare rolls — fast 2/4, everything FORWARD.
- Bachata engine: clean_chime_guitar requinto syncopation + guira (low-low-low-HIGH) + two-pitch conga + bass roots on 1&5 — romantic minor.
- Arabesk groove: saz melody UNISON w/ strings_stacc 8va + darbuka maqsum (DUM . TEK TEK DUM . TEK .) + low pluck counter — Hijaz/Phrygian, no chord stacks.
- Bluegrass drive: banjo forward-roll 16ths + fiddle long bows + upright_bass root-fifth + brush_snare train — fast majors.
- Bhangra lift: dhol low-DHA accents + tumbi 16th ostinato + zurna hook + claps 2&4 — D mixolydian ~100bpm.
- Chimurenga wheel: two interlocked mbira lanes (offset a beat, 8va apart, buzz 0.6) + shaker 16ths + muted guitar skanks + soft bass pulse — hypnotic 12/8.
- Track count 5-9; every track earns its place; space via fx-usage.
