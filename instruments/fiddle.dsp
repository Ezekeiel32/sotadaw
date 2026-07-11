// fiddle — bowed folk violin: sawtooth bow + rosin noise through violin body
// formants (~285/470/1100 Hz), bow-speed attack, DELAYED vibrato (arrives after
// the note settles — the fiddler's hand). Bluegrass breaks, old-time double stops.
// Research: docs/research_genre_expansion_sota.md. ZONE-ENRICHED (face law).
import("stdfaust.lib");
freq = hslider("freq", 440, 100, 2500, 0.001);
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
bowA   = hslider("bow", 0.05, 0.005, 0.3, 0.001);     // bow attack s
vibD   = hslider("vibrato", 0.007, 0, 0.02, 0.0005);  // vibrato depth (freq ratio)
vibR   = hslider("vibrate", 5.5, 3, 8, 0.1);          // vibrato rate Hz
bright = hslider("bright", 0.55, 0, 1, 0.01);         // direct-vs-body blend
venv = en.asr(0.35, 1.0, 0.1, gate);                   // vibrato fades IN late
env  = en.adsr(bowA, 0.08, 0.85, 0.15, gate);
f = freq * (1.0 + vibD * os.osc(vibR) * venv);
raw = (os.sawtooth(f) + no.noise * 0.04) * env;        // bow + rosin
body = raw <: fi.resonbp(285, 4, 0.8), fi.resonbp(470, 4, 0.7), fi.resonbp(1100, 3, 0.5) :> _;
process = (raw * bright + body * (1.0 - bright * 0.5)) * gain * 0.28 : fi.lowpass(2, 7000) <: _,_;  // vel-1.0 headroom (gain zone is engine-driven; body formants SUM)
