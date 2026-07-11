// bagpipes — Highland pipes: a reedy CHANTER on the played note over a constant
// DRONE (fixed tonic + octave) that sounds the whole time a note is held. Set `drone`
// to the tune's tonic (Hz). Play the chanter gapless/legato with grace-note cuts.
import("stdfaust.lib");
freq = hslider("freq", 466, 120, 2000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
drone     = hslider("drone", 116.5, 55, 240, 0.1);    // fixed drone pitch (A2-ish tonic)
dronelevel= hslider("dronelevel", 0.5, 0, 1, 0.01);
reed      = hslider("reed", 1.4, 1, 3, 0.01);         // chanter reed drive
bright    = hslider("bright", 6000, 2000, 10000, 1);
att = hslider("attack", 0.02, 0.002, 0.2, 0.001);
rel = hslider("release", 0.1, 0.02, 0.6, 0.001);
env  = en.adsr(att, 0.08, 0.95, rel, gate);
craw = os.sawtooth(freq)*reed : ma.tanh;
chanter = (craw : fi.resonbp(1400, 2, 1))*0.6 + craw*0.4;
drn  = (os.sawtooth(drone) + os.sawtooth(drone*2)*0.6 + os.sawtooth(drone*0.5)*0.5) * dronelevel * 0.3;
mix  = (chanter*0.7 + drn) : fi.lowpass(2, bright);
process = mix * env * gain * 0.4 <: _,_;
