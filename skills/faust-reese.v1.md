---
name: faust-reese
version: 1
kind: sound-design
tags: [dnb, dubstep, garage, reese, bass, faust]
hard_constraints:
  - Reese core = 2-4 saws detuned ±0.5%..2%, summed and divided by voice count.
  - Follow with a lowpass; add a resonant stage for growl. Peak must stay <= 0.9 (trim after resonance).
  - Range MIDI 26-38; sustained notes (len >= 1 beat) — a reese is a pad-bass, not a one-shot.
sound_binding: instruments/reese.dsp
---
# Reese bass (validated golden version)

```faust
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 2000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
cut  = hslider("cutoff", 1200, 50, 12000, 1);
env  = en.adsr(0.01, 0.2, 0.85, 0.3, gate);
d = 0.015;
s = os.sawtooth(freq) + os.sawtooth(freq*(1+d)) + os.sawtooth(freq*(1-d)) + os.sawtooth(freq*(1+2*d));
process = s/4 * env * gain : fi.lowpass(3, cut) : fi.resonlp(cut, 4, 1) <: _,_;
```

Taste guidance:
- Wider detune (d=0.02+) = angrier beating; narrower (0.006) = smoother.
- LFO the cutoff for wobble (see the wobble instrument): `cut = 200 + 4000*(0.5+0.5*os.osc(rate))`.
- Resonant stages clip: this exact recipe peaked at 1.000 in probe 2 — trim with `: *(0.6)` or tanh after.
