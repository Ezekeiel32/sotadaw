// fx_comp — THE channel compressor (full-band, stereo-linked, makeup).
// The rack's multiband sibling (fx_multiband) covers mastering; THIS is the
// track/bus glue. Explicit gain computer (NOT co.compressor_stereo — the legacy
// lib detector sums L+R, reading correlated material +6 dB hot so thresholds
// lie): linked key = max of both sides' peak envelopes (att/rel in ms), honest
// N:1 above `thresh` dB, makeup post. ratio 1 = 0 dB GR by construction = bypass.
// NOTE: {"type":"comp"} (Tracktion built-in) has DEAD friendly-param wiring —
// its native ratio is 1/N clamped to [0.05,1], so JSON "ratio":4 lands as 1:1
// (verified by render probe 2026-07-10). Use fx_comp until SongLoader converts.
// Stereo-through contract.
import("stdfaust.lib");
thresh = hslider("thresh", -24, -60, 0, 0.5);
ratio  = hslider("ratio", 3, 1, 20, 0.1);
att    = hslider("attack", 10, 0.1, 120, 0.1) * 0.001;   // ms -> s
rel    = hslider("release", 150, 20, 800, 1) * 0.001;    // ms -> s
mkup   = hslider("makeup", 0, -12, 24, 0.1) : ba.db2linear : si.smoo;

process = _,_ : cp
with {
    cp(l, r) = l * g * mkup, r * g * mkup
    with {
        env  = max(abs(l), abs(r)) : an.amp_follower_ud(att, rel);
        lvl  = ba.linear2db(env + 1e-9);
        gr   = max(0.0, lvl - thresh) * (1.0 - 1.0 / ratio);
        g    = ba.db2linear(0.0 - gr);
    };
};
