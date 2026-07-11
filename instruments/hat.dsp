// closed hi-hat: white noise -> highpass -> resonant bandpass sizzle, very fast decay
// zones (inits = the original constants): decay opens toward open-hat, tone = bp centre,
//   sizzle = bp Q
import("stdfaust.lib");
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
decay  = hslider("decay", 0.05, 0.01, 0.6, 0.001);
tone   = hslider("tone", 10000, 4000, 16000, 10);
sizzle = hslider("sizzle", 2, 0.5, 8, 0.01);
env  = en.ar(0.001, decay, gate);
process = no.noise : fi.highpass(4, 8000) : fi.resonbp(tone, sizzle, 1) : *(env*gain) : *(0.882) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
