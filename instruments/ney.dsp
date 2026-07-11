// ney — Middle-Eastern end-blown reed flute: BREATH-dominant, warm, with a slight
// grace-slide into each note and gentle vibrato. The airy, human, Sufi voice — the
// breath is a feature, not noise. Warmer & reedier than pan_flute/shakuhachi.
import("stdfaust.lib");
freq = hslider("freq", 392, 80, 2500, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
breath  = hslider("breath", 0.55, 0.1, 1, 0.01);      // ney is very breathy
warmth  = hslider("warmth", 5000, 1500, 9000, 1);
vibrato = hslider("vibrato", 0.009, 0, 0.03, 0.0001);
vibrate = hslider("vibrate", 5, 0, 8, 0.01);
grace   = hslider("grace", 0.02, 0, 0.1, 0.001);      // attack grace-slide down
att = hslider("attack", 0.06, 0.005, 0.4, 0.001);
rel = hslider("release", 0.2, 0.02, 1.2, 0.001);
vib  = (1 + vibrato*os.osc(vibrate)) * (1 - grace*en.ar(0.001, 0.05, gate));
tone = os.osc(freq*vib) + os.osc(freq*vib*2)*0.12 + os.osc(freq*vib*3)*0.06;
env  = en.adsr(att, 0.15, 0.82, rel, gate);
air  = no.noise : fi.resonbp(freq*1.2, 1.6, 1) : fi.lowpass(2, warmth);
airenv = breath*env + 0.5*breath*en.ar(0.004, 0.06, gate);
process = (tone*env*0.6 + air*airenv*0.7) * gain * 0.6 <: _,_;
