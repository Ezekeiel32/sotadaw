// acid303_slide — THE SLIDING 303 (w84, r-25 item 248): the acid303
// core (AOT, untouched — the nuke trap) twinned with the ONE missing
// 303 behavior: SLIDE. freq is slewed (slide ms) so overlapping/tied
// notes GLIDE through the engine's proven mono mechanism (w77:
// legato_ties / drill-808 overlap law). Everything else = the baked
// acid303 constants verbatim. JIT voice; AOT-bake when hot.
import("stdfaust.lib");
slide = hslider("slide", 60, 5, 300, 1);
freq  = hslider("freq", 55, 20, 2000, 0.001)
        : si.smooth(ba.tau2pole(slide * 0.001));
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
acc  = hslider("accent", 0.6, 0, 1, 0.01);
cutBase = hslider("cutoff", 300, 80, 2000, 1);
envAmt  = hslider("envmod", 3500, 0, 8000, 1);
res     = hslider("res", 8, 1, 16, 0.1);
fdec    = hslider("decay", 0.18, 0.05, 0.6, 0.001);
fenv = en.adsr(0.005, fdec, 0.10, 0.10, gate);
aenv = en.adsr(0.005, 0.30, 0.60, 0.15, gate);
cutoff = (cutBase + envAmt*fenv*(0.5+acc)) : min(12000);
process = os.sawtooth(freq) : fi.resonlp(cutoff, res+8*acc, 1)
          : *(aenv*gain) : ma.tanh : *(0.8) <: _,_;
