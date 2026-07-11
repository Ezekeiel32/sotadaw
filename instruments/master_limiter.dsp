// master bus glue + brickwall: drive into a stereo 1176-style limiter, hard ceiling after.
// FX (2-in 2-out) — hosted by FaustFxPlugin, typically last on the master chain.
import("stdfaust.lib");
drive   = hslider("drive", 0, -12, 12, 0.1) : ba.db2linear : si.smoo;
clg     = hslider("ceiling", -1.0, -12, 0, 0.1) : ba.db2linear;
lim     = co.limiter_1176_R4_stereo;
clampch = min(clg) : max(0 - clg);
process = par(i, 2, *(drive)) : lim : par(i, 2, clampch);
