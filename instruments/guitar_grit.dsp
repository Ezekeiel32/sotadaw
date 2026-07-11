// guitar_grit — driven electric guitar: Karplus-Strong string into a waveshaper
// and cab-ish filtering. Play power chords as NOTES (root-5-octave per
// power_chords technique); "drive" 0..1 = clean twang -> full grit. String
// damps naturally on release (no hung ring).
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq  = hslider("freq", 110, 20, 2000, 0.001);
gain  = hslider("gain", 0.65, 0, 1, 0.01);
gate  = button("gate");
drive = hslider("drive", 0.75, 0, 1, 0.01);
exc   = no.noise * en.ar(0.001, 0.009, gate);          // pick
damp  = hslider("damp", 7000, 1500, 10000, 1);       // string brightness (was 7000)
sus   = hslider("sustain", 0.996, 0.98, 0.999, 0.0001); // ring (was 0.996)
dampc = damp * max(0.1, gate);                         // release chokes the string
str   = (+ : de.fdelay(4096, ma.SR / freq - 2)) ~ (fi.lowpass(1, dampc) : *(sus));
sat(x) = ma.tanh(x * (1.5 + drive * 11.0));
pres(x) = x + 3.0 * (x : fi.resonbp(2900, 1.6, 1.0));  // cab presence: the grit lives 2-4k
process = exc : str : sat : pres : fi.lowpass(2, 5500) : fi.highpass(1, 75) : *(gain * 0.28) : *(0.586) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
