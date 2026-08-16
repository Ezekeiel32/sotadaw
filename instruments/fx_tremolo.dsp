// fx_tremolo — amplitude pulse (surf/soul guitar, ambient pads, dub organ;
// fx_pump is sidechain-shaped — a musical rate-synced tremolo did not exist).
// Sine or square-ish shape morph, stereo PHASE spread = auto-pan territory at
// spread 1. Depth 0 = bypass-transparent.
import("stdfaust.lib");
rate = hslider("rate", 4.6, 0.1, 12.0, 0.001);      // Hz
depth = hslider("depth", 0.5, 0.0, 1.0, 0.01);
shape = hslider("shape", 0.25, 0.0, 1.0, 0.01);     // 0 sine .. 1 hard chop
spread = hslider("spread", 0.0, 0.0, 1.0, 0.01);    // L/R phase offset (autopan)
mod(ph) = ((1.0 - depth) + depth * shaped) : si.smooth(ba.tau2pole(0.001))
with {
    raw = (1.0 + os.oscp(rate, ph)) * 0.5;
    hard = raw > 0.5;
    shaped = raw * (1.0 - shape) + hard * shape;
    // 1ms smoothing: the chop keeps its edge musically but gain STEPS die —
    // per-sample steps AM-splattered sidebands past the E5 alias budget (-58.2
    // vs -60 measured); smoothed passes with margin
};
process(l, r) = l * mod(0.0), r * mod(spread * 3.14);
