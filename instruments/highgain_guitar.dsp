// highgain_guitar — tight, aggressive HIGH-GAIN metal rhythm guitar. A Karplus
// string with a SHARP bright pick-click, driven through an asymmetric high-gain
// clip cascade into a tight 4x12 cab. Serves metalcore / death / black / post-metal
// — palm-muted chugs + tremolo riffs. Play power chords (root-5-octave) as NOTES.
// TIGHT not boomy: less sub than fuzz, highpassed low, controllable decay.
//   drive 0..1  = edge -> full brutality (a touch hotter than fuzz)
//   mute  0..1  = palm-mute: BOTH shortens string decay AND darkens (post lowpass)
//   mids -1..1  = <0 SCOOP ~1k (Florida death) / >0 BUMP ~1k (Swedish buzzsaw)
import("stdfaust.lib");
freq  = hslider("freq", 82, 20, 2000, 0.001);
gain  = hslider("gain", 0.6, 0, 1, 0.01);
gate  = button("gate");
drive = hslider("drive", 0.85, 0, 1, 0.01);
mute  = hslider("mute", 0.0, 0, 1, 0.01);        // palm-mute: shorter + darker
mids  = hslider("mids", 0.0, -1, 1, 0.01);       // <0 scoop 1k / >0 buzzsaw bump 1k
sus   = hslider("sustain", 0.995, 0.98, 0.9985, 0.0001);

// pick excitation (drives the string) + a SHARPER, BRIGHTER click on top of onset
exc   = no.noise * en.ar(0.001, 0.008, gate);
click = (no.noise : fi.highpass(2, 2600)) * en.ar(0.0004, 0.005, gate) * 0.6;

// palm-mute wiring: lower feedback gain (faster decay) + darker string damping
sus_e = sus - mute * 0.06;
damp  = (3200 + 3000 * (1 - mute)) * max(0.12, gate);
str   = exc : (+ : de.fdelay(4096, ma.SR / freq - 2)) ~ (fi.lowpass(1, damp) : *(sus_e));

// asymmetric high-gain clip cascade (a bit hotter than fuzz; +bias = even harmonics)
g        = 3.0 + drive * 21.0;
stage(x) = ma.tanh(x * g + 0.12) : fi.highpass(1, 70);   // clip + inter-stage DC block
dist     = (str + click) : stage : stage : stage;

// mid voicing: bipolar parametric @1k — mids<0 SCOOP (Florida death),
// mids>0 BUMP (Swedish buzzsaw). peak_eq level is in dB, so this is a true cut/boost.
voiced(x) = x : fi.peak_eq(mids * 10, 1000, 800);
// fixed presence: the metal "bite" lives 2.5-3.5k -> mid-forward, aggressive
pres(x)   = x + 2.0 * (x : fi.resonbp(3000, 1.3, 1.0));

// tight cab: mute-tracked lowpass (darker when muted) + fizz tame + TIGHT highpass
plp     = 6900 - mute * 3600;
cab(x)  = x : fi.lowpass(2, plp) : fi.lowpass(3, 6600) : fi.highpass(3, 120);
process = dist : voiced : pres : cab : *(gain * 0.12) <: _,_;
