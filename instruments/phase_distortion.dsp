// phase_distortion — the Casio CZ voice: a cosine read through a WARPED phase (not FM,
// not subtractive). `dcw` sets the body timbre (0.5=pure sine, lower=buzzy resonant
// saw/pulse); the attack starts bright and settles toward dcw (the DCW envelope).
// Glassy, vocal, digital — the phase-distortion timbre no other voice here has.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
dcw     = hslider("dcw", 0.32, 0.05, 0.5, 0.001);        // body distortion (0.5=sine)
brighttime = hslider("brighttime", 0.14, 0.005, 0.6, 0.001);  // attack-bright settle
att = hslider("attack", 0.005, 0.001, 0.5, 0.001);
rel = hslider("release", 0.25, 0.02, 2, 0.001);
p = os.lf_sawpos(freq);                                  // linear phase 0..1
sweepenv = en.ar(0.002, brighttime, gate);               // 1 -> 0
m  = max(0.04, min(0.96, dcw*(1 - sweepenv) + 0.10*sweepenv));  // bright attack -> dcw
y1 = 0.5 * p / m;
y2 = 0.5 + 0.5*(p - m)/(1 - m);
y  = select2(p < m, y2, y1);                             // warped phase
env = en.adsr(att, 0.3, 0.6, rel, gate);
process = cos(2*ma.PI*y) * env * gain <: _,_;
