// cowbell — the 808 campana: two detuned squares (587/845 Hz, the classic
// ratio) through a mid bandpass. decay opens toward a ringing bell.
import("stdfaust.lib");
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
decay = hslider("decay", 0.11, 0.03, 0.5, 0.001);
tone  = hslider("tone", 1200, 500, 3000, 1);           // bandpass center: bell body (was 1200)
sq1 = (os.lf_sawpos(587) < 0.5) - 0.5;
sq2 = (os.lf_sawpos(845) < 0.5) - 0.5;
env = en.ar(0.001, decay, gate);
process = (sq1 + sq2) : fi.resonbp(tone, 3, 1) : *(env * gain) : *(0.5) <: _,_;
