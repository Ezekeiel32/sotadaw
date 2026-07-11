---
name: faust-808
version: 1
kind: sound-design
tags: [trap, drill, 808, bass, hiphop, faust]
hard_constraints:
  - 808 core = single sine oscillator (mono-compatible sub). No detuned stacks below 100 Hz.
  - Pitch-drop envelope on the attack ("boom"), 2x-6x freq falling to fundamental in 30-70 ms.
  - Long amp decay (0.6-1.2 s), zero sustain, saturate with tanh for harmonics on small speakers.
  - Write pitches in the 808's range: MIDI 24-40 (C1-E2). The pattern IS the bassline.
  - Overlapping 808 notes must choke (host retriggers gate; keep releases <= 0.2 s so tails cut fast).
sound_binding: instruments/kick_808.dsp
---
# The 808 (validated golden version — probe 1+2, "not bad at all" verdict)

```faust
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 400, 0.001);
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
pitchenv = en.ar(0.001, 0.07, gate);              // fast 0->1->0: the "boom" drop
ampenv   = en.adsr(0.001, 0.9, 0.0, 0.15, gate);  // long tail, no sustain
sub = os.osc(freq * (1 + 3*pitchenv));
process = (sub * 1.4 : ma.tanh) * ampenv * gain <: _,_;
```

Taste guidance:
- Tune 808s to the song key; classic trap lines walk root -> b3 -> 4 -> 5 or descend root, b7, b6, 5.
- Long notes on bar downbeats (len 1.0-1.5 beats), short passing notes (len 0.3-0.5) for movement.
- Harder style: raise the tanh drive (sub * 2.0+) and shorten decay. Softer: drive 1.1, longer decay.
- Give the 808 the most gain of any track; everything else sits around it (see mix-headroom skill).
