// hammond_organ — drawbar organ (soul-jazz / hard-bop). Additive sine drawbars
// at the classic footages, a brief KEY-CLICK transient on attack, and a LESLIE
// rotating-speaker effect (amplitude tremolo + Doppler pitch wobble + chorus).
// Organ envelope: near-instant attack, full sustain while held, quick release.
// zones: freq, gain, gate, sub16 (low drawbars), bright (upper drawbars),
//        click (key-click level), leslie (rotary depth).
import("stdfaust.lib");
freq   = hslider("freq", 220, 20, 4000, 0.001);
gain   = hslider("gain", 0.5, 0, 1, 0.01);
gate   = button("gate");
sub16  = hslider("sub16", 1, 0, 2, 0.01);     // 16' + 5 1/3' low drawbars
bright = hslider("bright", 1, 0, 2, 0.01);    // 2 2/3' + 2' upper drawbars
click  = hslider("click", 0.4, 0, 1, 0.01);   // key-click transient level
leslie = hslider("leslie", 0.5, 0, 1, 0.01);  // rotary-speaker depth

// classic Hammond drawbar footages — sub16 scales lows, bright scales uppers
drawbars = os.osc(freq*0.5)*0.50*sub16      // 16'
         + os.osc(freq*1.5)*0.30*sub16      // 5 1/3'
         + os.osc(freq*1.0)*1.00            // 8'  (fundamental, always on)
         + os.osc(freq*2.0)*0.55            // 4'
         + os.osc(freq*3.0)*0.30*bright     // 2 2/3'
         + os.osc(freq*4.0)*0.26*bright;    // 2'

// organ envelope: fast attack, full sustain while held, quick release (no decay-while-held)
env  = en.adsr(0.004, 0.01, 1.0, 0.03, gate);

// KEY-CLICK: a brief bright noise transient stacked on the attack
clik = no.noise * en.ar(0.0004, 0.007, gate) : fi.highpass(1, 900) : *(click*0.5);

// dry organ tone (drawbars staged down + click) — computed once, split inside
// leslize. 0.20 keeps a single note ~-12 dBFS so a 4-note chord stays under 0.
dry  = drawbars*0.20*env + clik;

// LESLIE rotating speaker: one ~6.6 Hz rotor drives amplitude tremolo (AM),
// a modulated delay (Doppler pitch wobble + chorus depth), and their blend.
leslize(x) = wet * trem
with {
    lfo  = os.osc(6.6);
    vib  = x : de.fdelay(1024, 14 + 9*leslie*(0.5 + 0.5*lfo));  // Doppler / chorus
    wet  = x*(1.0 - 0.45*leslie) + vib*(0.45*leslie);
    trem = 1.0 + 0.28*leslie*lfo;                               // amplitude modulation
};

// per-voice tanh safety so a 4-note held chord still sits under 0 dBFS
process = dry : leslize : *(gain) : ma.tanh <: _,_;
