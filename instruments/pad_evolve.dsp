// pad_evolve — THE EVOLUTION PRIMITIVE (w62, r-17 item 213):
// two detuned saw layers (+-7 cents) under THREE free-running LFOs at
// INCOMMENSURATE slow rates (0.073 / 0.113 / 0.017 Hz — non-integer
// ratios never re-align) routed to cutoff + layer mix: motion that
// provably never repeats, no per-note automation authoring needed.
// Long A/R. Mono source by house convention (<: _,_) — width belongs
// to fx_widen on the lane. JIT voice; AOT-bake when hot.
import("stdfaust.lib");
freq   = hslider("freq", 220, 20, 2000, 0.001);
gain   = hslider("gain", 0.5, 0, 1, 0.01);
gate   = button("gate");
att    = hslider("attack", 1.2, 0.05, 4.0, 0.01);
rel    = hslider("release", 1.6, 0.1, 6.0, 0.01);
depth  = hslider("evolve_depth", 0.5, 0.0, 1.0, 0.01);

l1 = os.osc(0.073);            // incommensurate trio — free-running,
l2 = os.osc(0.113);            // retrigger OFF by construction
l3 = os.osc(0.017);

det = pow(2.0, 7.0/1200.0);    // +-7 cent layer detune (chorusing)
layerA = os.sawtooth(freq/det);
layerB = os.sawtooth(freq*det);
mixw = 0.5 + 0.5*depth*l2;     // layer blend breathes
osc2 = layerA*(1.0-mixw) + layerB*mixw;

cut = 900.0 + (2600.0 + 1400.0*l3) * (0.5 + 0.5*l1) * (0.35 + 0.65*depth);
env = en.adsr(att, 0.6, 0.8, rel, gate);
// headroom law: single saw pair through a LP — 0.42 keeps vel-1.0 clean
process = osc2 : fi.lowpass(2, cut) : *(env*gain*0.42) <: _,_;
