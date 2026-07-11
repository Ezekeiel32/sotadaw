// supersaw_fat — 7-voice detuned saw stack with stereo spread + sub, resonant LP.
// THE trance/edm wall. Zones: cutoff (filter), spread (detune+width), sub (level).
import("stdfaust.lib");
freq   = hslider("freq", 220, 30, 2500, 0.01);
gain   = hslider("gain", 0.7, 0, 1, 0.01);
gate   = button("gate");
cutoff = hslider("cutoff", 9000, 200, 16000, 1) : si.smoo;
spread = hslider("spread", 0.6, 0, 1, 0.01);
subl   = hslider("sub", 0.35, 0, 1, 0.01);

env  = en.adsr(0.012, 0.25, 0.8, 0.22, gate);
det(i) = freq * (1.0 + spread * 0.011 * (i - 3.0));
v(i) = os.sawtooth(det(i));
left  = v(0)*0.9 + v(1)*0.7 + v(2)*0.5 + v(3) + v(4)*0.3 + v(5)*0.2 + v(6)*0.15;
right = v(0)*0.15 + v(1)*0.2 + v(2)*0.3 + v(3) + v(4)*0.5 + v(5)*0.7 + v(6)*0.9;
sub   = os.osc(freq * 0.5) * subl;
mk(x) = fi.resonlp(cutoff, 1.1, 1.0, x + sub) * env * gain * 0.16 : ma.tanh;
process = mk(left), mk(right);
