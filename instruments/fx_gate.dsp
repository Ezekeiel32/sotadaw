// fx_gate — downward expander / noise gate (bleed + floor control for recorded stems).
// Linked-stereo key (max of both sides' envelopes, 2ms attack / `rel` release):
// level UNDER `thresh` is expanded down 3:1, capped at `depth` dB of attenuation —
// depth 0 = bit-transparent bypass, depth 60 ~= hard gate. Imported stems keep
// their takes' air between phrases without carrying the room's hum and bleed.
// Stereo-through contract.
import("stdfaust.lib");
thresh = hslider("thresh", -45, -70, 0, 0.5);
depth  = hslider("depth", 24, 0, 60, 0.5);
rel    = hslider("rel", 0.12, 0.02, 1.0, 0.005);

process = _,_ : gt
with {
    gt(l, r) = l * g, r * g
    with {
        env = max(abs(l), abs(r)) : an.amp_follower_ud(0.002, rel);
        lvl = ba.linear2db(env + 1e-9);
        gr  = min(depth, max(0.0, thresh - lvl) * 2.0);
        g   = ba.db2linear(0.0 - gr) : si.smoo;
    };
};
