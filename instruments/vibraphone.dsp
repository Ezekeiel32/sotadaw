// vibraphone — struck metal bar with motor tremolo: fundamental + ~4x shimmer,
// long sustain while held, the signature slow amp wobble. Jazz ballads, lofi.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
dec    = hslider("decay", 1.4, 0.3, 3.5, 0.01);        // bar ring (was 1.4)
motorA = hslider("motor", 0.22, 0, 0.5, 0.001);        // tremolo depth (was 0.22)
shineA = hslider("shine", 0.4, 0, 1, 0.01);            // 4x partial (was 0.4)
motor = 1.0 + motorA * os.osc(4.2);
bar   = os.osc(freq) * en.adsr(0.002, dec, 0.25, 0.4, gate);
shine = os.osc(freq * 3.98) * en.adsr(0.001, 0.15, 0.0, 0.05, gate) * shineA;
mallet = no.noise * en.ar(0.001, 0.007, gate) * 0.2 : fi.resonlp(freq * 3.0, 2.0, 1.0);
process = (bar * motor + shine + mallet) * gain : fi.lowpass(2, 6000) : *(0.578) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
