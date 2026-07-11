// brass_stab — funk/soul/disco horn section hit: detuned saw pair, filter envelope
// FASTER and brighter than the amp envelope (the "blat"), 50ms pitch scoop into the
// note like a real player. Short notes = stabs; held notes = section swells.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
bite = hslider("bite", 0.7, 0, 1, 0.01);       // how hard the filter env slams open
scoop = en.asr(0.05, 1.0, 0.05, gate);          // players scoop up into the pitch
f     = freq * (0.97 + 0.03 * scoop);
att   = hslider("attack", 0.012, 0.002, 0.2, 0.001);   // (was 0.012)
dec   = hslider("decay", 0.25, 0.05, 1.0, 0.001);      // stab settle (was 0.25)
amp   = en.adsr(att, dec, 0.62, 0.12, gate);
fenv  = en.adsr(0.004, 0.10, 0.35, 0.10, gate); // opens faster than amp = the blat
body  = os.sawtooth(f) + os.sawtooth(f * 1.006) + os.sawtooth(f * 0.5) * 0.35;
cut   = 500 + fenv * (1200 + 5200 * bite);
process = body / 2.35 * amp * gain : fi.resonlp(cut, 1.4, 1.0) : *(0.91) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
