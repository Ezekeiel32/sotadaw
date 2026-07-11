// sax_section — big-band reed section: bright saw through two formant peaks,
// breath-noise onset, jazz pitch scoop into the note, delayed vibrato.
// Unison lines = the soli; block chords = the shout chorus.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
att     = hslider("attack", 0.03, 0.005, 0.3, 0.001);  // tonguing (was 0.03)
vib     = hslider("vibrato", 0.018, 0, 0.05, 0.0001);  // depth (was 0.018)
breathA = hslider("breath", 0.05, 0, 0.2, 0.001);      // air (was 0.05)
env    = en.adsr(att, 0.12, 0.8, 0.12, gate);
scoop  = en.asr(0.06, 1.0, 0.06, gate);              // players slide up into it
vibdel = en.asr(0.28, 1.0, 0.1, gate);               // vibrato blooms late
f      = freq * (0.944 + 0.056 * scoop) * (1.0 + vib * vibdel * os.osc(5.4));
reed   = os.sawtooth(f) + os.square(f * 0.5) * 0.22; // reed bite + tube depth
breath = no.noise * en.ar(0.02, 0.25, gate) * breathA : fi.resonbp(2200, 2.0, 1.0);
body(x) = x : fi.lowpass(2, 2700) <: (fi.resonbp(1050, 2.2, 1.0) * 1.3, fi.resonbp(2300, 3.5, 1.0) * 0.5, _)
          :> _ * 0.34;
process = (reed : body) * env * 1.4 + breath * env : *(gain) : *(0.509) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
