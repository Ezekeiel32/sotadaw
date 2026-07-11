// accordion — musette reeds: two detuned square-ish banks in octaves, bellows
// swell, gentle tremolo from the beat between reeds. Cumbia, folk, chanson,
// tango-adjacent comping; sustained chords breathe.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
bellows = hslider("bellows", 0.06, 0.01, 0.5, 0.001);  // pump-in (was 0.06)
tone    = hslider("tone", 2800, 1000, 6000, 1);        // reediness (was 2800)
env   = en.adsr(bellows, 0.1, 0.85, 0.12, gate);
reed(f) = os.pulsetrain(f, 0.45) - 0.45;
bank  = reed(freq * 0.9965) + reed(freq * 1.0035) + reed(freq * 2.0 * 1.002) * 0.4
      + reed(freq * 0.5) * 0.3;
process = bank / 2.1 * env * gain : fi.lowpass(2, tone) : fi.highpass(1, 110) : *(0.548) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
