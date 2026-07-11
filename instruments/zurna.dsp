// zurna / shehnai — conical double-reed shawm: PIERCING, buzzy, nasal, loud and
// sustained (circular breathing). Rich odd+even harmonics driven through a nasal
// formant. The Balkan wedding / Anatolian / Indian-oboe lead that cuts through anything.
import("stdfaust.lib");
freq = hslider("freq", 440, 120, 2500, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
nasal   = hslider("nasal", 1600, 800, 3500, 1);       // nasal formant center
bright  = hslider("bright", 7000, 2000, 12000, 1);
buzz    = hslider("buzz", 1.6, 1, 4, 0.01);           // reed drive (piercing)
vibrato = hslider("vibrato", 0.006, 0, 0.025, 0.0001);
vibrate = hslider("vibrate", 5.5, 0, 8, 0.01);
att = hslider("attack", 0.02, 0.002, 0.3, 0.001);
rel = hslider("release", 0.12, 0.02, 1, 0.001);
vib    = 1 + vibrato*os.osc(vibrate);
reed   = os.sawtooth(freq*vib);
driven = reed*buzz : ma.tanh;                         // buzzy reed
body   = (driven : fi.resonbp(nasal, 2.2, 1))*0.7 + driven*0.4;
process = (body : fi.lowpass(2, bright)) * en.adsr(att, 0.1, 0.9, rel, gate) * gain * 0.45 <: _,_;
