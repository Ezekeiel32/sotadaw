// clave — rosewood click: impulse into one high-Q resonator (~2.5k), the
// timeline instrument of the whole Afro-Cuban family. freq retunes the wood.
import("stdfaust.lib");
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
freq  = hslider("freq", 2500, 800, 4000, 1);
decay = hslider("decay", 0.09, 0.02, 0.4, 0.001);
tone  = hslider("tone", 60, 20, 200, 1);               // resonator Q: wood hardness (was 60)
exc = ba.impulsify(gate);
process = exc : fi.resonbp(freq, tone, 1) : *(20) : fi.highpass(2, 600)
          : *(en.ar(0.0005, decay, gate) * gain) : *(0.8) <: _,_;
