// strings_disco — Solina-style ensemble strings: detuned saw stack through two
// LFO-modulated chorus delays, slow attack, long release. Disco euphoria pads.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.55, 0, 1, 0.01);
gate = button("gate");
att  = hslider("attack", 0.09, 0.01, 1.0, 0.001);   // bow-in (was 0.09)
rel  = hslider("release", 0.5, 0.05, 2.5, 0.001);   // tail (was 0.5)
lush = hslider("lush", 0.0035, 0, 0.01, 0.0001);    // chorus depth (was 0.0035)
env  = en.adsr(att, 0.3, 0.85, rel, gate);
saws = os.sawtooth(freq * 0.996) + os.sawtooth(freq) + os.sawtooth(freq * 1.004)
     + os.sawtooth(freq * 0.5 * 0.997) * 0.5 + os.sawtooth(freq * 0.5 * 1.003) * 0.5;
dry  = saws / 3.0 * env;
cho(rate, base) = de.fdelay(4096, (base + lush * os.osc(rate)) * ma.SR);
wet  = ((dry : cho(0.37, 0.016)), (dry : cho(0.53, 0.023))) :> _ * 0.5;
process = (dry * 0.45 + wet * 0.75) * gain : fi.lowpass(2, 6500) <: _,_;
