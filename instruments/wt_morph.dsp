// wt_morph — THE WAVETABLE FAMILY exemplar (BEST_DAW_30 #6).
// A wavetable-class morphing oscillator, alias-safe by construction: three
// band-limited harmonic frames (soft sine-stack / hollow odd-harmonic /
// bright saw-stack) crossfaded by the `wave` scan knob, per-frame harmonic
// count capped under Nyquist. `motion` slow-scans the table like a wavetable
// LFO. ZONE LAW: every knob agent-tweakable; defaults are the played truth.
import("stdfaust.lib");
freq   = hslider("freq", 220, 20, 4000, 0.001);
gain   = hslider("gain", 0.5, 0, 1, 0.01);
gate   = button("gate");
wave   = hslider("wave", 0.5, 0, 2, 0.001);      // 0 soft -> 1 hollow -> 2 bright
motion = hslider("motion", 0.0, 0, 4, 0.01);     // Hz of table scan (0 = still)
cutoff = hslider("cutoff", 9000, 500, 12000, 1);
att    = hslider("attack", 0.005, 0.001, 1.0, 0.001);
rel    = hslider("release", 0.35, 0.02, 2.0, 0.001);

env = en.adsr(att, 0.15, 0.85, rel, gate);
// scan position: the knob plus a slow triangle ride, clamped to the table
pos = min(2.0, max(0.0, wave + motion0)) with { motion0 = os.lf_triangle(max(motion, 0.001)) * (motion > 0); };
// band-limited partial stack: k-th harmonic silenced above 0.45*SR
h(k, a) = a * os.osc(freq * k) * (freq * k < ma.SR * 0.45);
soft    = h(1, 1.0) + h(2, 0.28) + h(3, 0.09) + h(4, 0.04);
hollow  = h(1, 1.0) + h(3, 0.42) + h(5, 0.22) + h(7, 0.12) + h(9, 0.07);
bright  = h(1, 1.0) + h(2, 0.52) + h(3, 0.36) + h(4, 0.27) + h(5, 0.22)
        + h(6, 0.17) + h(7, 0.14) + h(8, 0.11);
xf(a, b, t) = a * (1 - t) + b * t;
osc = xf(soft, hollow, min(pos, 1.0)) * (pos <= 1.0)
    + xf(hollow, bright, max(pos - 1.0, 0.0)) * (pos > 1.0);
process = osc / 2.2 * env * gain : fi.lowpass(3, cutoff) : *(0.82) <: _,_;  // headroom law
