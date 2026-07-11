// fx_djfilter — THE DJ mixer filter knob (one bipolar sweep, every DJ mixer has it):
// knob 0 = bypass-transparent, knob<0 sweeps a resonant lowpass DOWN (kills highs),
// knob>0 sweeps a resonant highpass UP (kills lows — the bass-swap tool).
// Stereo-through FX contract: 2 in -> 2 out.
import("stdfaust.lib");
knob  = hslider("knob", 0, -1, 1, 0.001) : si.smoo;
res   = hslider("res", 1.1, 0.5, 4, 0.01) : si.smoo;
lpc   = 60.0 * pow(300.0, 1.0 + min(0.0, knob));   // knob -1..0 -> 60Hz..18kHz
hpc   = 20.0 * pow(100.0, max(0.0, knob));         // knob  0..1 -> 20Hz..2kHz
f     = fi.resonlp(lpc, res, 1.0) : fi.resonhp(hpc, res, 1.0);
process = f, f;
