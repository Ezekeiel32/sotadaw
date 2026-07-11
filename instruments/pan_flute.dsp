// pan_flute (zampoña) — stopped-pipe Andean flute: near-sine tone with odd-harmonic
// colour (stopped pipe), a strong breath CHIFF on attack, quick soft decay. `odd`
// = stopped(hollow) vs open colour; `breath` = the air bed under the note.
import("stdfaust.lib");
freq = hslider("freq", 523, 80, 3000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
breath  = hslider("breath", 0.3, 0, 0.6, 0.01);       // air bed level
odd     = hslider("odd", 0.7, 0, 1, 0.01);            // stopped(odd) <-> open(even)
chiff   = hslider("chiff", 0.4, 0, 1, 0.01);          // attack breath burst
vibrato = hslider("vibrato", 0.008, 0, 0.03, 0.0001);
vibrate = hslider("vibrate", 5, 0, 8, 0.01);
att = hslider("attack", 0.04, 0.005, 0.3, 0.001);
rel = hslider("release", 0.15, 0.02, 1, 0.001);
vib  = 1 + vibrato*os.osc(vibrate);
tone = os.osc(freq*vib) + os.osc(freq*vib*3)*0.15*odd + os.osc(freq*vib*2)*0.08*(1-odd);
env  = en.adsr(att, 0.1, 0.85, rel, gate);
air  = no.noise : fi.resonbp(freq, 3, 1) : fi.lowpass(2, 6500);
airenv = breath*env + chiff*en.ar(0.005, 0.05, gate);
process = (tone*env*0.7 + air*airenv*0.6) * gain * 0.6 <: _,_;
