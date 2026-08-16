// tuba — low brass foundation (balkan_brass oompah, polka, ska/2tone walkdowns,
// NOLA brass band bass; the palette's basses are all synth-family — no wind bass
// existed). Conical-bore character: round fundamental (sine anchor) + saw bark
// filtered dark, slow lip settle from 3% flat (~80ms — big mouthpieces speak
// late), tuba formant ~315Hz, breath thump on the attack. Short notes = oompah
// pumps; held notes = swells.
// ZONE-ENRICHED (face law): bark/breath/attack agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 82, 25, 400, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
bark = hslider("bark", 0.45, 0, 1, 0.01);        // brass edge: dark tuba .. sousaphone blat
breath = hslider("breath", 0.4, 0, 1, 0.01);     // attack air thump
att = hslider("attack", 0.015, 0.004, 0.15, 0.001);

settle = en.asr(0.08, 1.0, 0.06, gate);           // low brass speaks late
f = freq * (0.97 + 0.03 * settle);
amp = en.adsr(att, 0.10, 0.82, 0.12, gate);
fenv = en.adsr(0.012, 0.16, 0.6, 0.12, gate);
cut = (160 + fenv * (200 + 1500 * bark)) * (0.6 + 0.4 * gain);  // vel = air: soft tuba is round, hard barks
thump = no.noise * 0.05 * breath * en.ar(0.002, 0.05, gate) : fi.lowpass(2, 700);
body = os.osc(f) * 0.52 + os.sawtooth(f) * 0.48 * amp;
process = (body * amp + thump) * gain * 0.85  // headroom law: 0 clipped @ vel 1.0 (oompah + held-swell probe)
        : fi.resonlp(min(cut, 8000), 1.05, 1.0)
        : fi.peak_eq(4.0, 315, 260)
        <: _, _;
