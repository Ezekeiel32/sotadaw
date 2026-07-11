// marimba — struck rosewood bar: fundamental + the characteristic ~4th partial
// (tuned bars ring near 4x), brief mallet thump, exponential decay, no sustain.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
dec    = hslider("decay", 0.5, 0.1, 2, 0.01);       // bar ring (was 0.5)
shineA = hslider("shine", 0.45, 0, 1, 0.01);        // 4th-partial level (was 0.45)
mallet = hslider("mallet", 0.25, 0, 1, 0.01);       // thump level (was 0.25)
body  = os.osc(freq) * en.adsr(0.002, dec, 0.0, 0.12, gate);
shine = os.osc(freq * 3.93) * en.adsr(0.001, 0.12, 0.0, 0.05, gate) * shineA;
thump = no.noise * en.ar(0.001, 0.01, gate) * mallet : fi.resonlp(freq * 2.0, 1.5, 1.0);
process = (body + shine + thump) * gain : fi.lowpass(2, 6000) : *(0.646) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
