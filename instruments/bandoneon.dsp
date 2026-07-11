// bandoneon — the tango free-reed: 3 slightly-detuned reed banks (the "musette"
// shimmer) + a bellows TREMOLO (slow amplitude breathing) + an attack air chiff.
// Warmer and more expressive than the shallow accordion — nuevo tango / folk / chanson.
import("stdfaust.lib");
freq = hslider("freq", 262, 55, 2000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
musette   = hslider("musette", 0.007, 0, 0.02, 0.0001);  // reed-bank detune
bellows   = hslider("bellows", 0.08, 0, 0.3, 0.01);      // bellows tremolo depth
bellowsrate = hslider("bellowsrate", 4.5, 0, 8, 0.01);
reed      = hslider("reed", 0.6, 0, 1, 0.01);            // warm <-> bright reed
chiff     = hslider("chiff", 0.25, 0, 1, 0.01);          // attack air chiff
att = hslider("attack", 0.03, 0.003, 0.4, 0.001);
rel = hslider("release", 0.18, 0.02, 1.2, 0.001);
bank(d) = os.sawtooth(freq*(1+d))*0.6 + os.square(freq*(1+d))*0.4;
reeds   = (bank(-musette) + bank(0) + bank(musette)) / 3;
trem    = 1 + bellows*os.osc(bellowsrate);
env     = en.adsr(att, 0.12, 0.9, rel, gate) * trem;
tone    = reeds : fi.lowpass(2, 1500 + reed*5000);
chiffn  = no.noise*chiff*0.3 : fi.highpass(2, 2000);
process = (tone + chiffn*en.ar(0.002, 0.05, gate)) * env * gain * 0.45 <: _,_;
