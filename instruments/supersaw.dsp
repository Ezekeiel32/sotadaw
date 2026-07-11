// supersaw: 7 detuned saws, ADSR, gentle lowpass
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq   = hslider("freq", 220, 20, 4000, 0.001);
gain   = hslider("gain", 0.5, 0, 1, 0.01);
gate   = button("gate");
detune = hslider("detune", 0.02, 0, 0.1, 0.001);
cutoff = hslider("cutoff", 7000, 500, 12000, 1);    // the veil lifts (was 7000)
att    = hslider("attack", 0.02, 0.001, 1.0, 0.001);  // (was 0.02)
rel    = hslider("release", 0.3, 0.02, 2.0, 0.001);   // (was 0.3)
env = en.adsr(att, 0.2, 0.8, rel, gate);
saw(d) = os.sawtooth(freq*(1+d));
voices = saw(-3*detune)+saw(-2*detune)+saw(-1*detune)+saw(0)+saw(1*detune)+saw(2*detune)+saw(3*detune);
process = voices/7 * env * gain : fi.lowpass(3, cutoff) : *(0.869) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
