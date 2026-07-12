// shaker — caxixi/egg: bandpassed noise with the late "scoop" attack real
// shakers speak with (grains build, then choke). decay opens toward maraca.
import("stdfaust.lib");
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
decay = hslider("decay", 0.055, 0.01, 0.3, 0.001);
tone  = hslider("tone", 6500, 2000, 12000, 10);
env = en.ar(0.008, decay, gate);
process = no.noise : fi.resonbp(tone, 3.5, 1) : fi.highpass(2, 2500) : *(env*gain) : *(0.38) <: _,_;
