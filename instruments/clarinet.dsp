// clarinet — cylindrical bore closed at the reed = ODD harmonics own the tone
// (klezmer/dixieland/swing/balkan second-line; the palette's reeds are all
// conical-family — sax/duduk/zurna — no clarinet existed). Chalumeau lows are
// hollow and soft, clarion brightens; register decides timbre. Breath rides
// the envelope; a soft attack 'tongue' transient. Klezmer krechz/bends =
// automate pitch; `dark` sets the wood.
// ZONE-ENRICHED (face law): dark/breath agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 294, 130, 1600, 0.1);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
dark = hslider("dark", 0.5, 0, 1, 0.01);        // wood: bright stage .. dark folk
breath = hslider("breath", 0.25, 0, 1, 0.01);

settle = en.asr(0.03, 1.0, 0.04, gate);          // reed speaks fast but not instant
f = freq * (0.992 + 0.008 * settle);
amp = en.adsr(0.035, 0.06, 0.9, 0.12, gate);
// register-true brightness: chalumeau (<330Hz) darker, clarion opens
reg = max(0.0, min(1.0, (freq - 250.0) / 500.0));
cut = (900 + 2400 * reg + 1800 * (1.0 - dark)) * (0.6 + 0.4 * gain);  // vel = air
tongue = no.noise * 0.04 * en.ar(0.003, 0.02, gate) : fi.resonbp(1800, 2, 1.0);
air = no.noise * 0.02 * breath * amp : fi.resonbp(2600, 1.4, 1.0);
reed = os.square(f) * amp;
process = (reed * 0.85 + tongue + air) * gain * 0.42
        : fi.lowpass(2, min(cut, 9000))
        : fi.peak_eq(3.0, 1500, 900)
        <: _, _;
