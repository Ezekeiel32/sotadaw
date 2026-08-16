// mbira — Shona mbira dzavadzimu (chimurenga's identity voice; kalimba existed
// but the BUZZ did not, and the buzz IS the instrument: bottle caps + shells
// on the soundboard rattle sympathetically with every tine). Tine = kalimba
// family (near-sine + inharmonic partial), plus the machachara: an amplitude-
// following rattle band gated by the tine's own envelope, chattering at an
// irregular ~110Hz — it breathes WITH the note, not on top of it. Interlocking
// kushaura/kutsinhira lines want two lanes of this voice an octave apart.
// ZONE-ENRICHED (face law): buzz/decay agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 440, 60, 3000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
buzz = hslider("buzz", 0.55, 0, 1, 0.01);      // machachara amount
dec = hslider("decay", 0.5, 0.1, 1.6, 0.01);   // tine ring

tenv = en.adsr(0.001, dec, 0.0, 0.12, gate);
tine = os.osc(freq) * tenv;
partial = os.osc(freq * 2.04) * en.adsr(0.001, 0.11, 0.0, 0.05, gate) * 0.3;
click = no.noise * en.ar(0.0004, 0.005, gate) * 0.25 : fi.highpass(1, 1400);
// machachara: rattle follows the tine's envelope, chatter = irregular pulse
// (two coprime-ish LFOs beat against each other so the rattle never loops)
chatter = (os.lf_sawpos(113.0) < 0.4) * (os.lf_sawpos(87.0) < 0.55);
rattle = no.noise * tenv * tenv * chatter * buzz * 0.7
       : fi.resonbp(3300, 1.3, 1.0) : fi.highpass(2, 1800);
process = (tine + partial + click + rattle) * gain * 0.5
        : fi.lowpass(2, 8000) <: _, _;
