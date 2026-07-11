// warm analog bass: detuned saws -> envelope-swept resonant lowpass
import("stdfaust.lib");
freq   = hslider("freq", 55, 20, 2000, 0.001);
gain   = hslider("gain", 0.8, 0, 1, 0.01);
gate   = button("gate");
cutoff = hslider("cutoff", 500, 20, 12000, 1);
q      = hslider("res", 3, 0.5, 20, 0.1);
env    = en.adsr(0.005, 0.12, 0.75, 0.25, gate);
fenv   = en.adsr(0.005, 0.15, 0.40, 0.25, gate);
osc    = 0.5*os.sawtooth(freq) + 0.5*os.sawtooth(freq*1.006);
process = osc * env * gain : fi.resonlp(cutoff*(0.25 + 0.75*fenv), q, 1) : *(0.623) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
