// supersaw_jp — THE EXACT SZABO MODEL (w55, r-17 item 020; Szabo 2010
// JP-8000 measurements, banked as PatchArchetype 'supersaw'):
//   7 saws at f0*(1+offset_i*curve(detune)) with the MEASURED unequal
//   offsets; detune knob 0-1 through the 11th-order polynomial;
//   center/side mix gains on their measured curves; HPF TRACKING f0
//   (kills sub-fundamental alias — the JP's own trick).
// Phase note: hardware runs free randomized phase per trigger; stock
// phasors start at 0 — detuned saws decorrelate within milliseconds,
// the audible difference is the first ~2ms only.
// JIT voice (unregistered) — renders instantly; AOT-bake when hot.
import("stdfaust.lib");
freq   = hslider("freq", 220, 20, 4000, 0.001);
gain   = hslider("gain", 0.5, 0, 1, 0.01);
gate   = button("gate");
detune = hslider("detune", 0.4, 0, 1, 0.001);
mixk   = hslider("mix", 0.8, 0, 1, 0.001);
att    = hslider("attack", 0.004, 0.001, 1.0, 0.001);
rel    = hslider("release", 0.15, 0.02, 2.0, 0.001);

// Szabo detune curve: knob x -> spread (Horner form, coefficients verbatim)
curve(x) = ((((((((((10028.7312891634*x - 50818.8652045924)*x
  + 111363.4808729368)*x - 138150.6761080548)*x + 106649.6679158292)*x
  - 53046.9642751875)*x + 17019.9518580080)*x - 3425.0836591318)*x
  + 404.2703938388)*x - 24.1878824391)*x + 0.6717417634)*x
  + 0.0030115596;

cgain = -0.55366*mixk + 0.99785;                    // center (measured)
sgain = -0.73764*mixk*mixk + 1.2841*mixk + 0.044372; // each side (measured)
sprd = curve(detune);
saw(o) = os.sawtooth(freq*(1.0 + o*sprd));
stack = saw(0.0)*cgain
      + (saw(-0.11002313) + saw(-0.06288439) + saw(-0.01952356)
       + saw(0.01991221) + saw(0.06216538) + saw(0.10745242))*sgain;
env = en.adsr(att, 0.12, 0.85, rel, gate);
// headroom law: worst-case coherent sum ~4.0 -> 0.10 keeps vel-1.0 solo clean
process = stack : fi.highpass(2, freq) : *(env*gain*0.10) <: _,_;
