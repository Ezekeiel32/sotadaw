---
name: fx-usage
version: 1
kind: mixing
tags: [always, fx, space, depth]
hard_constraints:
  - Dry mixes sound like demos. Melodic/lead tracks get space (fx_reverb and/or fx_delay); drums stay mostly dry (kick/808 ALWAYS dry).
  - Reverb mix 0.15-0.35 on sources, never on the master. Delay feedback <= 0.6.
  - fx chains go on the track ("fx": [...]), order matters: saturate -> delay -> reverb -> widen.
  - Never put fx_widen on mono-critical low end (808/kick/sub).
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
Checklist: every melodic track has SOME space; low end dry; one pumped element max; re-render after.
