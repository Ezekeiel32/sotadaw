// kalimba — plucked metal tine: near-sine fundamental with a slightly
// inharmonic high partial, thumb-click attack, quick ring. Lofi/afro signature.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
dec    = hslider("decay", 0.4, 0.1, 1.5, 0.01);      // tine ring (was 0.4)
spark  = hslider("sparkle", 0.35, 0, 1, 0.01);       // overtone (was 0.35)
clik   = hslider("click", 0.3, 0, 1, 0.01);          // thumb click (was 0.3)
tine  = os.osc(freq) * en.adsr(0.001, dec, 0.0, 0.1, gate);
sparkle = os.osc(freq * 2.08) * en.adsr(0.001, 0.09, 0.0, 0.04, gate) * spark;
click = no.noise * en.ar(0.0005, 0.006, gate) * clik : fi.highpass(1, 1200);
process = (tine + sparkle + click) * gain : fi.lowpass(2, 7000) : *(0.664) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
