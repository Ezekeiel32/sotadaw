---
name: sound-palette
version: 2
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
- Track count 5-9; every track earns its place; space via fx-usage.
