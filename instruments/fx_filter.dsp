// fx_filter — stereo resonant lowpass, THE automatable filter (cutoff/res zones).
// Stereo-through FX contract: 2 in -> 2 out. cutoff in Hz, res = resonance Q.
import("stdfaust.lib");
cutoff = hslider("cutoff", 18000, 60, 18000, 1) : si.smoo;
res    = hslider("res", 0.9, 0.5, 8, 0.01) : si.smoo;
flt    = fi.resonlp(cutoff, res, 1.0);
process = flt, flt;
