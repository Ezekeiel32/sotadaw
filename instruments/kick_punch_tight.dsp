// kick_punch_tight (W9) — the designed kick with the 120-500Hz box carved OUT:
// the parent's 45ms body sweep from ~5.5x freq parked half its energy in the
// lowmid (measured 2.4:1 low:lowmid solo; records run ~8.5:1). Here the pitch
// drop transits in 20ms from a lower start (4.2x) and the fundamental tail
// carries the weight the sweep gave up. Same zones, same click, same tanh glue.
// zones (inits = the designed constants):
//   punch = click level, drop = pitch-env depth, decay = body decay s,
//   tail = tail level, drive = pre-tanh scale
import("stdfaust.lib");
freq = hslider("freq", 52, 25, 200, 0.1);
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
punch = hslider("punch", 0.6, 0, 1.5, 0.01);
drop  = hslider("drop", 2.8, 0, 8, 0.1);
decay = hslider("decay", 0.30, 0.05, 1.2, 0.01);
tail  = hslider("tail", 0.7, 0, 1, 0.01);
drive = hslider("drive", 1, 0.2, 4, 0.01);
click = en.ar(0.0004, 0.008, gate) * (no.noise : fi.highpass(2, 2500)) * punch;
penv  = en.ar(0.001, 0.016, gate);
body  = os.osc(freq * (1 + drop*penv)) * en.adsr(0.001, decay, 0.0, 0.06, gate);
tailo = os.osc(freq) * en.adsr(0.005, 0.55, 0.0, 0.1, gate) * tail;
process = ((click + body*1.6 + tailo) * drive : ma.tanh) * gain <: _,_;
