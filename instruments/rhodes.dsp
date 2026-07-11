// Dilla-warm Rhodes: 2-op FM (ratio 2) with a decaying FM index for the bell-attack
// zones (inits = the original constants): bell = FM index scale (brightness of the
// strike), bark = how long the bright attack lasts s, decay = amp decay s,
// sustain = held level.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
bell = hslider("bell", 1.2, 0, 3, 0.01);
bark = hslider("bark", 0.4, 0.05, 1, 0.01);
dec  = hslider("decay", 1.2, 0.4, 3, 0.01);
sus  = hslider("sustain", 0.30, 0, 0.8, 0.01);
env  = en.adsr(0.005, dec, sus, 0.4, gate);
ienv = en.ar(0.001, bark, gate);           // FM index decays: bright attack -> mellow body
mod  = os.osc(freq*2) * (freq*2) * ienv * bell;
car  = os.osc(freq + mod);
process = car * env * gain : *(0.913) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
