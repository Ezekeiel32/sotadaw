// synthetic pluck: tri+saw with squared fast decay through a pitch-tracking lowpass
// zones (inits = the original constants): decay = env s (squared = snappy),
// color = LP tracking multiple (1 dark .. 12 open).
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
dec   = hslider("decay", 0.5, 0.05, 2, 0.01);
color = hslider("color", 4, 1, 12, 0.1);
env  = en.ar(0.001, dec, gate);
tone = 0.6*os.triangle(freq) + 0.4*os.sawtooth(freq);
process = tone * env * env * gain : fi.lowpass(2, freq*color + 300) <: _,_;
