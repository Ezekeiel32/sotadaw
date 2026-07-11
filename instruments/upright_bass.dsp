// upright_bass — acoustic double (upright) bass, PIZZICATO. The most-needed jazz
// voice: bebop/hard-bop/modal/spiritual WALKING bass. A Karplus-Strong string
// tuned LOW (the gut/steel string) + a fundamental sine (the low weight of the
// big body) + three summed low bandpass resonances (the wooden box) + a short
// filtered-noise finger/fingerboard attack (the pluck). Every note dies
// naturally: the amp ADSR has sustain=0 so it decays to silence over `decay`
// seconds — a real pizz note, never a hanging synth drone.
import("stdfaust.lib");
freq  = hslider("freq", 55, 20, 2000, 0.001);
gain  = hslider("gain", 0.85, 0, 1, 0.01);
gate  = button("gate");
decay = hslider("decay", 1.0, 0.2, 3.0, 0.01);   // note length in seconds (pizz ring)
body  = hslider("body", 0.6, 0, 1, 0.01);        // wooden-body resonance amount
click = hslider("click", 0.5, 0, 1, 0.01);       // finger / fingerboard attack level

// the pluck: a short noise burst injected into the string loop
exc   = no.noise * en.ar(0.0004, 0.006, gate);
sus   = 0.992;                                    // string feedback sustain
damp  = 2400;                                     // in-loop damping = warm/dark string
str   = exc : (+ : de.fdelay4(8192, ma.SR/freq - 1)) ~ (fi.lowpass(1, damp) : *(sus));

// fundamental sine — the deep low weight of the resonating body (under the string)
sub   = os.osc(freq);

// wooden body: three resonant peaks spanning low..low-mid = the warm woody box
bodyres(x) = x <: fi.resonbp(75, 9, 1.0), fi.resonbp(140, 7, 0.95), fi.resonbp(240, 5, 0.65) :> _;

// finger / fingerboard attack: a short broadband noise click (the pluck snap)
clik  = no.noise * en.ar(0.0003, 0.015, gate) : fi.highpass(1, 700) : fi.lowpass(2, 3200) : *(click*0.6);

// pizz amp envelope: sustain=0 => the note decays to silence over `decay`
aenv  = en.adsr(0.003, decay, 0.0, 0.06, gate);

voice = ((sub*0.35 + str*1.0 + bodyres(str)*body) + clik) * aenv;
process = voice : fi.lowpass(3, 2700) : *(gain*0.5) <: _,_;
