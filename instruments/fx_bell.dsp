// parametric bell EQ (one peaking band, stereo-through) — wave 21
// THE MASKING COURT's EQ-LAST rung: bounded complementary cuts on the
// masker at the collision center (r-6: depth <= 6dB, static EQ is the
// weakest tool so it comes last). gain in dB (negative = cut), q = width.
import("stdfaust.lib");
freq = hslider("freq", 1000, 40, 16000, 1) : si.smoo;
gain = hslider("gain", 0, -12, 12, 0.1) : si.smoo;
q    = hslider("q", 2.0, 0.4, 8, 0.05);
bell = fi.peak_eq(gain, freq, freq/q);
process = bell, bell;
