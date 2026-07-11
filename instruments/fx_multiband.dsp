// fx_multiband: 3-band mastering compressor — THE multiband dynamics gap.
// No crossover existed anywhere in the repo before this; every other FX is full-band.
// Linkwitz-Riley LR4 crossovers (24 dB/oct = the mastering standard; two cascaded
// 2nd-order Butterworth = LR4, and LP(f)+HP(f) sum FLAT in magnitude at unity, so the
// three bands reconstruct the input when no band is reducing). Each band is compressed
// STEREO-LINKED (one detector drives L+R together = the image never wanders). Gentle
// ratios (1.3-2:1, high threshold) = mastering GLUE; steeper = corrective band control.
// Order: low = LP(xlow); mid = HP(xlow)->LP(xhigh); high = HP(xhigh). makeup post-sum.
// Zones freq/gain/gate are NOT here (this is an FX, stereo-through 2->2, not a voice).
import("stdfaust.lib");

xlo  = hslider("xlow",  150, 40, 500, 1);           // low|mid crossover (Hz)
xhi  = hslider("xhigh", 2500, 800, 9000, 1);        // mid|high crossover (Hz)
att  = hslider("attack",  20, 1, 120, 1) * 0.001;   // ms -> s (shared)
rel  = hslider("release", 150, 20, 800, 1) * 0.001; // ms -> s (shared)
lo_t = hslider("low_thresh",  -18, -48, 0, 0.5);
lo_r = hslider("low_ratio",     2, 1, 8, 0.1);
md_t = hslider("mid_thresh",  -18, -48, 0, 0.5);
md_r = hslider("mid_ratio",     2, 1, 8, 0.1);
hi_t = hslider("high_thresh", -18, -48, 0, 0.5);
hi_r = hslider("high_ratio",    2, 1, 8, 0.1);
mkup = hslider("makeup", 0, -12, 12, 0.1) : ba.db2linear : si.smoo;

// LR4 = two cascaded 2nd-order Butterworth at the same cutoff.
lp4(fc) = fi.lowpass(2, fc)  : fi.lowpass(2, fc);
hp4(fc) = fi.highpass(2, fc) : fi.highpass(2, fc);

// each band: split the stereo pair, then stereo-linked compress (2->2).
bandLo  = par(i, 2, lp4(xlo))            : co.compressor_stereo(lo_r, lo_t, att, rel);
bandMid = par(i, 2, hp4(xlo) : lp4(xhi)) : co.compressor_stereo(md_r, md_t, att, rel);
bandHi  = par(i, 2, hp4(xhi))            : co.compressor_stereo(hi_r, hi_t, att, rel);

// fan stereo to the 3 bands, sum, apply makeup.
process = (_,_ <: bandLo, bandMid, bandHi :> _,_) : par(i, 2, *(mkup));
