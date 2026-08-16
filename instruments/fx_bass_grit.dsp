// fx_bass_grit — THE MULTIBAND BASS TRANSLATION HEAL (w69, r-5 item 188):
// split at ~120Hz. The SUB passes CLEAN (the fundamental for big systems,
// mono-summable by construction). The upper path is HP'd again at 220Hz
// and driven through the house ADAA tanh (same math as fx_saturate) to
// synthesize the missing-fundamental harmonics — the 850-1200Hz grit
// that survives phones and laptops. The grit is a PARALLEL layer: the
// original band balance stays; grit adds only what small speakers need.
import("stdfaust.lib");
xover = hslider("xover", 120, 60, 200, 1);
drv   = hslider("drive", 9, 0, 24, 0.1) : ba.db2linear : si.smoo;
grit  = hslider("grit", 0.5, 0, 1, 0.01);

antideriv(x) = abs(x) + log(1.0 + exp(-2.0 * abs(x))) - log(2.0);
adaa(x) = out
with {
    x1  = x @ 1;
    dx  = x - x1;
    reg = ma.tanh(0.5 * (x + x1));
    num = antideriv(x) - antideriv(x1);
    out = select2(abs(dx) < 1e-4, num / (dx + (dx == 0.0) * 1e-30), reg);
};

// MaxxBass order: saturate the FULL signal (the 49Hz fundamental IS
// the harmonic source), THEN high-pass the born harmonics at 220 —
// HP-before-tanh starves the shaper on pure subs (engine-measured
// +5.5dB vs +20dB this way round).
gritpath(x) = adaa(x * drv) : fi.highpass(3, 220)
              : fi.peak_eq(4.0, 1000, 800) : fi.lowpass(1, 6500) : *(0.5);

chan(x) = x <: fi.lowpass(3, xover), fi.highpass(3, xover),
              (gritpath : *(grit)) :> _;
process = _,_ : par(i, 2, chan) : _,_;
