// trap snare: tonal body (detuned triangles) + band-limited noise, fast decay
// zones (inits = the original constants): body = tonal level, snap = noise level,
//   tone = body pitch scale, decay = both-env scale
import("stdfaust.lib");
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
bodyl = hslider("body", 0.5, 0, 1.5, 0.01);
snap  = hslider("snap", 0.8, 0, 1.5, 0.01);
tone  = hslider("tone", 1, 0.5, 2, 0.01);
decay = hslider("decay", 1, 0.3, 3, 0.01);
tenv = en.ar(0.001, 0.12*decay, gate);
nenv = en.ar(0.001, 0.16*decay, gate);
body  = (os.triangle(180*tone) + os.triangle(330*tone)) * 0.5 * tenv;
noise = (no.noise : fi.highpass(2, 1500) : fi.lowpass(2, 7000)) * nenv;
process = (body*bodyl + noise*snap) * gain <: _,_;
