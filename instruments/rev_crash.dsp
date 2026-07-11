// reverse cymbal: a noise swell RISING into the downbeat (the anti-crash) —
// the record language for "the second drop arrives differently". swell =
// rise seconds (emission sets it from bpm so the peak lands AT the bar),
// bright = highpass floor. env^2 = exponential-feel rise; snap release so
// the downbeat owns the impact. freq is unused but the zone law requires it.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 2000, 0.01);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
swell = hslider("swell", 1.5, 0.1, 6, 0.01);
bright = hslider("bright", 3500, 500, 12000, 1);
env = en.ar(swell, 0.05, gate);
sig = no.noise : fi.highpass(2, bright) : fi.lowpass(1, 14000);
process = sig * env * env * gain * 0.7 <: _,_;
