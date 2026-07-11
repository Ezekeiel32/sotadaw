// harp — plucked concert harp: bright pluck softening into a warm ring,
// gentle inharmonic shimmer. Glissandi = fast runs; cinematic/jazz color.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
dec    = hslider("decay", 0.9, 0.2, 2.5, 0.01);      // string ring (was 0.9)
pluckA = hslider("pluck", 0.55, 0, 1, 0.01);         // attack noise mix (was 0.55)
tone   = hslider("tone", 6500, 1500, 10000, 1);      // veil (was 6500)
pluck = no.noise * en.ar(0.001, 0.01, gate) : fi.resonbp(freq * 4.5, 2.5, 1.0);
body  = (os.osc(freq) + os.osc(freq * 2.002) * 0.3 + os.osc(freq * 2.997) * 0.12)
        * en.adsr(0.002, dec, 0.0, 0.2, gate);
process = (body + pluck * pluckA) * gain : fi.lowpass(2, tone) : *(0.608) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
