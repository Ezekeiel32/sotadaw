// chip_bass — NES-style stepped triangle bass: mellow, hollow, faintly buzzy. The
// triangle is quantized to `steps` levels (NES APU = 16, the 4-bit stairstep) for the
// chip character; light tanh drive adds grit. Sits under chiptune_pulse leads.
import("stdfaust.lib");
freq = hslider("freq", 110, 20, 1000, 0.001);
gain = hslider("gain", 0.85, 0, 1, 0.01);
gate = button("gate");
steps = hslider("steps", 16, 4, 64, 1);        // triangle quantization (NES=16)
decay = hslider("decay", 0.7, 0.1, 3, 0.01);
tone  = hslider("tone", 3800, 400, 9000, 1);
drive = hslider("drive", 1.15, 0.5, 3, 0.01);
tri  = os.triangle(freq);
half = steps * 0.5;
stepped = floor(tri*half + 0.5) / half;        // quantize to 'steps' levels
env = en.adsr(0.002, decay, 0.55, 0.08, gate);
process = (stepped*drive : ma.tanh) * env * gain : fi.lowpass(2, tone) <: _,_;
