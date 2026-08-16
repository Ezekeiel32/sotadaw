// nylon_guitar — classical/flamenco/bossa fingerstyle (clean_chime_guitar is
// electric-voiced; the nylon warmth did not exist). Karplus-Strong with a WARM
// finger-flesh excitation (dark burst, mid pluck point), classical-body modal
// trio (~100/210/420), moderate singing sustain. Flamenco rasgueado = fast
// near-simultaneous chord notes at high vel (vel opens the pick brightness);
// bossa comping = soft vel 0.4-0.6 = felt-warm.
// ZONE-ENRICHED (face law): warmth/body agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 196, 70, 1200, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
warmth = hslider("warmth", 0.55, 0, 1, 0.01);   // flesh .. nail
body = hslider("body", 0.4, 0, 1, 0.01);

burst = no.noise * en.ar(0.0006, 0.004, gate);
n = ma.SR / max(70.0, freq);
pluckdel = max(1.0, n * 0.28);                   // mid-string = round classical tone
damphz = (1600.0 + (1.0 - warmth) * 3400.0) * (0.6 + 0.4 * gain);  // vel = nail
excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
       : fi.lowpass(2, damphz);
loopfilter = fi.lowpass(1, 2200.0 + (1.0 - warmth) * 3000.0) * 0.9968;
string = (+ : de.fdelay4(4096, max(2.0, n - 2.0))) ~ loopfilter;
modal = _ <: fi.resonbp(100, 4, 0.4), fi.resonbp(210, 5, 0.32), fi.resonbp(420, 6, 0.22) :> _;
voice = excite : string <: _ * (1.0 - body * 0.5), (modal * body) :> _;
process = voice * gain * 1.0 <: _, _;  // headroom law: cert-verified (fingerstyle probe peaked -15 at 0.75 — lifted)
