// cine_brass — cinematic brass swell: dark detuned saw wall with an octave
// double below, SLOW filter bloom (the crescendo lives in the filter), long
// release. Held notes = trailer swells; brass_stab stays the funk voice.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 110, 20, 4000, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
swell = hslider("swell", 0.7, 0, 1, 0.01);            // how far the bloom opens
att   = hslider("attack", 0.18, 0.02, 1.0, 0.001);     // (was 0.18)
rel   = hslider("release", 0.5, 0.05, 2.5, 0.001);     // (was 0.5)
amp   = en.adsr(att, 0.3, 0.85, rel, gate);
bloomT = hslider("bloom", 0.6, 0.1, 2.0, 0.001);       // bloom time (was 0.6)
bloom = en.adsr(bloomT, 0.8, 0.3, 0.6, gate);          // opens SLOW, rests DARK
wall  = os.sawtooth(freq) + os.sawtooth(freq * 1.005) + os.sawtooth(freq * 0.995)
      + os.sawtooth(freq * 0.5) * 0.7 + os.sawtooth(freq * 0.501) * 0.5;
cut   = 200 + bloom * (350 + 1500 * swell);
process = wall / 3.4 * amp * gain : fi.resonlp(cut, 1.2, 1.0) : *(0.678) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
