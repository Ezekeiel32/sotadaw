// banjo — bluegrass/country/folk roll machine (bluegrass births had fiddle +
// harmonica but NO banjo — the genre's identity voice). Karplus-Strong string
// tuned BRIGHT and SHORT (fingerpick attack, fast head damping) into the pot:
// a drum-head resonator (two strong modal bands ~450/900Hz) that gives the
// "plunk". Fast rolls stay articulate because the string damps quickly.
// ZONE-ENRICHED (face law): pick/pot/sustain agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 294, 60, 2000, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
pick = hslider("pick", 0.75, 0, 1, 0.01);      // fingerpick brightness
pot = hslider("pot", 0.45, 0, 1, 0.01);        // head resonator blend
sustain = hslider("sustain", 0.3, 0, 1, 0.01); // banjo = short by nature

burst = no.noise * en.ar(0.0004, 0.003, gate);
n = ma.SR / max(60.0, freq);
pluckpos = 0.13;                                // near-bridge = banjo bite
pluckdel = max(1.0, n * pluckpos);
damphz = (2500.0 + pick * 6500.0) * (0.65 + 0.35 * gain);  // vel = pick force: soft rolls darken
excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
       : fi.lowpass(2, damphz);
fb = 0.978 + sustain * 0.012;                   // plunk .. mild ring
loopfilter = fi.lowpass(1, damphz) * fb;
string = (+ : de.fdelay4(4096, max(2.0, n - 2.0))) ~ loopfilter;
head = _ <: fi.resonbp(450, 3, 0.5), fi.resonbp(880, 4, 0.35) :> _;
voice = excite : string <: _ * (1.0 - pot * 0.55), (head * pot) :> _;
process = voice * gain * 1.0 <: _, _;  // headroom law: 0 clipped @ vel 1.0 (roll + cert probes)
