// formant_vox — the singing synth / talkbox: a glottal saw driven through three vocal
// FORMANT bandpasses. `vowel` morphs Ah(0) -> Ee(0.5) -> Oo(1); `breath` adds air;
// vibrato makes it sing. The vocal / robot-voice / vocoder-source gap, filled.
// (Formant centres are neutral-male approximations; refine per research.)
import("stdfaust.lib");
freq = hslider("freq", 180, 40, 1500, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
vowel   = hslider("vowel", 0.0, 0, 1, 0.001);    // Ah -> Ee -> Oo
breath  = hslider("breath", 0.12, 0, 1, 0.01);
vibrato = hslider("vibrato", 0.006, 0, 0.03, 0.0001);
vibrate = hslider("vibrate", 5.2, 0, 8, 0.01);
att = hslider("attack", 0.03, 0.001, 1, 0.001);
rel = hslider("release", 0.25, 0.02, 2, 0.001);
// 3-anchor vowel interpolation: Ah(0.0) Ee(0.5) Oo(1.0), LOG-interp (natural formant glide)
interp(v,a,b,c) = select2(v < 0.5, b*pow(c/b, (v-0.5)*2), a*pow(b/a, v*2));
F1 = interp(vowel, 730, 270, 300);
F2 = interp(vowel, 1090, 2290, 870);
F3 = interp(vowel, 2440, 3010, 2240);
vib = 1 + vibrato*os.osc(vibrate);
env = en.adsr(att, 0.2, 0.85, rel, gate);
src = (os.sawtooth(freq*vib) + no.noise*breath*0.5) * env;
fmt(fc,q,g) = fi.resonbp(fc, q, g);
vox = src <: fmt(F1,11,1.0) + fmt(F2,14,0.55) + fmt(F3,17,0.32);
// scale for polyphonic safety (chords sum) then tanh catches peaks (near-linear when quiet)
process = (vox * 0.30 * gain : ma.tanh) : fi.lowpass(2, 9000) <: _,_;
