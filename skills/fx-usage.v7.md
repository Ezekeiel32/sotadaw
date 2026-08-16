---
name: fx-usage
version: 7
kind: mixing
tags: [always, fx, space, depth, vst3, presets, rack, physics]
hard_constraints:
  - Dry mixes sound like demos. Melodic/lead tracks get space (fx_reverb and/or fx_delay); drums stay mostly dry (kick/808 ALWAYS dry).
  - Reverb mix 0.15-0.35 on sources, never on the master. Delay feedback <= 0.6.
  - fx chains go on the track ("fx": [...]), order matters: saturate -> delay -> reverb -> widen.
  - Never put fx_widen on mono-critical low end (808/kick/sub).
  - vst3 fx count against the 4-insert habit like any other; ONE character reverb per bus, not per track.
  - "A/B with \"bypass\": true on any fx entry (track/bus/master) — the plugin is created but disabled, settings survive, renders honor it. Toggle it back instead of re-authoring."
  - "SELECTION: when the context says SELECTED FX, that exact chain entry is THE subject — tweak its params (or bypass it) and leave the rest of the chain alone."
  - "MEASURED (dsp_bench.py, THE PHYSICS E5/E12, re-certed 2026-07-07): fx_saturate is now ADAA anti-aliased (antiderivative of tanh, single-rate) — musical-band aliasing -61.9 dBc at default drive 6 (IN the -60 budget; was -49 as a naive 1x tanh), -67.7 at drive 3, same tanh character (THD 2.92% vs 2.95%). Use it freely at drive <= 6; at EXTREME drive (9+) on very bright/near-Nyquist content residual fold-back returns (single-rate physics) — there keep mix < 1 or drop drive. fx_truepeak is clean (alias -160 dBc, FR flat 0.0 dB, 132-sample latency PDC-compensated) — trust it on the master."
---
# Using the FX rack (fx_reverb, fx_delay, fx_saturate, fx_widen, fx_pump, fx_deess)

Set via set_track_fx. Every entry accepts optional "bypass": true. Legal entry shapes:
`{"id": "fx_*", "params": {...}}` · `{"type": "eq"|"comp", "params": {...}}` ·
`{"id": "vst3:<plugin>", "preset": "<blob path>", "params": {...}}`.
The user hand-edits the SAME chain in the device rack (knobs persist into song.json);
their tweaks come back in get_song/get_selection. Recipes that work:
- Haunting lead/bell: [{"id":"fx_delay","params":{"time":<dotted-8th ms>,"feedback":0.45,"mix":0.25}},
  {"id":"fx_reverb","params":{"mix":0.3,"size":3.5,"damp":4000}}]  — dotted 8th ms = 45000/bpm*1.5
- Piano intimacy: fx_reverb mix 0.2 size 1.8 damp 5500 (small room, close).
- Pad width/motion: fx_widen width 1.5 rate 0.3 + fx_reverb mix 0.3 size 4.
- Grit/energy on keys/bass(non-sub): fx_saturate drive 8-12 tone 3500 mix 0.5-0.8
  (at drive 9+ on bright sources keep mix <= 0.8; physics in the MEASURED law above).
- Sidechain pump feel on pads/keys (house/trap alike): fx_pump rate = bpm/60 (quarter notes) or bpm/30
  (8ths), depth 0.4-0.7, release 0.2-0.35. Instantly "produced".
- Snare/clap tail: fx_reverb mix 0.18 size 1.5 — short, bright. Hats: dry or width 1.2 max.
- Sibilant vocal: fx_deess FIRST in the chain, pre-reverb (esses excite verbs) — freq 6500
  thresh -32 amount 12; harsher -> thresh -38 before more amount (>16 lisps); amount 0 = bypass.

## Modulation natives (2026-07-31): fx_chorus + fx_tremolo

fx_chorus — 3-tap true chorus (18ms base, taps AND sides phase-spread; NOT the flanger):
  {"id": "fx_chorus", "params": {"mix": 0.4, "rate": 0.8, "depth": 0.5, "voices": 3}}
  - Bachata/requinto + clean guitars: mix 0.45-0.6, rate 0.7-1.0 — THE genre sheen.
  - Dreampop/shoegaze washes: depth 0.7+, voices 3, on a pad or guitar bus.
  - 80s keys (rhodes/fm4_keys/organ): mix 0.3, subtle rate 0.5. Verified: mono source
    -> width -8.7dB, lr_corr 0.76, zero clipping.
  - voices 1 = a single modulated double (lighter than 3-tap thickness).

fx_tremolo — amplitude pulse, NOT fx_pump (that's sidechain-shaped):
  {"id": "fx_tremolo", "params": {"rate": 4.6, "depth": 0.5, "shape": 0.25, "spread": 0.0}}
  - Surf/soul guitar: rate 4-6Hz, depth 0.5-0.7, shape 0.3.
  - Ambient pads: slow rate 0.5-2, depth 0.3, spread 1.0 = AUTOPAN (L/R antiphase).
  - Dub organ chop: shape 0.9 (hard square), rate synced-ish to 8ths (bpm/60*2).
  - depth is duty-true: 0.5 averages -2.5dB — stage gain accordingly.

## The pro rack: vst3 fx + 291 factory fx presets (W19)

Any scanned VST3 works as an insert anywhere a faust fx goes — tracks, buses, master —
via set_track_fx / set_buses / update_song_meta master[] (all three validate ids +
preset paths):
  {"id": "vst3:Airwindows Consolidated"}          // default = a pro reverb
  {"id": "vst3:Surge XT Effects", "preset": "library/presets/surgefx/<name>.blob"}

The 291 curated Surge fx presets (40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser)
load via vst_presets — 'get' returns a ready use_as_fx entry. Taste rules:
- CHARACTER spaces (Large Church, plates, springs) go on a BUS with sends, faust fx_reverb
  stays for utility track space. One character space per song section.
- Surge Delay presets are tempo-aware creative delays — use for dub/ambient throws; keep
  faust fx_delay for rhythmic dotted-8ths.
- Distortion/EQ presets are INSERTS on the source track, pre-reverb.
- The Airwindows category inside Surge fx is EXPERIMENTAL — prefer the named families.

Checklist: every melodic track has SOME space; low end dry; one pumped element max;
re-render after — finish through master_report (see mix-headroom), not ear-of-faith.
