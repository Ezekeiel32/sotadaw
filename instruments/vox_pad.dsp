// vox_pad — designed choir "ah": detuned saws through two vowel formants,
// slow bloom, gentle shimmer. ZONE-ENRICHED (face law) — defaults exact.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
att  = hslider("attack", 0.25, 0.02, 2, 0.001);     // bloom (was 0.25)
rel  = hslider("release", 0.6, 0.05, 3, 0.001);     // (was 0.6)
shm  = hslider("shimmer", 0.04, 0, 0.15, 0.001);    // (was 0.04)
tone = hslider("tone", 3000, 800, 8000, 1);         // output veil (was 3000)
env  = en.adsr(att, 0.4, 0.85, rel, gate);
src  = os.sawtooth(freq * 0.996) + os.sawtooth(freq) + os.sawtooth(freq * 1.004);
ah(x) = x <: (fi.resonbp(700, 4.5, 1.0) * 1.3, fi.resonbp(1050, 5.5, 1.0) * 0.6, fi.lowpass(2, 800) * 0.8) :> _;
shim = 1.0 + shm * os.osc(0.9);
process = (src / 3.0 : ah) * env * shim * gain : fi.lowpass(2, tone) : *(0.393) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
