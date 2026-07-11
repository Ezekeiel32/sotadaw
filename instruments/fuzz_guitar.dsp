// fuzz_guitar — Big-Muff-style STACKED-CLIPPING fuzz. A Karplus string driven
// through 4 cascaded soft-clip gain stages (the Muff cascade) with a mid-scoop
// "smile" tone stack, a sub-octave for girth, and a 4x12 cab lowpass. Long string
// feedback = the singing sustain of grunge / stoner / doom. Play power chords as
// NOTES. drive 0..1 = edge-of-breakup -> full fuzz; scoop = the Muff mid-scoop.
import("stdfaust.lib");
freq  = hslider("freq", 82, 20, 2000, 0.001);
gain  = hslider("gain", 0.62, 0, 1, 0.01);
gate  = button("gate");
drive = hslider("drive", 0.85, 0, 1, 0.01);
sus   = hslider("sustain", 0.9975, 0.99, 0.9995, 0.0001);  // string ring = fuzz sustain
scoop = hslider("scoop", 0.55, 0, 1, 0.01);                // mid-scoop depth (the Muff smile)
sub   = hslider("sub", 0.35, 0, 1, 0.01);                  // sub-octave girth
exc   = no.noise * en.ar(0.001, 0.012, gate);              // pick
damp  = 6500 * max(0.12, gate);                            // release chokes the ring
str   = exc : (+ : de.fdelay(4096, ma.SR/freq - 2)) ~ (fi.lowpass(1, damp) : *(sus));
g     = 2.0 + drive * 18.0;
stage(x) = ma.tanh(x * g) : fi.highpass(1, 60);            // clip + inter-stage DC block
fuzz  = str : stage : stage : stage : stage;               // 4 cascaded Muff stages
sublo = os.osc(freq * 0.5) * en.ar(0.002, 0.5, gate) * sub;
tone(x) = x - scoop * (x : fi.resonbp(650, 0.9, 1.0));     // scoop the low-mids (smile)
cab(x)  = x : fi.lowpass(3, 4800) : fi.highpass(2, 80);    // 4x12-ish
process = (fuzz + sublo) : tone : cab : *(gain * 0.22) <: _,_;
