// shakuhachi — Japanese bamboo flute: BREATH-forward, open-pipe tone with a noisy
// "muraiki" attack and the meri/kari head-tilt pitch `bend`. Meditative, expressive.
// More air and slower vibrato than pan_flute; automate `bend` for the microtonal drops.
import("stdfaust.lib");
freq = hslider("freq", 440, 80, 2500, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
breath  = hslider("breath", 0.45, 0, 0.8, 0.01);      // strong air (defining)
bend    = hslider("bend", 0, -0.06, 0.06, 0.001);     // meri/kari head-tilt
muraiki = hslider("muraiki", 0.5, 0, 1, 0.01);        // noisy attack burst
vibrato = hslider("vibrato", 0.01, 0, 0.03, 0.0001);
vibrate = hslider("vibrate", 4.5, 0, 7, 0.01);
att = hslider("attack", 0.05, 0.005, 0.4, 0.001);
rel = hslider("release", 0.25, 0.02, 1.5, 0.001);
vib  = (1 + vibrato*os.osc(vibrate)) * (1 + bend);
tone = os.osc(freq*vib) + os.osc(freq*vib*2)*0.2;      // open pipe: some even colour
env  = en.adsr(att, 0.15, 0.8, rel, gate);
air  = no.noise : fi.resonbp(freq*1.5, 2, 1) : fi.lowpass(2, 7500);
airenv = breath*env + muraiki*en.ar(0.003, 0.08, gate);
process = (tone*env*0.7 + air*airenv*0.6) * gain * 0.6 <: _,_;
