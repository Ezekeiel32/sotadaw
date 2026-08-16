// duduk — Armenian apricot-wood double reed: a WARM, dark, near-cylindrical tone with
// a deep slow vibrato (the "cry") and a soft pitch SCOOP into each note. Legato and
// mournful — the definitive cinematic lament voice. Automate pitch for portamento.
import("stdfaust.lib");
freq = hslider("freq", 220, 80, 1500, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
breath = hslider("breath", 0.15, 0, 0.5, 0.01);
warmth = hslider("warmth", 1800, 600, 4000, 1);      // dark reed lowpass
cry    = hslider("cry", 0.012, 0, 0.04, 0.0001);     // deep vibrato depth
cryrate= hslider("cryrate", 4.5, 0, 7, 0.01);        // slow vibrato
scoop  = hslider("scoop", 0.02, 0, 0.08, 0.001);     // attack pitch scoop
att = hslider("attack", 0.05, 0.005, 0.5, 0.001);
rel = hslider("release", 0.25, 0.02, 1.5, 0.001);
vib    = 1 + cry*en.asr(0.4, 1, 0.1, gate)*os.osc(cryrate);
pscoop = 1 - scoop*en.ar(0.001, 0.06, gate);         // scoop up into pitch
f2     = freq*vib*pscoop;
env    = en.adsr(att, 0.2, 0.9, rel, gate);
reed   = os.square(f2);                                   // odd harmonics (cylindrical bore + double reed)
air    = no.noise*breath*0.4 : fi.resonbp(480, 1.5, 1.0);  // ~480 Hz reed resonance = the dark cry (Acta Acustica 2024)
body   = reed : fi.lowpass(2, warmth) : fi.resonlp(900, 1.6, 1.0);
process = (body*0.9 + air) * env * gain * 0.42 <: _,_;  // headroom law: the 900Hz resonlp peak lands ON an A5 fundamental (+4dB) — cleared with margin
