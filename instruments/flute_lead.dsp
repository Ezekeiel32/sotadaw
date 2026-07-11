// flute_lead — breathy flute: strong fundamental, soft octave, air noise that
// follows the envelope, late vibrato. Jazz/bossa heads, trap-flute toplines,
// highlife runs. Play legato lines; short notes read as staccato tonguing.
// ZONE-ENRICHED (face law) — defaults are EXACTLY the old constants.
import("stdfaust.lib");
freq = hslider("freq", 440, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
att    = hslider("attack", 0.045, 0.005, 0.4, 0.001); // tonguing (was 0.045)
vib    = hslider("vibrato", 0.012, 0, 0.04, 0.0001);   // depth (was 0.012)
airA   = hslider("air", 0.09, 0, 0.3, 0.001);          // breath (was 0.09)
env    = en.adsr(att, 0.1, 0.85, 0.15, gate);
vibdel = en.asr(0.3, 1.0, 0.1, gate);
f      = freq * (1.0 + vib * vibdel * os.osc(5.2));
tone   = os.osc(f) + os.osc(f * 2.0) * 0.18 + os.osc(f * 3.0) * 0.05;
air    = no.noise * airA : fi.resonbp(f * 5.0, 1.2, 1.0) : fi.lowpass(1, 5200);
process = (tone * 0.8 + air) * env * gain <: _,_;
