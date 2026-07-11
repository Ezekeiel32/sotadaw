// metallic hat: 6 detuned squares (808-style) -> bandpass + hp, fast env
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
decay = hslider("decay", 0.045, 0.01, 0.4, 0.001);
metal = os.square(263) + os.square(400) + os.square(421) + os.square(474) + os.square(587) + os.square(845);
env = en.ar(0.0005, decay, gate);
sizzle = hslider("sizzle", 7500, 5000, 10000, 1);      // body cut (was 7500)
tone   = hslider("tone", 10500, 6000, 14000, 1);       // ring centre (was 10500)
process = metal/6 : fi.highpass(4, sizzle) : fi.resonbp(tone, 2.5, 1) : *(env*gain*1.4) <: _,_;
