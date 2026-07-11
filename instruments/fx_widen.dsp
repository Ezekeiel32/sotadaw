// stereo widener: short modulated haas + mid/side width
import("stdfaust.lib");
width = hslider("width", 1.4, 0, 2, 0.01) : si.smoo;
rate  = hslider("rate", 0.4, 0.05, 3, 0.01);
dl = de.fdelay(4096, 8*ma.SR/1000.0 * (1 + 0.15*os.osc(rate)));
mid(l,r) = (l+r)/2;
side(l,r) = (l-r)/2;
process(l,r) = m + s*width, m - s*width
with { l2 = l; r2 = r : dl; m = mid(l2,r2); s = side(l2,r2); };
