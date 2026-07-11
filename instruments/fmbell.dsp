// metallic FM bell: inharmonic ratio 3.5, long decay
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 6000, 0.001);
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
ratio  = hslider("ratio", 3.5, 0.5, 8, 0.01);       // inharmonicity (was 3.5)
dec    = hslider("decay", 2.5, 0.3, 6, 0.01);       // ring length (was 2.5)
bright = hslider("bright", 1.2, 0.1, 3, 0.01);      // mod-index decay (was 1.2)
env  = en.ar(0.002, dec, gate);
ienv = en.ar(0.002, bright, gate);
mod  = os.osc(freq*ratio) * (freq*ratio) * ienv;   // inharmonic -> metallic
car  = os.osc(freq + mod);
process = car * env * gain <: _,_;
