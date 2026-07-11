// ep_bright (W83) — the mid-register bed voice the spectrum map proved
// missing: every existing keys/pad voice at a C4 chord parks 60-99% of its
// energy BELOW 500Hz (jazz_piano 80% lowmid, keys_dark 99%); the only
// mid-fillers were vox timbres. This is a bright FM tine EP: sine carrier +
// enveloped 7x tine burst + 2nd-harmonic body — the classic electric piano
// spectrum whose 2nd-4th harmonics land squarely in 500-2k from C4.
// Structural headroom: 0.34 sum scale holds vel-1.0 chords under 0dBFS.
// zones: tine = attack burst level, body = 2nd-harmonic level,
//        bell = tine ratio brightness, decay = amplitude decay s
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.5, 0, 1, 0.01);
gate = button("gate");
tine  = hslider("tine", 0.7, 0, 1.5, 0.01);
body  = hslider("body", 0.55, 0, 1, 0.01);
bell  = hslider("bell", 7.0, 2, 12, 0.1);
decay = hslider("decay", 1.4, 0.2, 4, 0.01);
tenv  = en.ar(0.001, 0.09, gate);
aenv  = en.adsr(0.002, decay, 0.25, 0.25, gate);
mod   = os.osc(freq * bell) * tenv * tine;
car   = os.osc(freq + mod * freq * 0.9);
h2    = os.osc(freq * 2.001) * body;
h3    = os.osc(freq * 3.003) * body * 0.35;
process = ((car + h2 + h3) * aenv * 0.34) * gain <: _,_;
