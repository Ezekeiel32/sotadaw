// additive_harm — Kawai-K5000-style additive / drawbar voice: a stack of 8 sine
// partials summed directly. `bright` tilts energy toward the upper harmonics (dark
// organ -> glassy bell); `odd` balances odd vs even partials (1=hollow/clarinet-ish,
// 0.5=full/organ). Sustained release = organ/pad; short release = struck bell.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 3000, 0.001);
gain = hslider("gain", 0.75, 0, 1, 0.01);
gate = button("gate");
bright = hslider("bright", 0.5, 0, 1, 0.01);     // upper-partial tilt
odd    = hslider("odd", 0.5, 0, 1, 0.01);        // odd/even balance
att = hslider("attack", 0.01, 0.001, 1, 0.001);
rel = hslider("release", 0.4, 0.02, 3, 0.001);
oddw(n) = select2((int(n) % 2) == 1, 1.0 - odd, 0.5 + 0.5*odd);  // even->(1-odd), odd->(.5+.5odd)
tilt = 2.0 - 1.3*bright;                          // harmonic rolloff exponent
partial(n) = os.osc(freq*n) * oddw(n) / pow(n, tilt);
stack = sum(i, 8, partial(i+1));
env = en.adsr(att, 0.3, 0.8, rel, gate);
process = stack * env * gain * 0.5 <: _,_;
