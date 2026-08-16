// THE DUB DELAY (wave 47, r-25): tempo-synced delay with a LOW-PASS
// INSIDE the feedback loop — every repeat gets darker (the shared FX
// DNA of goa, psytrance and dub techno). time in ms (0.75*60000/bpm =
// the dotted-8th law); damp = the loop filter cutoff.
import("stdfaust.lib");
dtime = hslider("time", 375, 20, 1500, 1);
fb    = hslider("feedback", 0.55, 0, 0.85, 0.01);
damp  = hslider("damp", 2200, 400, 8000, 1);
mix   = hslider("mix", 1.0, 0, 1, 0.01) : si.smoo;
loop = de.fdelay(65536, dtime * ma.SR / 1000.0) : fi.lowpass(2, damp) : *(fb);
wet = + ~ loop;
process = _,_ : par(i, 2, _ <: *(1.0 - mix), (wet : *(mix)) :> _);
