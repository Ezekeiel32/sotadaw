// dark keys: 2-osc detuned triangle + sub octave, slow filter env, vibrato tail
// zones (inits = the original constants): cutoff = filter base Hz, sweep = filter-env
// range Hz, sub = octave-down level, detune = osc2 offset, vibrato = tail depth.
import("stdfaust.lib");
freq = hslider("freq", 220, 30, 2500, 0.01);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
cut  = hslider("cutoff", 700, 200, 3000, 1);
swp  = hslider("sweep", 2600, 0, 6000, 10);
subL = hslider("sub", 0.5, 0, 1, 0.01);
det  = hslider("detune", 0.004, 0, 0.02, 0.0005);
vibd = hslider("vibrato", 0.004, 0, 0.02, 0.0005);
vib = 1 + vibd*os.osc(5)*en.asr(0.6, 1, 0.3, gate);
o = os.triangle(freq*vib) + os.triangle(freq*(1+det)*vib) + subL*os.osc(freq/2);
env = en.adsr(0.006, 0.5, 0.55, 0.35, gate);
fenv = en.adsr(0.01, 0.7, 0.3, 0.4, gate);
process = o/2.5 : fi.lowpass(2, cut + swp*fenv) : *(env*gain) <: _,_;
