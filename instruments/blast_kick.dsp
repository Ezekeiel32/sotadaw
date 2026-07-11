// blast-beat double-KICK: tight + clicky, FAST decay so 200+bpm 16ths stay articulate.
//   Strong beater CLICK (noisy slap + a short bright tick), quick pitch drop, tight
//   (non-boomy) low end.
// Zones: freq (base pitch), gain, gate, click (beater slap level), decay (fast!), drive.
import("stdfaust.lib");
freq  = hslider("freq", 50, 20, 300, 0.001);
gain  = hslider("gain", 0.95, 0, 1, 0.01);
gate  = button("gate");
click = hslider("click", 1.0, 0, 1.5, 0.01);       // beater slap (articulation)
decay = hslider("decay", 0.09, 0.04, 0.3, 0.001);  // FAST amp decay (blast-tight)
drive = hslider("drive", 3, 1, 8, 0.1);

drop = 7;                                            // quick, strong pitch drop
penv = en.ar(0.0005, 0.018, gate);                  // fast pitch-drop envelope
aenv = en.ar(0.001, decay, gate);                   // tight body decay (no sub tail)
// beater slap: hi-passed noise burst + a short bright tick tone (both very fast)
cenv = en.ar(0.0002, 0.005, gate);
tick = (os.osc(3300) + os.osc(4700)*0.6);
clik = cenv * ((no.noise : fi.highpass(2, 1600)) + tick*0.5) * click;
body = os.osc(freq*(1 + drop*penv)) * aenv;
process = ((body + clik*0.7)*drive : ma.tanh) * (gain*0.62) <: _,_;
