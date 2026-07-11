// log_drum — THE amapiano bass: pitched woody knock (fast pitch-drop mid layer)
// over a round sub tail. Play it as a bassline (log_drum_bass technique:
// it answers the kick in the holes). Default G2-ish.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 98, 20, 2000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
dec    = hslider("decay", 0.32, 0.08, 1.0, 0.001);     // barrel ring (was 0.32)
knockA = hslider("knock", 0.65, 0, 1.2, 0.01);         // stick mix (was 0.65)
sub   = os.osc(freq) * en.adsr(0.004, dec, 0.0, 0.07, gate);
kenv  = en.ar(0.001, 0.028, gate);
knock = os.osc(freq * 2.0 * (1.0 + 0.9 * kenv)) * en.ar(0.001, 0.09, gate)
        : fi.resonlp(1300, 2.2, 1.0);
process = (sub + knock * knockA) * gain : fi.lowpass(2, 2400) : *(0.444) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
