// trap 808: sine sub with fast downward pitch glide + long amp decay + soft saturation
// zones (inits = the original constants): glide = pitch-drop depth, decay = amp decay s,
//   drive = pre-tanh scale (fatness)
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 400, 0.001);
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
glide = hslider("glide", 3, 0, 8, 0.1);
decay = hslider("decay", 0.9, 0.2, 3, 0.01);
drive = hslider("drive", 1.4, 0.5, 5, 0.01);
pitchenv = en.ar(0.001, 0.07, gate);              // 0->1->0 fast: the "boom" drop
ampenv   = en.adsr(0.001, decay, 0.0, 0.15, gate);  // long tail, no sustain
sub = os.osc(freq * (1 + glide*pitchenv));
process = (sub * drive : ma.tanh) * ampenv * gain <: _,_;
