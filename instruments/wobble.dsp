// dubstep wobble: detuned saws -> resonant lowpass swept by an LFO
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 2000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
rate  = hslider("rate", 4, 0.1, 16, 0.01);          // wobble LFO speed (Hz)
base  = hslider("base", 200, 50, 2000, 1);          // sweep floor (was 200)
depth = hslider("depth", 4000, 200, 8000, 1);       // sweep depth (was 4000)
res   = hslider("res", 6, 1, 12, 0.1);              // (was 6)
env  = en.adsr(0.01, 0.2, 0.9, 0.2, gate);
lfo  = 0.5 + 0.5*os.osc(rate);
cut  = base + depth*lfo;
s = os.sawtooth(freq) + os.sawtooth(freq*1.01);
// analysis feedback: resonant sweep peaked at 1.000 (0 dBFS) -> clean headroom trim, keep the sweep undistorted
process = s/2 * env * gain : fi.resonlp(cut, res, 1) : *(0.6) : *(0.433) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
