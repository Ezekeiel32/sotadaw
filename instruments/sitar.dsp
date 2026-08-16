// sitar — Indian long-neck lute (bollywood_filmi/raga/psychedelia; 184
// never-briefed genres include the whole Indian family and NO sitar existed).
// The identity is threefold: the JAWARI bridge (grazing buzz = gentle
// saturation of the string against a curved bridge), SYMPATHETIC strings
// (a bank of high-Q resonators tuned to scale degrees, rung by the main
// string — the shimmer that hangs after every note), and the meend-friendly
// long sustain. chikari drone hits = just play the high tonic staccato.
// ZONE-ENRICHED (face law): jawari/sympathy agent-tweakable.
import("stdfaust.lib");
freq = hslider("freq", 261, 80, 1500, 0.1);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
jawari = hslider("jawari", 0.5, 0, 1, 0.01);    // bridge buzz amount
sympathy = hslider("sympathy", 0.5, 0, 1, 0.01); // sympathetic bank level

burst = no.noise * en.ar(0.0005, 0.004, gate);
n = ma.SR / max(80.0, freq);
pluckdel = max(1.0, n * 0.12);
damphz = (5200.0 + 3000.0) * (0.65 + 0.35 * gain);  // vel = pluck force
excite = burst : (_ <: _, @(int(pluckdel)) :> _ - _) * 0.5
       : fi.lowpass(2, damphz);
loopfilter = fi.lowpass(1, damphz) * 0.9975;         // long singing sustain
string = (+ : de.fdelay4(4096, max(2.0, n - 2.0))) ~ loopfilter;
// jawari: the string grazes a curved bridge — asymmetric soft saturation,
// drive scaled DOWN so the buzz stays a sheen, never fuzz
buzzed(x) = x * (1.0 - jawari * 0.5) + ma.tanh(x * (1.5 + jawari * 2.5)) * jawari * 0.45;
// sympathetic bank: 5 high-Q strings at scale-ish intervals ring with the note
symp = _ <: fi.resonbp(freq * 1.5, 90, 0.3), fi.resonbp(freq * 2.0, 90, 0.3),
            fi.resonbp(freq * 2.25, 90, 0.22), fi.resonbp(freq * 3.0, 90, 0.2),
            fi.resonbp(freq * 1.125, 90, 0.2) :> _ * sympathy * 0.7;
raw = excite : string : buzzed;
process = (raw + (raw : symp)) * gain * 0.36 <: _, _;  // headroom law: A5 sympathetic-bank sum cleared (register court)
