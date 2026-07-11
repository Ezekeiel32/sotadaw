// strings_stacc — spiccato string section: detuned saw ensemble with a FAST
// bow-attack envelope and no sustain. THE ostinato engine: 8th/16th cells under
// cine_brass swells and timpani hits (trailer_build), disco/funk stabs too.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
dec   = hslider("decay", 0.16, 0.05, 0.6, 0.001);    // stab length (was 0.16)
biteA = hslider("bite", 0.18, 0, 0.5, 0.01);         // bow noise (was 0.18)
env  = en.adsr(0.008, dec, 0.0, 0.09, gate);         // bow bite, no sustain
saws = os.sawtooth(freq * 0.997) + os.sawtooth(freq) + os.sawtooth(freq * 1.003)
     + os.sawtooth(freq * 2.0) * 0.25;
bite = no.noise * en.ar(0.002, 0.02, gate) * biteA : fi.resonbp(2800, 2.0, 1.0);
process = (saws / 3.25 + bite) * env * gain : fi.highpass(1, 140) : fi.lowpass(2, 7000) <: _,_;
