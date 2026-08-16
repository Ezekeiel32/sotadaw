// tumbi — bhangra's one-string high-tension lute (dhol existed, the iconic
// treble ostinato voice did not). Single Karplus-Strong string, VERY tight:
// staccato plucks, nasal bright attack, quick decay, small gourd body bump.
// Plays the classic G4-C5 register ostinatos; fast 16th lines stay separate
// notes because the string chokes fast.
// ZONE-ENRICHED (face law): bite/choke agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 392, 120, 2500, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
bite = hslider("bite", 0.7, 0, 1, 0.01);       // pluck edge
choke = hslider("choke", 0.6, 0, 1, 0.01);     // how fast the string dies

burst = no.noise * en.ar(0.0003, 0.0022, gate);
n = ma.SR / max(120.0, freq);
pluckdel = max(1.0, n * 0.09);                  // extreme near-bridge = nasal
damphz = (3200.0 + bite * 5800.0) * (0.65 + 0.35 * gain);  // vel = pluck force
excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
       : fi.lowpass(2, damphz);
fb = 0.988 - choke * 0.014;                     // ring .. choked
loopfilter = fi.lowpass(1, damphz) * fb;
string = (+ : de.fdelay4(2048, max(2.0, n - 2.0))) ~ loopfilter;
gourd = _ <: _ * 0.82, (fi.resonbp(620, 5, 0.3)) :> _;
process = excite : string : gourd * gain * 1.0 <: _, _;  // headroom law: 0 clipped @ vel 1.0 (ostinato + cert probes)
