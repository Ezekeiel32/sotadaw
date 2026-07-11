// karplus-ish pluck: noise burst into tuned comb, warm lowpass
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 40, 3000, 0.01);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
damp    = hslider("damp", 6000, 1000, 10000, 1);        // string damping (was 6000)
sus     = hslider("sustain", 0.985, 0.9, 0.999, 0.0001); // comb feedback (was 0.985)
tone    = hslider("tone", 5200, 800, 10000, 1);         // output veil (was 5200)
excite = en.ar(0.0005, 0.01, gate) * no.noise;
ks = excite : (+ : de.fdelay4(4096, ma.SR/freq - 1)) ~ (fi.lowpass(1, damp) : *(sus));
process = ks : fi.lowpass(2, tone) : *(gain*0.9) <: _,_;
