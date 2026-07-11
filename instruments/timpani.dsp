// timpani — tuned orchestral drum: sine fundamental with a slight strike
// pitch-drop + filtered noise mallet attack, long boomy decay. Rolls = fast
// repeated notes at low vel (trailer_build technique).
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 82, 20, 2000, 0.001);   // E2 default
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
penv = en.ar(0.001, 0.09, gate);
dec     = hslider("decay", 1.1, 0.3, 3.0, 0.01);       // drum ring (was 1.1)
bend    = hslider("bend", 0.06, 0, 0.2, 0.001);        // strike pitch-drop (was 0.06)
malletA = hslider("mallet", 0.5, 0, 1.2, 0.01);        // felt attack (was 0.5)
tone = os.osc(freq * (1.0 + bend * penv)) * en.adsr(0.002, dec, 0.0, 0.25, gate);
mallet = no.noise * en.ar(0.001, 0.018, gate) : fi.resonlp(freq * 3.5, 2.5, 1.0);
process = (tone + mallet * malletA) * gain : fi.lowpass(2, 1700) : *(0.835) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
