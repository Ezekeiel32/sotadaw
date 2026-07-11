---
name: faust-writing
version: 1
kind: language
tags: [faust, always]
hard_constraints:
  - Every instrument MUST expose zones named exactly: freq (hslider, if pitched), gain (hslider 0..1), gate (button). The host maps MIDI to these names.
  - Output MUST be stereo: end the process expression with `<: _,_` (or produce 2 channels).
  - `import("stdfaust.lib");` first line. Use namespaced stdlib: os.*, fi.*, en.*, no.*, ma.*.
  - Never let output exceed |1.0|: keep gain envelopes*levels <= ~0.9, or soft-clip with `: ma.tanh`.
  - Keep per-sample CPU bounded: no unbounded recursion; Faust guarantees this if it compiles.
---
# Writing Faust instruments for this DAW (validated idioms)

Standard skeleton (all 13 shipped instruments follow it):

```faust
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
env  = en.adsr(0.005, 0.2, 0.7, 0.2, gate);   // or en.ar(att, rel, gate) for one-shots
process = os.sawtooth(freq) * env * gain : fi.lowpass(2, 3000) <: _,_;
```

Validated building blocks:
- Oscillators: `os.osc` (sine), `os.sawtooth`, `os.triangle`; noise: `no.noise`.
- Envelopes: `en.ar(a, r, gate)` for drums/one-shots; `en.adsr(a, d, s, r, gate)` for sustained.
- Filters: `fi.lowpass(order, hz)`, `fi.highpass(order, hz)`, `fi.resonlp(hz, q, gain)`, `fi.resonbp(hz, q, gain)`.
- Saturation: `: ma.tanh` after a gain boost gives analog-style drive (used on 808 + hard kick).
- Pitch envelopes: `os.osc(freq * (1 + amount*en.ar(0.001, time, gate)))` — the 808/kick "drop".
- FM: `os.osc(freq + os.osc(freq*ratio) * (freq*ratio) * indexEnv)` — ratio 2 = Rhodes-like, 3.5 = metallic bell.
- Detune stacks: sum `os.sawtooth(freq*(1+d))` for d in ±0.005..0.03, divide by voice count.

Compile-check discipline: after writing, the host validates with the Faust compiler and returns
stderr on failure — read the error line number, fix, resubmit. Common errors: missing `;`,
unbalanced parens, using `min(a,b)` where partial application `: min(x)` is meant, wrong arg counts.
