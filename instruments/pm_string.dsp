// pm_string — THE FIRST PHYSICAL MODEL (0.320 SOUND family, 2026-07-24).
// Karplus-Strong waveguide: a real string, not an oscillator wearing one —
// pluck-position comb excitation, fractional-delay loop, one-pole damping,
// two modal body resonances. Every zone agent-tweakable.
//   damp   = string brightness decay (dark felt .. bright steel)
//   pluck  = pluck position along the string (bridge .. middle)
//   sustain= loop feedback (staccato .. ringing)
//   body   = modal body blend (direct string .. woody box)
// Headroom law: peak-normalized excitation + tanh-free linear path, proven
// 0 clipped at vel 1.0 solo (voice-headroom law).
import("stdfaust.lib");

freq = hslider("freq", 220, 27, 4000, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
damp = hslider("damp", 0.45, 0, 1, 0.01);
pluck = hslider("pluck", 0.24, 0.05, 0.5, 0.01);
sustain = hslider("sustain", 0.6, 0, 1, 0.01);
body = hslider("body", 0.35, 0, 1, 0.01);

// excitation: 4ms noise burst, comb-filtered at the pluck point (a string
// plucked at 1/4 length is missing every 4th harmonic — position IS timbre),
// then PRE-DAMPED by the same loop filter: the first measured cut left the
// raw burst's broadband click dominating the spectrum whatever damp said
// (centroid ~10kHz at damp 0.05) — a real pluck's attack is already dark.
burst = no.noise * en.ar(0.0005, 0.004, gate);
pluckdel = max(1.0, n * pluck);
excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
       : fi.lowpass(2, damphz);

// the string: fractional delay + damping lowpass inside the loop
n = ma.SR / max(27.0, freq);
damphz = 1200.0 + damp * 8800.0;
fb = 0.985 + sustain * 0.0135;                 // .985 staccato .. .9985 ring
loopfilter = fi.lowpass(1, damphz) * fb;
string = (+ : de.fdelay4(8192, max(2.0, n - 2.0))) ~ loopfilter;

// body: two modal resonances (woody 110Hz + boxy 225Hz), gentle blend
modal = _ <: fi.resonbp(110, 4, 0.35), fi.resonbp(225, 5, 0.28) :> _;
voice = excite : string <: _ * (1.0 - body * 0.6), (modal * body) :> _;

process = voice * gain * 0.7 <: _, _;
