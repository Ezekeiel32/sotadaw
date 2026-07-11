---
name: sound-palette
version: 4
kind: sound-design
tags: [always, palette, samples, vst, layering]
hard_constraints:
  - Sub bass / 808 is ALWAYS a faust source (kick_808 for glides/trap, sub_clean for static bass, reese for dnb growl).
  - Real drums from sample kits; DESIGNED drums from faust (kick_punch, clap_909, hat_metal) — layering both is the pro move.
  - Pitched sample kits (piano/epiano/strings/warmpad/pluckbass/choir) repitch full-range.
  - vst3 must exist in scan cache (Dexed installed). One vst3 track max until presets land.
---
# The palette (samples x designed-faust x vst — hybrid is what sounds REAL)

FAUST instruments (designed, ours):
- Low end: kick_808 (glide sub, trap), kick_punch (tight click+body, house/techno), sub_clean (static sub), reese (dnb growl), hardkick (distorted).
- Drums: clap_909 (designed clap), hat_metal (metallic 808-style hat w/ decay param), snare (body layer), hat (filtered-noise).
- Melodic: pluck2 (karplus string), keys_dark (dark EP), pad_motion (evolving pad w/ autopan), fmbell, rhodes, supersaw, acid303, wobble.
- FOUNDATIONS (battery-verified f0/centroid/tail): brass_stab (horn section: filter-env blat + pitch scoop — stabs short, swells held; `bite` zone = aggression), clav_funk (Stevie clav: 16th staccato comping, ghost velocities 0.2-0.4), organ_soul (drawbar organ w/ Hammond percussion + rotary — gospel/soul glue), strings_disco (Solina ensemble: chorused saw stack, slow attack — disco octave pads).
- RHYTHM SECTION (battery-verified): guitar_grit (Karplus-Strong -> tanh drive -> cab presence; play power chords as NOTES root-5-oct, `drive` 0..1 twang->grit — rock/metal/punk/indie/blues/country), log_drum (THE amapiano bass: woody pitch-drop knock + sub tail — sequence as the bassline in the kick's holes), timpani (tuned cinematic drum: strike drop + long boom; fast low-vel repeats = rolls).
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
- Track count 5-9; every track earns its place; space via fx-usage.
