// fx_ms_eq: mid-side mastering EQ — shape the CENTER (mono sum) and the SIDES
// (stereo difference) independently. The classic pro moves this unlocks: CUT side-lows
// to mono the bass (tight, translatable low end), BOOST side-highs for AIR & width
// without harshening the center, lift mid-highs for lead/vocal presence. Before this
// only fx_widen touched M/S — and only to widen. M=(L+R)/2, S=(L-R)/2; decode L=M+S,
// R=M-S. 2nd-order shelves (smooth, mastering-grade). width = overall side gain (dB).
import("stdfaust.lib");

mlo = hslider("mid_low",   0, -12, 12, 0.1);            // low-shelf dB on MID
mhi = hslider("mid_high",  0, -12, 12, 0.1);            // high-shelf dB on MID
slo = hslider("side_low",  0, -12, 12, 0.1);            // low-shelf dB on SIDE (cut = mono lows)
shi = hslider("side_high", 0, -12, 12, 0.1);            // high-shelf dB on SIDE (boost = air)
wid = hslider("width", 0, -12, 12, 0.1) : ba.db2linear : si.smoo;   // overall side gain
flo = hslider("low_freq",  250, 80, 600, 1);
fhi = hslider("high_freq", 8000, 2000, 14000, 1);

midEQ  = fi.lowshelf(2, mlo, flo) : fi.highshelf(2, mhi, fhi);
sideEQ = fi.lowshelf(2, slo, flo) : fi.highshelf(2, shi, fhi) : *(wid);

process(l, r) = m + s, m - s
with {
    m = (l + r) * 0.5 : midEQ;
    s = (l - r) * 0.5 : sideEQ;
};
