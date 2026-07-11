// sine_siren — the automotivo/bruxaria TUIN: a bare sine that TRACKS PITCH and
// GLIDES into every note (the sliding octave blip). test_sine (constant 440 Hz
// validator, no zones) was standing in for this voice and rendered the whole
// genre as a static drone — this is the real organ. `glide` is the portamento
// the siren slides on; `bite` adds the faint square edge the funk carioca rigs
// get from driving cheap DACs; drop=octave-up attack blip settling to pitch.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.7, 0, 1, 0.01);
gate = button("gate");
glide   = hslider("glide", 0.045, 0.0, 0.3, 0.001);      // portamento seconds
bite    = hslider("bite", 0.12, 0, 0.6, 0.001);          // square-edge blend
drop    = hslider("drop", 0.35, 0, 1, 0.01);             // attack blip depth (up)
droptime= hslider("droptime", 0.05, 0.005, 0.3, 0.001);
vibrato = hslider("vibrato", 0.0, 0, 0.03, 0.0001);
vibrate = hslider("vibrate", 5.5, 0, 9, 0.01);
env   = en.adsr(0.002, 0.05, 0.85, 0.06, gate);
fslid = freq : si.smooth(ba.tau2pole(glide));            // the slide itself
pdrop = drop * en.ar(0.001, droptime, gate);             // 1 -> 0 fast, pitched UP
vib   = 1 + vibrato * os.osc(vibrate);
f2    = fslid * (1 + pdrop) * vib;
sq    = (os.lf_sawpos(f2) < 0.5) - 0.5;
tone  = os.osc(f2) * (1 - bite) + sq * 2 * bite;
process = tone * env * gain : *(0.86) <: _,_;  // headroom law: sine-dominant, 0 clipped @ vel 1.0
