// fx_chorus — the palette had flanger but NO CHORUS (bachata/requinto guitar,
// dreampop washes, 80s keys, jazz EP shimmer — bread-and-butter modulation).
// Three modulated taps per side around 18ms (out of flanger comb territory),
// LFO phases spread across taps AND sides, equal-power mix. voices zone thins
// to a lighter double when 3 taps is too thick.
import("stdfaust.lib");
rate = hslider("rate", 0.8, 0.05, 4.0, 0.001);      // Hz
depth = hslider("depth", 0.5, 0.0, 1.0, 0.01);
mix = hslider("mix", 0.4, 0.0, 1.0, 0.01);
voices = hslider("voices", 3, 1, 3, 1);             // taps per side
base = 0.018 * ma.SR;                                // 18ms center
sweep = 0.007 * ma.SR;                               // +/-7ms max
tap(ph) = de.fdelay4(4096, base + sweep * depth * os.oscp(rate, ph));
one(side) = _ <: tap(side + 0.0), tap(side + 2.1), tap(side + 4.2)
          : _, *(voices >= 2), *(voices >= 3) :> _ / max(1.0, voices);
wetgain = mix : min(1.0) : sqrt;
drygain = (1.0 - mix) : max(0.0) : sqrt;
process(l, r) = l * drygain + one(0.0, l) * wetgain,
                r * drygain + one(3.14, r) * wetgain;
