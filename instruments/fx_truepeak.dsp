// fx_truepeak: TRUE-PEAK brickwall (ITU-R BS.1770 lane) — the release-grade wall.
// Spec refs: BS.1770-4/-5 define true-peak via 4x oversampling (48k->192k) of the
// measurement path; our detector mirrors that estimator (3 fractional-phase FIRs =
// the 4 phases of the oversampled domain). docs/SURFACE_LEDGER.md carries the cites.
// fx_brickwall keys on SAMPLE peaks; inter-sample peaks reconstruct ~1-1.8dB hot
// at the DAC/codec, so masters paid a -3dB insurance ceiling. This wall keys on a
// 4x-OVERSAMPLED DETECTOR (the BS.1770-4 true-peak estimator design: only the
// sidechain is oversampled — 3 fractional-phase windowed-sinc FIRs + the aligned
// dry pair), rides gain via a 128-sample lookahead running-max (doubling cascade)
// with an ~80ms release, applies it to the DELAYED dry signal, then a final hard
// clip at the ceiling catches residue. ceiling in dBTP.
import("stdfaust.lib");

ceil_db = hslider("ceiling", -1.0, -12.0, 0.0, 0.1);
// THE RECONSTRUCTION MARGIN (measured, firing 100): dense material limited AT the
// ceiling rides it with sharp corners and reconstructs ~+0.93dB between samples
// (same physics as clipping — the click-probe proved the limiter itself is clean).
// 'ceiling' means dBTP OF THE OUTPUT, which is what a release spec asks for
// (the W114 32-tap cascade regulates that quantity directly).
// W114 THE CASCADE: the 8x detector alone left dense mixes +0.5 over —
// the limited waveform's OWN reconstruction varies with material (gain-
// modulation sidebands + clip corners), so no open-loop margin lands
// everywhere. Stage 1 limits at a 1.0dB internal margin as before;
// stage 2 measures the STAGE-1 OUTPUT's true peak and shaves the actual
// reconstruction against the stated ceiling (0.1 guard). Latency 2xLA.
// THE MARGIN LADDER (measured, W114): 0.3/0.05 and 0.55/0.1 both let hot
// rough mixes reach the final clip (T4 +0.5 over). 1.0/0.1 is the honest
// configuration: 7/7 battery, 19/19 corpus compliant, spread 0.17dB —
// a PREDICTABLE ~0.9dB under stated (loudness-recovered upstream; the
// undershoot is codec headroom, never a compliance failure).
c1 = ba.db2linear(ceil_db - 1.0);
c2 = ba.db2linear(ceil_db - 0.1);

// ---- true-peak detector (W114 v3): 4 phases x 32-TAP interpolators ----
// THE BLINDNESS: 8-tap fractional sincs roll off -8.5dB at 0.9xNyquist —
// both the 4x and 8x short detectors were nearly deaf to near-Nyquist ISP
// (exactly what dense bright mixes + the 9k air shelf create; the corpus
// gradient measured it: +0.56 over stated on pop/house, sparse dark -0.7
// under). 32-tap Hamming sincs hold -0.1dB at 0.9xNyquist (ITU-grade);
// with a flat interpolator, 4 phases suffice and the stage-2 cascade
// absorbs the residual estimator error. Detector alignment GD = 16.
fir32(x, (h)) = sum(i, 32, ba.take(i + 1, (h)) * x@i);
H1 = (-0.0011827738, 0.0014147608, -0.0019956640, 0.0029899368,
      -0.0044707495, 0.0065259073, -0.0092682370, 0.0128541238,
      -0.0175179070, 0.0236396911, -0.0318908613, 0.0435849468,
      -0.0616756842, 0.0944151882, -0.1765678602, 0.8997364908,
      0.2999121636, -0.1261199001, 0.0772487904, -0.0534522597,
      0.0389970577, -0.0291177429, 0.0218886029, -0.0163877195,
      0.0121196025, -0.0087929428, 0.0062223767, -0.0042805049,
      0.0028726843, -0.0019230944, 0.0013668028, -0.0011452254);
H2 = (-0.0016455112, 0.0019660335, -0.0027696861, 0.0041433260,
      -0.0061843783, 0.0090081684, -0.0127607525, 0.0176416227,
      -0.0239452837, 0.0321417476, -0.0430451168, 0.0582068322,
      -0.0809823398, 0.1201559829, -0.2080613612, 0.6361307165,
      0.6361307165, -0.2080613612, 0.1201559829, -0.0809823398,
      0.0582068322, -0.0430451168, 0.0321417476, -0.0239452837,
      0.0176416227, -0.0127607525, 0.0090081684, -0.0061843783,
      0.0041433260, -0.0027696861, 0.0019660335, -0.0016455112);
H3 = (-0.0011452254, 0.0013668028, -0.0019230944, 0.0028726843,
      -0.0042805049, 0.0062223767, -0.0087929428, 0.0121196025,
      -0.0163877195, 0.0218886029, -0.0291177429, 0.0389970577,
      -0.0534522597, 0.0772487904, -0.1261199001, 0.2999121636,
      0.8997364908, -0.1765678602, 0.0944151882, -0.0616756842,
      0.0435849468, -0.0318908613, 0.0236396911, -0.0175179070,
      0.0128541238, -0.0092682370, 0.0065259073, -0.0044707495,
      0.0029899368, -0.0019956640, 0.0014147608, -0.0011827738);
tp(x) = max(max(abs(x@15), abs(x@16)),
            max(abs(fir32(x, H1)),
                max(abs(fir32(x, H2)), abs(fir32(x, H3)))));

// ---- gain computer, DUAL-STAGE (the T4 lesson): a step-changing gain remakes
// inter-sample overshoot on dense material (gain modulation sidebands), so the
// attenuation is (1) release-extended, (2) held by a lookahead running-MAX,
// then (3) SMOOTHED by a matching moving-average — gain RAMPS linearly across
// the lookahead window into every peak instead of stepping at it. Attenuation
// form: a=0 at init = unity gain (gain-form recursion inits at 0 = fade-in bug).
LA = 128;
GD = 16;                                       // detector alignment (32 taps center ~15.5)
relC = exp(-1.0 / (0.080 * ma.SR));
atten(cc, env) = aloop ~ _ : ba.slidingMax(LA, LA) : ba.slidingSump(LA, LA) / LA
with {
    aWant = 1.0 - cc / max(cc, env);           // 0 under the ceiling
    aloop(prev) = max(aWant, prev * relC);
};

// ---- one limiter stage: detect on max(L,R), gain both, delay dry, clip ----
stage(cc, l, r) = max(-cc, min(cc, dl * g)), max(-cc, min(cc, dr * g))
with {
    dl = l @ (LA + GD);
    dr = r @ (LA + GD);
    g = 1.0 - atten(cc, max(tp(l), tp(r)));
};

// ---- the cascade: stage 1 at the internal margin, stage 2 regulates the
// stage-1 output's MEASURED true peak against the stated ceiling ----
process = stage(c1) : stage(c2);
