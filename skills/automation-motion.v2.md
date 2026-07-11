---
name: automation-motion
version: 2
kind: mixing
tags: [always, automation, motion, build, drop, transition]
hard_constraints:
  - MOTION IS MUSIC. A section change without any parameter motion is a missed transition — builds/drops get at least one automation arc.
  - Automation values are REAL units (Hz for cutoff, dB for gainDb, the zone's own range otherwise — check list_plugin_params). vst3 params are 0..1.
  - "SHAPE THE SEGMENT: point curve -1..1 (engine-verified). Builds = curve 0.6..0.9 on the START point (late-bloom: holds, then accelerates INTO the drop — linear builds feel early and flat). Post-drop settles/duck releases = curve -0.5..-0.8 (early-jump). Plain rides = 0."

  - Never automate 808/kick/sub gainDb for effect (only corrective rides <=3dB); never automate anything on the master limiter.
  - Filter builds end where the drop begins — the cutoff must reach its target ON the drop beat, not after.
  - Keep sends on kick/808 at zero (dry low end); pads/keys/leads are the send customers.
---
# Automation & motion (the difference between a demo and a record)

## The tools
- `automate(song, track, target, points)` — target `gainDb` | `pan` | `fx[i].<param>` | `source.<param>`;
  song-scope (no track): `masterGainDb` | `master[i].<param>`. Points `[{beat, v}]`, linear interpolation.
- `list_plugin_params(song)` — EVERY knob in the session with current value + range (faust zones, VST3 params, send levels).
- `set_track_param` — static set (no motion). `set_buses` + `update_track sends` — shared spaces.

## Recipes (beats are absolute; 1 bar = 4 beats)
- **Filter build into a drop at bar N**: put `fx_filter` first in the track's chain (`set_track_fx`), then
  `automate fx[0].cutoff`: `[{beat: (N-8)*4, v: 250}, {beat: N*4, v: 9000}]` (8-bar rise; 4-bar for short builds).
  res 1.5–3 makes the sweep sing; >4 screams (use sparingly).
- **Volume swell** (pads/strings into a section): gainDb `[{beat: a, v: -18}, {beat: b, v: -6}]`. Corrective rides: ±2–3 dB.
- **Width bloom on the hook**: fx_widen on the lead, automate `fx[i].width` from 0.6 (verse) to 1.6 (hook), back after.
- **Reverb throw**: put the reverb on a BUS (`set_buses [{id:"verb", fx:[{id:"fx_reverb", params:{mix:1.0}}]}]`
  — mix 1.0 on a bus because the send level does the balancing). Route with `sends:[{bus:"verb",gainDb:-12}]`.
  Automate the SEND for throws: the send gain appears in list_plugin_params ("Aux Send") — spike it on the last
  beat before a section change, duck it back.
- **Pump/sidechain feel**: `fx_pump` on pads/keys (rate = bpm/60 Hz, depth 0.5–0.8) — do NOT put it on drums.
- **Pan motion**: slow pan drift on ear-candy percs (`pan` −0.4→0.4 over 8 bars), never on kick/snare/808/lead vocals.
- **Outro/intro**: masterGainDb song-scope fades are allowed the last/first 2 bars only.

## Verify your motion
After rendering, `analyze_wav` shows `rms_by_quarter_db` and `centroid_by_quarter_hz` — a filter build must show
centroid RISING into the drop quarter; a swell shows rms rising. If the gradient is flat, the automation didn't land
(wrong target name or wrong fx index) — check list_plugin_params and fix.
