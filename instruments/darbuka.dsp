// darbuka — goblet drum (arabesk/dabke/chaabi/turkish pop; the palette had
// conga/dhol but no Middle-Eastern goblet voice — arabesk births rode a
// trap kit). PITCH SELECTS STROKE like a keyboard-mapped kit: low notes
// (< ~G3 / 200Hz) = DUM (deep goblet resonance, fast round decay), high
// notes = TEK (rim slap: metallic ring + bright snap, very short). The
// crossfade is continuous so mid pitches blend naturally; freq also TUNES
// both layers, so a lane's grid pitch picks the drum's size.
// ZONE-ENRICHED (face law): snap/ring agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 110, 50, 1200, 0.1);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
snap = hslider("snap", 0.6, 0, 1, 0.01);       // tek brightness/click amount
ring = hslider("ring", 0.35, 0, 1, 0.01);      // goblet ring length

exc = ba.impulsify(gate);
tekness = max(0.0, min(1.0, (freq - 140.0) / 160.0));  // 140Hz->0 .. 300Hz->1
dumf = max(70.0, min(freq, 160.0));
// DUM: goblet fundamental + hoop partial, round attack, 0.18-0.4s decay
dum = ((exc : fi.resonbp(dumf, 14, 1)) * 1.0
     + (exc : fi.resonbp(dumf * 2.31, 20, 1)) * 0.3)
    * en.ar(0.001, 0.18 + 0.25 * ring, gate);
// TEK: ceramic rim ring (inharmonic pair) + slap noise band, ~80ms
tekf = max(300.0, freq * 2.4);
tek = ((exc : fi.resonbp(tekf, 30, 1)) * 0.8
     + (exc : fi.resonbp(tekf * 1.83, 34, 1)) * 0.5
     + (no.noise * en.ar(0.0005, 0.020, gate) : fi.highpass(2, 2500)) * (0.5 + 0.7 * snap))
    * en.ar(0.0008, 0.05 + 0.04 * snap, gate);
process = (dum * 3.4 * (1.0 - 0.85 * tekness) + tek * 1.9 * (0.15 + 0.85 * tekness))
        * gain * 0.32 <: _, _;  // headroom law: 0 clipped @ vel 1.0 (maqsum + cert probes)
