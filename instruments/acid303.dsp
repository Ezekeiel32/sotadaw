// TB-303 acid: saw -> envelope-swept resonant lowpass with accent
// ZONE-ENRICHED (face law: a 303 without cutoff/res knobs is a letdown).
// Defaults are EXACTLY the old constants — render-neutral by construction.
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 2000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
acc  = hslider("accent", 0.6, 0, 1, 0.01);
cutBase = hslider("cutoff", 300, 80, 2000, 1);      // base cutoff (was the 300 constant)
envAmt  = hslider("envmod", 3500, 0, 8000, 1);      // filter-envelope sweep depth (was 3500)
res     = hslider("res", 8, 1, 16, 0.1);            // base resonance (was 8; accent still adds)
fdec    = hslider("decay", 0.18, 0.05, 0.6, 0.001); // the 303 filter-decay money knob (was 0.18)
fenv = en.adsr(0.005, fdec, 0.10, 0.10, gate);
aenv = en.adsr(0.005, 0.30, 0.60, 0.15, gate);
cutoff = (cutBase + envAmt*fenv*(0.5+acc)) : min(12000);
// analysis feedback: raw resonance peaked at 1.000 (0 dBFS) -> tanh soft-clip (authentic 303 drive) + headroom
process = os.sawtooth(freq) : fi.resonlp(cutoff, res+8*acc, 1) : *(aenv*gain) : ma.tanh : *(0.8) <: _,_;
