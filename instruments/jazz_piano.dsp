// jazz_piano — felt/acoustic grand piano: ADDITIVE struck-string synthesis (NOT FM,
// which reads as electric Rhodes). A bank of 9 INHARMONIC partials at ratios
// n*sqrt(1 + B*n^2) (real piano string stiffness) where the upper partials both sit
// LOWER and DECAY FASTER — the bright hammer strike blooms, then mellows into a warm
// mid-forward body: the signature of a real acoustic grand. A soft LOWPASSED felt
// hammer seeds the onset; a light Karplus string adds sustain/weight. Every note
// decays to silence (per-partial sustain=0) — natural bloom-then-decay, never a drone.
// Zones: freq, gain, gate, decay, brightness, felt.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
decay      = hslider("decay", 2.0, 0.4, 4.0, 0.01);   // fundamental ring (s)
brightness = hslider("brightness", 0.5, 0, 1, 0.01);  // upper-partial tilt (dark->glassy)
felt       = hslider("felt", 0.4, 0, 1, 0.01);        // soft hammer thump level

N = 9;
B = 0.0004;                                // string inharmonicity coefficient
tilt = 1.6 - 1.15*brightness;              // partial-amp rolloff exponent (bright=shallow)
att  = 0.004;                              // soft felt attack (s), NOT a hard click
rel  = 0.18;                               // damper release when key lifts (s)

// one inharmonic partial (n = harmonic number 1..N): amp rolls off ~1/n^tilt,
// higher partials decay faster (pdec shrinks with n) -> mellows over time
ratio(n) = n * sqrt(1.0 + B*n*n);
amp(n)   = pow(n, 0.0 - tilt);
pdec(n)  = decay / (1.0 + 0.6*(n - 1.0));
partial(n) = os.osc(freq*ratio(n)) * amp(n) * en.adsr(att, pdec(n), 0.0, rel, gate);
stack = sum(i, N, partial(i + 1.0));

// soft felt hammer: short lowpassed noise thump at onset (adds strike definition)
thump = no.noise * en.ar(0.001, 0.02, gate) * felt : fi.lowpass(2, 1800 + freq*2.5);

// light Karplus string body for sustain/weight (decays with the master `decay`)
exc  = no.noise * en.ar(0.001, 0.006, gate);
kstr = exc : (+ : de.fdelay4(4096, ma.SR/freq - 1)) ~ (fi.lowpass(1, 2600) : *(0.988));
body = kstr * en.adsr(att, decay, 0.0, rel, gate);

// sum, gain, warm lowpass, then ma.tanh safety limiter for polyphonic chord peaks
voice = stack*0.28 + body*0.20 + thump*0.45;
process = voice * gain : fi.lowpass(2, 6500) : ma.tanh <: _,_;
