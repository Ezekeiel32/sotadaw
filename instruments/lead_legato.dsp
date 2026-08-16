// lead_legato — TRUE LEGATO for melodic lines (w77, r-26 item 162):
// the sub_808_slide mechanism lifted to lead register. The freq zone
// is slewed (glide ms) so any note-to-note change GLIDES; with
// OVERLAPPING notes the engine's mono tracking holds the gate open —
// the destination note's attack transient never retriggers, exactly
// the sampler transition model. The articulation op ties the notes;
// this voice supplies the connected phrase. Sustain-shaped envelope
// (a lead holds, unlike the 808's decay tail).
// JIT voice; AOT-bake when hot.
import("stdfaust.lib");
glide = hslider("glide", 60, 5, 400, 1);
freq  = hslider("freq", 220, 20, 3000, 0.001)
        : si.smooth(ba.tau2pole(glide * 0.001));
gain  = hslider("gain", 0.6, 0, 1, 0.01);
gate  = button("gate");
att   = hslider("attack", 0.012, 0.001, 0.5, 0.001);
rel   = hslider("release", 0.22, 0.02, 2.0, 0.001);
cut   = hslider("cutoff", 3800, 300, 12000, 1) : si.smoo;
vib   = hslider("vibrato", 0.20, 0, 1, 0.01);

// vibrato blooms late (300ms) — the singer's law, never on the attack
vibenv = en.asr(0.3, 1.0, 0.2, gate);
f = freq * (1.0 + vib * vibenv * 0.006 * os.osc(5.3));
osc2 = os.sawtooth(f) * 0.62 + os.osc(f) * 0.38;
env = en.adsr(att, 0.15, 0.85, rel, gate);
// headroom law: saw+sine mix through LP — 0.5 keeps vel-1.0 solo clean
process = osc2 : fi.lowpass(2, cut) : *(env * gain * 0.5) <: _,_;
