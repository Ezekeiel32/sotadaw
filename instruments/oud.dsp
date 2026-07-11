// oud — the Arab lute: warm nylon-ish pluck, fretless slides, deep round body,
// short sustain, no metallic ring. Khaleeji/chaabi/arabesk/dabke family lead.
// Karplus-ish: excited noise burst into a tuned comb + warm body lowpass.
// Research: docs/research_genre_expansion_w4.md addendum. ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq = hslider("freq", 220, 60, 1200, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
warmth = hslider("warmth", 2400, 800, 6000, 1);    // body lowpass Hz (oud is DARK)
ring   = hslider("ring", 0.994, 0.98, 0.999, 0.0001); // string feedback (decay)
pick   = hslider("pick", 0.4, 0, 1, 0.01);         // risha attack level
exc = no.noise * en.ar(0.0005, 0.006, gate);        // risha (plectrum) burst
dl = ma.SR / freq;
string = exc : (+ : de.fdelay4(4096, dl - 1)) ~ (fi.lowpass(1, warmth) : *(ring));
body = string : fi.resonlp(freq * 2.2, 1.2, 1.0);   // round wooden bowl
snapfx = exc * pick : fi.resonbp(1800, 1.5, 1.0);
process = (body + snapfx) * gain * 0.7 : fi.lowpass(2, 5200) <: _,_;  // vel-1.0 headroom (gain zone engine-driven)
