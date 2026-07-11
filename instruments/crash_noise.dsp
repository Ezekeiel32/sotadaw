// crash_noise: synthesized crash cymbal — bright noise burst, exponential decay.
// The arrangement's downbeat marker (drops/chorus arrivals). zones: freq shifts
// the highpass corner (pitch ~ brightness), decay = ring seconds, tone = the
// lowpass ceiling (dark club wash -> full-spectrum splash), shimmer = the
// resonant sizzle band's presence (0 = pure wash). Defaults keep the original
// voice byte-faithful (tone 0.8 -> 14k ceiling, shimmer 1.0 -> full sizzle).
import("stdfaust.lib");
freq    = hslider("freq", 300, 50, 2000, 0.1);
gain    = hslider("gain", 0.6, 0, 1, 0.01);
gate    = button("gate");
decay   = hslider("decay", 1.8, 0.3, 5.0, 0.01);
tone    = hslider("tone", 0.8, 0.0, 1.0, 0.01);
shimmer = hslider("shimmer", 1.0, 0.0, 1.0, 0.01);
env  = gate : en.adsre(0.002, decay, 0.0, decay);
hp   = max(2500, freq * 12);
lp   = 6000 + tone * 10000;
sizz = no.noise : fi.highpass(3, hp) : fi.lowpass(2, lp);
shim = no.noise : fi.resonbp(hp * 1.6, 2.2, 0.5);
process = (sizz + shim * shimmer) * env * env * gain * 0.7 : ma.tanh <: _,_;
