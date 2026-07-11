---
name: fx-usage
version: 2
kind: mixing
tags: [always, fx, space, depth, vst3, presets]
hard_constraints:
  - Dry mixes sound like demos. Melodic/lead tracks get space (fx_reverb and/or fx_delay); drums stay mostly dry (kick/808 ALWAYS dry).
  - Reverb mix 0.15-0.35 on sources, never on the master. Delay feedback <= 0.6.
  - fx chains go on the track ("fx": [...]), order matters: saturate -> delay -> reverb -> widen.
  - Never put fx_widen on mono-critical low end (808/kick/sub).
  - vst3 fx count against the 4-insert habit like any other; ONE character reverb per bus, not per track.
---
# Using the FX rack (fx_reverb, fx_delay, fx_saturate, fx_widen, fx_pump)

Set via set_track_fx. Recipes that work:
- Haunting lead/bell: [{"id":"fx_delay","params":{"time":<dotted-8th ms>,"feedback":0.45,"mix":0.25}},
  {"id":"fx_reverb","params":{"mix":0.3,"size":3.5,"damp":4000}}]  — dotted 8th ms = 45000/bpm*1.5
- Piano intimacy: fx_reverb mix 0.2 size 1.8 damp 5500 (small room, close).
- Pad width/motion: fx_widen width 1.5 rate 0.3 + fx_reverb mix 0.3 size 4.
- Grit/energy on keys/bass(non-sub): fx_saturate drive 8-12 tone 3500 mix 0.5-0.8.
- Sidechain pump feel on pads/keys (house/trap alike): fx_pump rate = bpm/60 (quarter notes) or bpm/30
  (8ths), depth 0.4-0.7, release 0.2-0.35. Instantly "produced".
- Snare/clap tail: fx_reverb mix 0.18 size 1.5 — short, bright. Hats: dry or width 1.2 max.

## The pro rack: vst3 fx + 291 factory fx presets (W19)

Any scanned VST3 works as an insert anywhere a faust fx goes — tracks, buses, master:
  {"id": "vst3:Airwindows Consolidated"}          // default = a pro reverb
  {"id": "vst3:Surge XT Effects", "preset": "library/presets/surgefx/<name>.blob"}

The 291 curated Surge fx presets (40 Reverb2 spaces, 29 delays, distortion/EQ/chorus/phaser)
load via vst_presets (query by name/category, e.g. query="Reverb 2") — 'get' returns a ready
use_as_fx entry. Taste rules:
- CHARACTER spaces (Large Church, plates, springs) go on a BUS with sends, faust fx_reverb
  stays for utility track space. One character space per song section.
- Surge Delay presets are tempo-aware creative delays — use for dub/ambient throws; keep
  faust fx_delay for rhythmic dotted-8ths.
- Distortion/EQ presets are INSERTS on the source track, pre-reverb.
- The Airwindows category inside Surge fx is EXPERIMENTAL — prefer the named families.

Checklist: every melodic track has SOME space; low end dry; one pumped element max; character
spaces on buses via sends; re-render after.
