// the SUB DROP: the modern record's impact one-shot — a sine falling an
// octave-and-change (freq -> freq*ratio) over "fall" seconds with a long
// tail. MONO SUB LAW: single centered lane, keep it dry. depth = tanh
// drive. Structural 0.85 headroom (vel-1.0 law). freq zone = start pitch.
import("stdfaust.lib");
freq = hslider("freq", 55, 20, 200, 0.001);
gain = hslider("gain", 0.9, 0, 1, 0.01);
gate = button("gate");
fall = hslider("fall", 0.8, 0.1, 3, 0.01);
ratio = hslider("ratio", 0.45, 0.2, 1, 0.01);
depth = hslider("depth", 1.3, 0.5, 4, 0.01);
env = en.ar(0.002, fall * 2.2, gate);
prog = en.ar(0.001, fall, gate);                  // 1 -> 0 over the fall
f = freq * (ratio + (1.0 - ratio) * prog);
process = (os.osc(f) * depth : ma.tanh) * env * gain * 0.85 <: _,_;
