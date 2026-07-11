// clean sub bass: pure sine + gentle 2nd harmonic, tight envelope (non-808 basslines)
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 300, 0.01);
gain = hslider("gain", 0.85, 0, 1, 0.01);
gate = button("gate");
harm = hslider("harmonic", 0.15, 0, 0.6, 0.01);     // 2nd-harmonic blend (was 0.15)
dec  = hslider("decay", 0.15, 0.02, 0.6, 0.001);    // envelope decay (was 0.15)
rel  = hslider("release", 0.12, 0.02, 0.5, 0.001);  // envelope release (was 0.12)
env = en.adsr(0.004, dec, 0.8, rel, gate);
process = (os.osc(freq) + harm*os.osc(freq*2)) * env * gain : ma.tanh <: _,_;
