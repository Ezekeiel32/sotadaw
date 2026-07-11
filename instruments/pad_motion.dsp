// evolving pad: detuned saw stack, slow filter sweep + auto-pan motion
// zones (inits = the original constants): detune = stack spread, motion = sweep
// rate Hz, depth = sweep range Hz, drift = auto-pan rate Hz.
import("stdfaust.lib");
freq = hslider("freq", 110, 30, 1500, 0.01);
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
d      = hslider("detune", 0.007, 0, 0.03, 0.0005);
motion = hslider("motion", 0.11, 0.02, 1, 0.005);
depth  = hslider("depth", 1800, 0, 4000, 10);
drift  = hslider("drift", 0.07, 0.0, 0.5, 0.005);
stack = os.sawtooth(freq) + os.sawtooth(freq*(1+d)) + os.sawtooth(freq*(1-d)) + os.sawtooth(freq*2*(1+d/2));
env = en.adsr(0.6, 1.0, 0.8, 1.2, gate);
sweep = 400 + depth*(0.5 + 0.5*os.osc(motion));
sig = stack/4 : fi.lowpass(3, sweep) : *(env*gain);
pan = 0.5 + 0.35*os.osc(drift);
process = sig <: *(sqrt(1-pan)), *(sqrt(pan));
