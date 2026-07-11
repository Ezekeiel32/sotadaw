// stereo room/hall reverb (zita-light) as an insert: mix controls wet/dry
import("stdfaust.lib");
mix   = hslider("mix", 0.25, 0, 1, 0.01) : si.smoo;
size  = hslider("size", 2.5, 0.5, 8, 0.1);      // t60 low band seconds
damp  = hslider("damp", 5000, 1000, 12000, 1);   // hf rolloff
wet   = re.zita_rev1_stereo(20, 200, damp, size, size*0.6, 44100);
process = _,_ <: (_,_ : wet : par(i,2,*(mix))), par(i,2,*(1-mix)) :> _,_;
