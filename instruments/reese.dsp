// DnB reese bass: wide-detuned saw stack -> lowpass + resonant growl
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 2000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
cut  = hslider("cutoff", 1200, 50, 12000, 1);
res  = hslider("res", 4, 1, 12, 0.1);               // growl Q (was 4)
det  = hslider("detune", 0.015, 0, 0.06, 0.001);    // stack width (was 0.015)
rel  = hslider("release", 0.3, 0.02, 1.5, 0.001);   // (was 0.3)
env  = en.adsr(0.01, 0.2, 0.85, rel, gate);
s = os.sawtooth(freq) + os.sawtooth(freq*(1+det)) + os.sawtooth(freq*(1-det)) + os.sawtooth(freq*(1+2*det));
process = s/4 * env * gain : fi.lowpass(3, cut) : fi.resonlp(cut, res, 1) : *(0.53) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
