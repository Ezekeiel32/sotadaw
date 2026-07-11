// organ_soul — drawbar organ (Hammond lineage): sine stack at classic footages,
// one-shot percussion harmonic on the attack, slow rotary tremolo. Gospel/soul glue.
// zones (inits = the original constants): sub/body/sparkle = drawbar GROUP scales
// (16' | 8'+5 1/3'+4' | 2 2/3'+2'+1'), perc = percussion level, rotary = wobble
// depth, speed = rotary rate Hz.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.6, 0, 1, 0.01);
gate = button("gate");
subL    = hslider("sub", 1, 0, 2, 0.01);
bodyL   = hslider("body", 1, 0, 2, 0.01);
sparkle = hslider("sparkle", 1, 0, 2, 0.01);
percL   = hslider("perc", 0.35, 0, 1, 0.01);
rotd    = hslider("rotary", 0.13, 0, 0.5, 0.01);
rots    = hslider("speed", 5.7, 0.5, 8, 0.1);
env   = en.adsr(0.004, 0.05, 0.95, 0.08, gate);
perc  = en.adsr(0.002, 0.35, 0.0, 0.05, gate);        // Hammond percussion: decays while held
rot   = 1.0 + rotd * os.osc(rots);                    // rotary-ish amp wobble
drawbars = os.osc(freq * 0.5) * 0.45 * subL           // 16'
         + ( os.osc(freq)       * 1.0                 // 8'
           + os.osc(freq * 1.5) * 0.45                // 5 1/3'
           + os.osc(freq * 2.0) * 0.55 ) * bodyL      // 4'
         + ( os.osc(freq * 3.0) * 0.30                // 2 2/3'
           + os.osc(freq * 4.0) * 0.28                // 2'  (gospel sparkle lives up here)
           + os.osc(freq * 8.0) * 0.15 ) * sparkle;   // 1'
tone  = drawbars / 3.18 * env + os.osc(freq * 4.0) * perc * percL;
process = tone * rot * gain <: _,_;
