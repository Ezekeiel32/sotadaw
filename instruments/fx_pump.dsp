// sidechain-style pump without routing: beat-rate ducking envelope.
// CLICKLESS: the raw saw-wrap made the gain STEP discontinuously each cycle
// (audible click on pads; broadband spray in the bench, -55.3 dBc). A 2 ms
// one-pole attack smooth on the envelope keeps the "instant duck" feel (real
// sidechain compressors attack in 1-5 ms) and removes the step spray: bench
// -64.0 dBc, IN the -60 E5 budget. The low-rate AM sidebands ARE the effect.
import("stdfaust.lib");
rate  = hslider("rate", 2.37, 0.5, 8, 0.01);      // duck events per second (set to bpm/60*beats)
depth = hslider("depth", 0.6, 0, 1, 0.01);
shape = hslider("release", 0.25, 0.05, 0.7, 0.01); // recovery time s
phasor = os.lf_saw(rate) : +(1) : /(2);            // 0..1 rising
env = 1 - depth * exp(0 - phasor/shape*3) : si.smooth(ba.tau2pole(0.002));
process = _,_ : par(i,2,*(env));
