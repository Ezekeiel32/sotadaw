// chiptune_pulse — the 8-bit lead: variable-duty pulse (SID/NES/Game Boy voice).
// Duty 0.5=full square (hollow), 0.25=reedy, 0.125=nasal/thin; PWM LFO breathes the
// timbre; `drop` = the NES downward blip on attack (starts sharp, settles to pitch).
// Raw pulse aliasing is period-authentic to the chip; `tone` tames the very top.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
duty    = hslider("duty", 0.5, 0.125, 0.875, 0.001);      // pulse width (0.5=square)
pwm     = hslider("pwm", 0.12, 0, 0.5, 0.001);            // PWM sweep depth
pwmrate = hslider("pwmrate", 1.8, 0, 8, 0.01);           // PWM LFO Hz
drop    = hslider("drop", 0.0, 0, 1, 0.01);              // NES attack pitch-blip depth
droptime= hslider("droptime", 0.04, 0.005, 0.3, 0.001);
vibrato = hslider("vibrato", 0.004, 0, 0.03, 0.0001);     // vibrato depth (ratio)
vibrate = hslider("vibrate", 5, 0, 9, 0.01);
tone    = hslider("tone", 11000, 800, 16000, 1);         // gentle top-end lowpass
env  = en.adsr(0.001, 0.08, 0.75, 0.05, gate);
pdrop = drop * en.ar(0.001, droptime, gate);              // 1 -> 0 fast
vib   = 1 + vibrato * os.osc(vibrate);
f2    = freq * (1 + pdrop) * vib;
d     = duty + pwm * 0.5 * os.osc(pwmrate);
pulse = (os.lf_sawpos(f2) < d) - 0.5;                     // +/-0.5 variable-duty square
process = pulse * 2 * env * gain : fi.lowpass(1, tone) : *(0.912) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
