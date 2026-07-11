// hard-techno kick: steep pitch drop + noise click, driven hard through tanh
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 50, 20, 300, 0.001);
gain = hslider("gain", 0.95, 0, 1, 0.01);
gate = button("gate");
drop  = hslider("drop", 6, 1, 12, 0.1);             // pitch-drop depth (was 6)
dec   = hslider("decay", 0.35, 0.05, 1.0, 0.001);   // body decay (was 0.35)
clik  = hslider("click", 0.5, 0, 1, 0.01);          // attack click level (was 0.5)
drive = hslider("drive", 3, 1, 8, 0.1);             // tanh drive (was 3)
penv = en.ar(0.001, 0.03, gate);              // fast, steep pitch envelope
aenv = en.adsr(0.001, dec, 0.0, 0.05, gate);
click = en.ar(0.0005, 0.006, gate) * no.noise * clik;
body = os.osc(freq*(1 + drop*penv));
process = ((body + click) * drive : ma.tanh) * aenv * gain : *(0.913) <: _,_;  // headroom law: cert-calibrated, 0 clipped @ vel 1.0
