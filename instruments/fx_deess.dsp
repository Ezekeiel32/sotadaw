// fx_deess — split-band sibilance tamer (the vocal chain's missing dynamics tool).
// Complementary split at `freq`: lo = 3rd-order lowpass, hi = x - lo (PERFECT
// reconstruction — under threshold the fx is bit-transparent by construction).
// The high band rides a linked stereo envelope (0.8ms attack / 60ms release):
// level over `thresh` is reduced 4:1, capped at `amount` dB of max GR. Lows are
// never touched — esses duck, the voice's body stays. Stereo-through contract.
import("stdfaust.lib");
freq   = hslider("freq", 6500, 3000, 11000, 1) : si.smoo;
thresh = hslider("thresh", -32, -60, 0, 0.5);
amount = hslider("amount", 12, 0, 24, 0.5);

process = _,_ : de
with {
    de(l, r) = (lol + hil * g), (lor + hir * g)
    with {
        lol = l : fi.lowpass(3, freq);
        lor = r : fi.lowpass(3, freq);
        hil = l - lol;
        hir = r - lor;
        key = (hil + hir) * 0.5 : an.amp_follower_ar(0.0008, 0.06);
        lvl = ba.linear2db(key + 1e-9);
        gr  = min(amount, max(0.0, lvl - thresh) * 0.75);
        g   = ba.db2linear(0.0 - gr) : si.smoo;
    };
};
