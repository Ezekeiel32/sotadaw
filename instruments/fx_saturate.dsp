// warm saturation: drive into tanh with ANTIDERIVATIVE ANTI-ALIASING (ADAA).
// The naive 1x tanh aliased -11.7 dBc @ drive 9 (over the -60 E5 budget; G6). ADAA
// (Parker/Esqueda/Bilbao 2016) replaces the pointwise tanh with the slope of its
// antiderivative across each sample step — single-rate, no oversampling, SAME tanh
// character (drive/tone/mix unchanged; THD 2.92% vs 2.95%). Measured (dsp_bench):
// alias into budget through 11 kHz (-63 dBc, was -28.7); only near-Nyquist torture
// tones (12.5-15 kHz, not musical content) remain the single-rate physics limit.
//   F(x) = integral of tanh = log(cosh x)  [stable form: |x| + log(1+e^-2|x|) - log2]
//   y[n] = (F(x[n]) - F(x[n-1])) / (x[n]-x[n-1]), tanh(midpoint) when the step is tiny.
import("stdfaust.lib");
drv  = hslider("drive", 6, 0, 24, 0.1) : ba.db2linear : si.smoo;
tone = hslider("tone", 3500, 500, 10000, 1);
mix  = hslider("mix", 1.0, 0, 1, 0.01);

antideriv(x) = abs(x) + log(1.0 + exp(-2.0 * abs(x))) - log(2.0);

adaa(x) = out
with {
    x1  = x @ 1;                              // x[n-1] (mem via @1; primes break in with{})
    dx  = x - x1;
    reg = ma.tanh(0.5 * (x + x1));            // midpoint fallback near dx=0
    num = antideriv(x) - antideriv(x1);
    out = select2(abs(dx) < 1e-4, num / (dx + (dx == 0.0) * 1e-30), reg);
};

sat(x) = adaa(x * drv) : fi.lowpass(1, tone) : *(0.7);
process = _,_ <: (par(i,2,sat) : par(i,2,*(mix))), par(i,2,*(1-mix)) :> _,_;
