// kick_psy — tight psy/techno kick: fast pitch-drop body + click transient, tanh glue.
// Zones: punch (pitch-envelope depth), decay (body length).
import("stdfaust.lib");
freq  = hslider("freq", 50, 25, 120, 0.1);
gain  = hslider("gain", 0.9, 0, 1, 0.01);
gate  = button("gate");
punch = hslider("punch", 12, 2, 24, 0.1);
decay = hslider("decay", 0.26, 0.08, 0.8, 0.01);

penv  = en.ar(0.0008, 0.045, gate);
aenv  = en.ar(0.0008, decay, gate);
body  = os.osc(freq * (1.0 + punch * penv * penv)) * aenv;
click = no.noise : fi.highpass(2, 2800) : *(en.ar(0.0004, 0.007, gate)) : *(0.55);
process = (body * 1.15 + click) * gain : ma.tanh <: _,_;
