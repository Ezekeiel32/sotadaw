// riser: bandpass-swept noise tension builder (the HTML prototype's riser(), voiced)
// zones: freq = sweep START Hz (note pitch), sweep = seconds to full rise (set = bars),
//        range = freq multiple at the top (20 => 300->6000), q = bp resonance.
// gain env rises with the sweep (late-bloom: env^2), tanh-capped.
import("stdfaust.lib");
freq  = hslider("freq", 300, 50, 2000, 0.1);
gain  = hslider("gain", 0.6, 0, 1, 0.01);
gate  = button("gate");
sweep = hslider("sweep", 8.0, 0.5, 20, 0.1);
range = hslider("range", 20, 2, 40, 0.1);
q     = hslider("q", 1.2, 0.5, 6, 0.01);
env = en.ar(sweep, 0.08, gate);
f = freq * pow(range, env) : min(16000);
process = no.noise : fi.resonbp(f, q, 1) : *(env*env*gain) : ma.tanh <: _,_;
