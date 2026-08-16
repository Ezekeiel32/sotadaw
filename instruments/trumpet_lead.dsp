// trumpet_lead — melodic SOLO trumpet (balkan_brass/salsa/ska/mariachi/afrobeat
// horn lines; the palette had section stabs and cinematic swells but NO soloist).
// A single voice, not a section: one saw into an envelope-bloomed lowpass (the
// brass "blare" = brightness FOLLOWS air pressure), bell formant peak ~1.25kHz,
// lip settle (starts 1.5% flat, lands in 50ms — players slur INTO the note),
// DELAYED vibrato (real players add it after the note speaks, ~350ms), breath
// noise band riding the amp envelope. Held notes sing; short notes tongue.
// ZONE-ENRICHED (face law): vibrato/bright/attack agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 440, 80, 2500, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
vibrato = hslider("vibrato", 0.5, 0, 1, 0.01);   // depth: 0 straight .. 1 = +/-35 cents
bright = hslider("bright", 0.6, 0, 1, 0.01);     // how far the bell opens
att = hslider("attack", 0.02, 0.004, 0.2, 0.001); // tongued .. breathed-in

settle = en.asr(0.05, 1.0, 0.05, gate);           // lip slur into pitch
vibenv = en.asr(0.35, 1.0, 0.1, gate);            // vibrato arrives late
vib = os.osc(5.5) * vibrato * 0.02 * vibenv;
f = freq * (0.985 + 0.015 * settle) * (1.0 + vib);
amp = en.adsr(att, 0.08, 0.85, 0.15, gate);
fenv = en.adsr(0.008, 0.12, 0.75, 0.15, gate);    // blare opens faster than amp
cut = (650 + fenv * (900 + 4600 * bright)) * (0.55 + 0.45 * gain);  // vel = breath pressure: soft plays DARK, hard blares (gain zone rides velocity)
breath = no.noise * 0.012 * amp : fi.resonbp(3400, 1.2, 1.0);
horn = os.sawtooth(f) * amp;
process = (horn + breath) * gain * 0.44   // headroom law: 0 clipped @ vel 1.0 incl. legato overlaps
        : fi.resonlp(min(cut, 16000), 1.15, 1.0)
        : fi.peak_eq(5.0, 1250, 700)
        <: _, _;
