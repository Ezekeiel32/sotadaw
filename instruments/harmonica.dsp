// harmonica — diatonic free reed: a beating reed PAIR (slightly detuned = the tremolo
// shimmer) through a cupped-hand formant (the `cup` wah) with pushed-breath grit.
// `bend` drops pitch for blues draw-bends; automate it for expression.
import("stdfaust.lib");
freq = hslider("freq", 330, 40, 2000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
beat    = hslider("beat", 0.006, 0, 0.02, 0.0001);    // reed-pair detune (tremolo)
cup     = hslider("cup", 1200, 600, 3000, 1);         // cupped-hand wah formant
bright  = hslider("bright", 3000, 1000, 6000, 1);
grit    = hslider("grit", 1.4, 1, 5, 0.01);
bend    = hslider("bend", 0, -0.12, 0.02, 0.001);     // draw-bend (semitone-ish)
vibrato = hslider("vibrato", 0.004, 0, 0.02, 0.0001);
vibrate = hslider("vibrate", 5, 0, 8, 0.01);
att = hslider("attack", 0.02, 0.001, 0.4, 0.001);
rel = hslider("release", 0.12, 0.02, 1, 0.001);
vib   = (1 + vibrato*os.osc(vibrate)) * (1 + bend);
reeds = (os.sawtooth(freq*vib) + os.sawtooth(freq*vib*(1+beat))) * 0.5;
env   = en.adsr(att, 0.1, 0.9, rel, gate);
body  = (reeds : fi.resonbp(cup, 2, 1))*0.6 + reeds*0.5;
tone  = (body*grit : ma.tanh) : fi.lowpass(2, bright);
process = tone * env * gain * 0.5 <: _,_;
