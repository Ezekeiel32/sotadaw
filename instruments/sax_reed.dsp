import("stdfaust.lib");
// sax_reed — expressive SOLO saxophone: tenor <-> soprano (bright zone), Coltrane /
// Pharoah Sanders wail (growl overblow). A reed source (saw + sub-square) driven through
// a RICH formant body (4 sax-vowel peaks ~600/1050/2300/3200 Hz), late-blooming vibrato
// with a pitch SCOOP into the note, an onset breath burst + a continuous air layer under
// the tone. A CUTTING lead voice — energy concentrated in the mid + hi-mid.
//   bright 0->1 shifts the formant centres UP (tenor -> soprano) and opens the tone.
//   growl  0->1 overblows: octave harmonic + throat-flutter + tanh drive + noise = the snarl.
freq    = hslider("freq", 220, 20, 4000, 0.001);
gain    = hslider("gain", 0.6, 0, 1, 0.01);
gate    = button("gate");
vibrato = hslider("vibrato", 0.02, 0, 0.06, 0.0001);    // vibrato depth (blooms late)
breathA = hslider("breath", 0.08, 0, 0.3, 0.001);       // breath / air amount
growl   = hslider("growl", 0.0, 0, 1, 0.01);            // overblow snarl (the wail)
bright  = hslider("bright", 0.3, 0, 1, 0.01);           // tenor(0) <-> soprano(1)
att     = hslider("attack", 0.03, 0.005, 0.3, 0.001);
rel     = hslider("release", 0.14, 0.02, 1.0, 0.001);

env    = en.adsr(att, 0.12, 0.82, rel, gate);
scoop  = en.asr(0.06, 1.0, 0.06, gate);                 // rises 0->1 = scoop UP into pitch
vibdel = en.asr(0.30, 1.0, 0.10, gate);                 // vibrato blooms in late
f      = freq*(0.945 + 0.055*scoop)*(1.0 + vibrato*vibdel*os.osc(5.4));

fsh    = 0.82 + bright*0.66;                            // formant-shift factor
drive  = 1.0 + growl*4.0;                               // overblow tanh drive
fl     = 1.0 + growl*0.28*os.osc(52);                   // growl throat-flutter (AM)

reed   = (os.sawtooth(f) + os.square(f*0.5)*0.22 + os.sawtooth(f*2)*growl*0.18) * fl;
od     = (reed*drive : ma.tanh) : fi.highpass(1, 70);   // overblown reed

body(x) = x : fi.lowpass(2, 3200 + bright*3400) <:
    ( fi.resonbp(600*fsh,  2.4, 1.0)*0.7,
      fi.resonbp(1050*fsh, 2.8, 1.0)*1.2,
      fi.resonbp(2300*fsh, 3.4, 1.0)*1.05,
      fi.resonbp(3200*fsh, 4.2, 1.0)*(0.65 + growl*0.6),
      _*0.30 ) :> _*0.34;

grn     = no.noise * growl * 0.3 : fi.resonbp(2600, 1.5, 1.0);      // growl noise
breathN = no.noise : fi.resonbp(2000 + bright*1500, 1.8, 1.0);
onset   = breathN * en.ar(0.02, 0.22, gate) * breathA * 1.4;        // breath burst
airlow  = breathN * env * breathA * 0.45;                          // continuous air

voiced  = ((od : body) + grn) * 1.5;
process = (voiced*env + onset + airlow) : *(gain*0.3) <: _,_;
