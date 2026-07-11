// dhol — the dagga (bass head) of the Punjabi dhol: a deep booming membrane hit
// with a STRONG strike pitch-drop (players press the head) + a skin-slap attack.
// Drives the bhangra CHAAL. Higher freq tightens toward the tilli (treble head).
// Research: docs/research_genre_expansion_sota.md. ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq = hslider("freq", 70, 30, 400, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
dec  = hslider("decay", 0.45, 0.1, 1.5, 0.01);   // boom length
bend = hslider("bend", 0.35, 0, 0.8, 0.01);      // strike pitch-drop depth (dhol is DEEP)
slap = hslider("slap", 0.5, 0, 1.2, 0.01);       // skin-slap attack level
penv = en.ar(0.001, 0.06, gate);
tone = os.osc(freq * (1.0 + bend * penv)) * en.adsr(0.001, dec, 0.0, 0.15, gate);
snap = no.noise * en.ar(0.0005, 0.012, gate) : fi.resonbp(freq * 9.0, 1.2, 1.0);
process = (tone + snap * slap) * gain * 0.78 : fi.lowpass(2, 3000) <: _,_;  // vel-1.0 headroom (gain zone is engine-driven)
