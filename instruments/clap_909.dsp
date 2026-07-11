// designed clap: 3 pre-bursts + main burst through bandpass, soft clip glue
// zones (inits = the original constants): decay = main-burst decay s, tone = bp centre,
//   spread = pre-burst timing scale (roll tightness)
import("stdfaust.lib");
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
decay  = hslider("decay", 0.24, 0.08, 0.8, 0.01);
tone   = hslider("tone", 1400, 600, 4000, 10);
spread = hslider("spread", 1, 0.3, 2.5, 0.01);
gd(d) = gate : @(int(d*ma.SR));
burst(d, a) = en.ar(0.001, 0.03, gd(d)) * no.noise * a;
main = en.ar(0.001, decay, gd(0.028*spread)) * no.noise;
mixed = burst(0.0, 0.5) + burst(0.010*spread, 0.55) + burst(0.019*spread, 0.6) + main*0.9;
process = mixed : fi.resonbp(tone, 1.2, 1) : fi.highpass(2, 500) : *(gain*1.6) : ma.tanh <: _,_;
