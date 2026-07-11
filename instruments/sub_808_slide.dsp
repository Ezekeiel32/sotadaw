// melodic trap 808: the SLIDE bass. freq zone is smoothed (slide = ms tau) so
// any note-to-note change GLIDES — with overlapping notes the engine's mono
// tracking ignores the old note's off (gate never closes) = the FL-porta 808.
// boom = small attack pitch-drop (the KICK lane owns the big boom), decay =
// amp tail seconds, drive = tanh fatness. Structural 0.85 headroom (vel-1.0 law).
import("stdfaust.lib");
slide = hslider("slide", 80, 5, 400, 1);
freq = hslider("freq", 55, 20, 400, 0.001) : si.smooth(ba.tau2pole(slide * 0.001));
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
boom = hslider("boom", 0, 0, 8, 0.1);
decay = hslider("decay", 1.1, 0.2, 3, 0.01);
drive = hslider("drive", 1.5, 0.5, 5, 0.01);
pitchenv = en.ar(0.001, 0.05, gate);
ampenv = en.adsr(0.002, decay, 0.0, 0.18, gate);
sub = os.osc(freq * (1 + boom * pitchenv));
process = (sub * drive : ma.tanh) * ampenv * gain * 0.85 <: _,_;
