// chip_noise — the NES/SID noise channel: band-filtered pseudo-random noise for 8-bit
// drums & hats. `freq` maps to the band center (low=snare/tom, high=hat); `metal`
// narrows the band (short-LFSR 'pitched/metallic' vs long-LFSR 'white'). Env is a
// one-shot hit — hold notes longer for noise sweeps/risers.
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 8000, 0.001);   // noise band center
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
decay = hslider("decay", 0.12, 0.01, 1.5, 0.001);
metal = hslider("metal", 0.3, 0, 1, 0.01);       // 0=white, 1=narrow/pitched
tone  = hslider("tone", 9000, 800, 16000, 1);
env = en.ar(0.001, decay, gate);
q   = 0.6 + metal*18;                            // band Q
src = no.noise : fi.resonbp(freq, q, 1.0);
process = src * env * gain * 0.5 : fi.lowpass(2, tone) <: _,_;  // headroom law: A5 band-center bump clipped 24 (register court 2026-07-31)
