// conga — tuned hand drum: impulse-excited resonant modes (open tone) plus a
// highpassed slap layer. freq = the open-tone pitch (grid <lane>_pitch
// retunes quinto/conga/tumba); tone blends the slap in.
import("stdfaust.lib");
freq = hslider("freq", 190, 60, 600, 0.1);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
tone   = hslider("tone", 0.35, 0, 1, 0.01);
decay  = hslider("decay", 0.22, 0.05, 1.0, 0.001);
exc  = ba.impulsify(gate);
body = (exc : fi.resonbp(freq, 18, 1)) + 0.5 * (exc : fi.resonbp(freq * 1.52, 22, 1))
       + 0.25 * (exc : fi.resonbp(freq * 2.1, 25, 1));
slap = no.noise * en.ar(0.001, 0.03, gate) : fi.highpass(2, 1200) : *(tone);
process = (body * 3.2 + slap) * en.ar(0.0015, decay, gate) * gain : *(1.1) <: _,_;
