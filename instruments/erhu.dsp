// erhu — Chinese bowed 2-string fiddle (no fingerboard): a bowed saw shaped by a
// nasal snakeskin-resonator FORMANT + bow noise, with a WIDE expressive vibrato that
// blooms in. The crying, singing "Chinese violin." Automate pitch for its glissando.
import("stdfaust.lib");
freq = hslider("freq", 293, 80, 2000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
bow     = hslider("bow", 0.35, 0, 1, 0.01);          // bow-noise amount
formant = hslider("formant", 1400, 600, 3000, 1);    // snakeskin resonator (nasal)
bright  = hslider("bright", 3500, 1000, 7000, 1);
vibrato = hslider("vibrato", 0.012, 0, 0.04, 0.0001); // wide, expressive
vibrate = hslider("vibrate", 5.5, 0, 8, 0.01);
att = hslider("attack", 0.06, 0.005, 0.5, 0.001);
rel = hslider("release", 0.2, 0.02, 1.5, 0.001);
vib    = 1 + vibrato*en.asr(0.3, 1, 0.1, gate)*os.osc(vibrate);  // vibrato blooms in
env    = en.adsr(att, 0.15, 0.9, rel, gate);
string = os.sawtooth(freq*vib);
bown   = no.noise*bow*0.3 : fi.bandpass(2, freq*0.5, freq*4);
raw    = (string + bown) : fi.lowpass(2, bright);
body   = (raw : fi.resonbp(formant, 1.8, 1))*0.5 + raw*0.6;
process = body * env * gain * 0.5 <: _,_;
