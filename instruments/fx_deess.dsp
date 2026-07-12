// fx_deess — split-band de-esser (ledger dr19: the product's own vocal-chain
// doc mandates a de-esser FIRST; no such voice existed). The band above the
// crossover compresses on its own energy (sibilance ducks itself); the low
// band passes untouched. Compression-only = output <= input, headroom-safe
// by construction. Stereo-through per the FX law.
import("stdfaust.lib");
freq   = hslider("freq", 5500, 3000, 9000, 10);     // crossover
thresh = hslider("thresh", -32, -60, 0, 0.5);
ratio  = hslider("ratio", 4, 1, 12, 0.1);
deess(x) = lo + hic with {  // 'de' clashes stdfaust's delay lib (redefinition — broke gen_faust AOT)
  lo  = x : fi.lowpass(3, freq);
  hi  = x : fi.highpass(3, freq);
  hic = hi : co.compressor_mono(ratio, thresh, 0.002, 0.05);
};
process = deess, deess;
