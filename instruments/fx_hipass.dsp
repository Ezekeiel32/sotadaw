// fx_hipass — stereo resonant highpass, the mud-cleanup twin of fx_filter.
// Born 2026-07-12: the corpus court found 29 songs writing fx_filter
// {"mode":"hp"} — a zone that does not exist; the intent (clean the lows off
// a pad/lead/verb) had NO home in the rack. Stereo-through FX contract:
// 2 in -> 2 out. cutoff in Hz (default 20 = transparent), res = resonance Q.
import("stdfaust.lib");
cutoff = hslider("cutoff", 20, 20, 8000, 1) : si.smoo;
res    = hslider("res", 0.9, 0.5, 8, 0.01) : si.smoo;
flt    = fi.resonhp(cutoff, res, 1.0);
process = flt, flt;
