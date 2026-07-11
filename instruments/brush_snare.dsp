// BRUSHED snare (not a crack): a soft filtered-noise SWISH (2-5kHz, soft attack,
//   medium decay = the brush sweeping the head) + a faint SOFT low body. No transient.
// Zones: freq (body pitch), gain, gate, swish (swish level), body (body level),
//   decay (overall length scale).
import("stdfaust.lib");
freq  = hslider("freq", 200, 20, 2000, 0.001);
gain  = hslider("gain", 0.8, 0, 1, 0.01);
gate  = button("gate");
swish = hslider("swish", 0.9, 0, 1.5, 0.01);     // brush swish level
body  = hslider("body", 0.3, 0, 1.5, 0.01);      // faint body level (soft)
decay = hslider("decay", 1.0, 0.3, 3.0, 0.01);   // length scale

// the SWISH: bandpassed noise ~2-5kHz, SOFT attack (~9ms, no crack), medium decay
senv = en.ar(0.009, 0.24*decay, gate);
sw = no.noise : fi.highpass(2, 2000) : fi.lowpass(2, 5000) : *(senv*swish);

// faint SOFT body: quiet low triangle, soft attack (no click), short decay
benv = en.ar(0.005, 0.10*decay, gate);
bd = (os.triangle(freq) + os.triangle(freq*1.48)*0.5) : *(benv*body);

process = (sw + bd*0.45) : *(gain*0.6) <: _,_;
