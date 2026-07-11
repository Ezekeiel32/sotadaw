// steel_pan — struck pan: fundamental + strong 2x and ~2.4x partials (the pan's
// dents), bright ping attack, medium ring. Soca/calypso lead, tropical color.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.65, 0, 1, 0.01);
gate = button("gate");
strike = en.ar(0.001, 0.012, gate);
dec   = hslider("decay", 0.6, 0.15, 2.0, 0.01);        // pan ring (was 0.6)
pingA = hslider("ping", 0.2, 0, 0.6, 0.01);            // strike (was 0.2)
tone  = hslider("tone", 7500, 2000, 11000, 1);         // veil (was 7500)
body  = os.osc(freq) * en.adsr(0.002, dec, 0.0, 0.15, gate);
harm  = (os.osc(freq * 2.0) * 0.55 + os.osc(freq * 2.41) * 0.3)
        * en.adsr(0.001, 0.5, 0.0, 0.12, gate);
ping  = no.noise * strike * pingA : fi.resonbp(freq * 4.0, 3.0, 1.0);
process = (body + harm + ping) * gain : fi.lowpass(2, tone) : *(0.56) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
