// fx_crush — bitcrusher + sample-rate reducer: the internet-genre patina.
// sigilkore/digicore/dariacore texture (bitcrush ON THE BUS as the genre color),
// dungeon-synth/lofi tape rot alternative. bits 16 + srate 44100 = clean bypass.
// Research: docs/research_genre_expansion_w2.md. Stereo-through (FX law).
import("stdfaust.lib");
bits  = hslider("bits", 10, 2, 16, 0.1);        // amplitude quantize depth
srate = hslider("srate", 12000, 500, 44100, 1); // sample-hold rate Hz
mix   = hslider("mix", 1.0, 0, 1, 0.01);
levels = pow(2.0, bits - 1.0);
crush(x) = floor(x * levels + 0.5) / levels * 0.95;  // 0.95 = round-up headroom
lofi = ba.downSample(srate) : crush;
process = _,_ <: (par(i,2,lofi) : par(i,2,*(mix))), par(i,2,*(1-mix)) :> _,_;
