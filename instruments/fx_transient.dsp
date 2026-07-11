// fx_transient — transient shaper (SPL-style differential envelopes; the rack
// had no attack/sustain tool). Two follower pairs on a LINKED peak key:
//   attack detector  = fast-attack env over slow-attack env (positive ~25ms at onsets)
//   sustain detector = slow-release env over fast-release env (positive in tails)
// Each detector's dB excess (normalized at 6 dB) scales its knob: attack +/-12 dB
// shapes the hit, sustain +/-12 dB shapes the ring/room. Both at 0 = unity gain
// by construction. Punch: attack +6..9, sustain -4. Roomier: sustain +6.
// Stereo-through contract.
import("stdfaust.lib");
attack  = hslider("attack", 0, -12, 12, 0.1);
sustain = hslider("sustain", 0, -12, 12, 0.1);

process = _,_ : sh
with {
    sh(l, r) = l * g, r * g
    with {
        key = max(abs(l), abs(r));
        fa  = key : an.amp_follower_ud(0.0005, 0.06);
        sa  = key : an.amp_follower_ud(0.025, 0.06);
        da  = max(0.0, ba.linear2db(fa + 1e-9) - ba.linear2db(sa + 1e-9));
        fr  = key : an.amp_follower_ud(0.001, 0.03);
        sr_ = key : an.amp_follower_ud(0.001, 0.35);
        ds  = max(0.0, ba.linear2db(sr_ + 1e-9) - ba.linear2db(fr + 1e-9));
        gdb = attack * min(1.0, da * 0.166667) + sustain * min(1.0, ds * 0.166667);
        g   = ba.db2linear(gdb);
    };
};
