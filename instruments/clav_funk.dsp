// clav_funk — the Stevie clavinet: narrow pulse + snapping attack transient,
// fast decay, bright and percussive. Play it staccato with ghost velocities.
// zones (inits = the original constants): duty = pulse width (hollowness of the
// bark), snap = attack noise level, decay = string decay s, tone = resonant LP Hz.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
duty  = hslider("duty", 0.28, 0.1, 0.45, 0.01);
snapL = hslider("snap", 0.5, 0, 1.5, 0.01);
dec   = hslider("decay", 0.35, 0.1, 1, 0.01);
toneF = hslider("tone", 6500, 2000, 12000, 10);
env   = en.adsr(0.001, dec, 0.12, 0.05, gate);   // struck string: quick decay, thin sustain
snap  = no.noise * en.ar(0.001, 0.012, gate) * snapL : fi.highpass(2, 2500);
pulse = os.pulsetrain(freq, duty) - duty;         // narrow duty = hollow clav bark
tone  = pulse * env + snap * env;
process = tone * gain : fi.highpass(1, 120) : fi.resonlp(toneF, 1.1, 1.0) : *(0.421) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
