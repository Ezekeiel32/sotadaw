// fm2op — THE REUSABLE FM OPERATOR PRIMITIVE (w55, r-17 item 136).
// True DX-style PHASE modulation (os.oscp), one carrier + one
// modulator with its own fast-decay envelope (mod index IS the attack
// transient — the DX7 e-piano trick). Canonical presets (set zones via
// source params / automation):
//   e-piano body   ratio 1.0   index 1.5  index_decay 0.6
//   e-piano tine   ratio 14.0  index 5.0  index_decay 0.03
//   harmonic brass ratio 1.0   index 6.0  index_decay 0.4
//   bell/metallic  ratio 3.5   index 6.0  index_decay 1.2  (non-integer
//                  C:M = inharmonic — the r-17 ratio rule)
// JIT voice (unregistered) — renders instantly; AOT-bake when hot.
import("stdfaust.lib");
freq  = hslider("freq", 220, 20, 4000, 0.001);
gain  = hslider("gain", 0.6, 0, 1, 0.01);
gate  = button("gate");
ratio = hslider("ratio", 1.0, 0.25, 16.0, 0.01);
index = hslider("index", 3.0, 0.0, 12.0, 0.01);
idec  = hslider("index_decay", 0.25, 0.01, 2.0, 0.001);
adec  = hslider("amp_decay", 0.9, 0.05, 4.0, 0.001);
asus  = hslider("amp_sustain", 0.35, 0.0, 1.0, 0.01);

ienv = en.adsr(0.001, idec, 0.0, idec, gate);       // index falls to 0
aenv = en.adsr(0.002, adec, asus, 0.3, gate);
mod  = os.osc(freq*ratio) * index * ienv;
car  = os.oscp(freq, mod);
// headroom law: PM sine peaks at 1.0 -> 0.85 keeps vel-1.0 solo clean
process = car * aenv * gain * 0.85 <: _,_;
