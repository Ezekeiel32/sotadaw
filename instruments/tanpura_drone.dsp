// tanpura_drone — sustained Indian tanpura drone (spiritual-jazz bed).
// A long-ringing Karplus-Strong string (sustain ~0.999) whose bright harmonics
// are fed through the JIVARI: a slowly-sweeping resonant band driven into a soft
// nonlinearity, blooming the shimmering, buzzing overtone "wave" a tanpura is
// famous for. The string rings for many seconds after the pluck = a true drone.
// zones: freq, gain, gate, buzz (jivari shimmer), sustain (ring length).
import("stdfaust.lib");
freq = hslider("freq", 110, 20, 4000, 0.001);
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
buzz = hslider("buzz", 0.5, 0, 1, 0.01);                  // jivari shimmer intensity
sus  = hslider("sustain", 0.999, 0.99, 0.9999, 0.0001);   // string ring length

// soft finger-pluck; highpass the burst so no DC/sub enters the sus~1 loop.
// gentle attack (blooms, doesn't spike) = the tanpura's slow swell.
exc  = no.noise * en.ar(0.004, 0.03, gate) : fi.highpass(1, 45);
damp = 7600;   // bright in-loop damping (tanpura shimmer keeps its highs)

// Karplus-Strong string: near-lossless feedback ring = the sustaining drone
str  = exc : (+ : de.fdelay4(4096, ma.SR/freq - 1)) ~ (fi.lowpass(1, damp) : *(sus));

// JIVARI: a slow "wave" sweeps two bright resonances across the string's
// harmonics, driven into tanh so overtones bloom & buzz (amplitude-dependent =
// it shimmers). Two bands (mid + upper) widen the shimmering overtone cascade.
wave = 1.0 + 0.35*buzz*os.osc(0.6);                       // the slow jivari wave
jivari(x) = ma.tanh( (lo + hi) * (3.0 + 10.0*buzz) ) * (0.62*buzz)
with {
    lo = x : fi.resonbp(freq*6.0*wave,   8, 1.0);
    hi = x : fi.resonbp(freq*15.0*wave, 11, 0.9);
};

// blend dry string + jivari buzz; x computed ONCE (function fan-out, not re-inst)
voice(x) = (x*0.78 + jivari(x)) * gain * 0.42;

// per-voice tanh safety so a 3-4 note chord still sits under 0 dBFS
process = str : voice : ma.tanh <: _,_;
