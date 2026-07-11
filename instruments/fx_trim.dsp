// fx_trim: static stereo gain in dB - the master headroom tool.
// The built-in limiter clamps at 0 dBFS (ceiling param non-functional);
// a post-limiter trim IS the working ceiling.
import("stdfaust.lib");
lvl = hslider("level", 0.0, -24.0, 24.0, 0.1) : ba.db2linear : si.smoo;
process = _ * lvl, _ * lvl;
