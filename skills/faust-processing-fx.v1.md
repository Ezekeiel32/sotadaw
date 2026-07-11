---
name: faust-processing-fx
version: 1
kind: sound-design
tags: [faust, fx, mixing, mastering, amp, tape, vinyl, vocoder, reverb, compressor, delay, spatial, cookbook]
hard_constraints:
  - FX are stereo-through: `process = _,_ : ... : _,_;`. Stage levels with fx_trim (dB), NEVER by normalizing output.
  - Cascaded static nonlinearities (amp/saturation/wavefold) MUST be oversampled 4-8x + anti-aliased; Faust does NOT auto-insert AA.
  - Build via write_instrument (JIT compiles instantly). Reuse skills/faust-reusable-blocks (fx_tape/fx_lofi/fx_ensemble/fx_leslie) rather than reinventing.
  - The CORRECTION LAWS below are adversarially verified (docs/research_sound_foundry_ii.md) and OUTRANK common knowledge.
---
# The processing studio (Slice E) -- amp/cab/pedal · tape/vinyl · vocoder · reverb · dynamics · delays/spatial

The whole mix+master FX rack as inspectable Faust. Faust's stdlib does most of the work (co.lib
dynamics, re.lib reverbs, de.lib/hoa.lib/spats.lib delays+spatial, tonestacks.lib/wdmodels.lib amp).
Assume `import("stdfaust.lib");`. Full per-item DNA + sources: docs/research_sound_foundry_ii.md.

## Guitar/bass amp + cab + pedal (fx_amp + pedals)
Chain: `fi.dcblocker -> input gain -> [pedals] -> tube preamp stages -> tone stack -> power-amp/sag -> cab`.
- Tube stage = `ma.tanh(drive*x)` (odd) or `ef.cubicnl(drive,offset)` (asymmetry -> EVEN harmonics; `fi.dcblocker` after). OVERSAMPLE 4-8x.
- Tone stack = tonestacks.lib Fender/Marshall/Vox biquads. Diode clippers = wdmodels.lib WDF.
- Cab = `soundfile` partitioned-IR convolution (real speaker IR) OR a biquad/modal cab to stay pure-Faust.
- Overdrive (Tube Screamer): pre-EQ mid bump ~720Hz -> `ma.tanh` soft clip. Or `ve.klonCentaur(gain,treble,level)`.
- **LAW: the Tube Screamer's ~720Hz corner is a HIGH-PASS (bass cut) in the clipping feedback, NOT a low-pass** -- frequencies ABOVE 720Hz get the gain.
- Fuzz (Big Muff/Fuzz Face) = cascaded hard clip `min/max`. Wah = swept `fi.resonbp`. Chorus/phaser/flanger = modulated de.fdelay / allpass.

## Tape / vinyl / cassette (fx_tape_deep -- deepens reusable block #3)
- Wow/flutter = incommensurate + PER-INSTANCE-SEEDED modulated `de.fdelay` (the minted tape block).
- Record saturation = anhysteretic Langevin S-curve + one `fi.pole` memory (fakes hysteresis lag). Full Jiles-Atherton (RK4/Newton in a `~` loop, 16x OS) is the optional hard tier.
- Vinyl crackle = Poisson `no.sparse_noise` impulses shaped; hiss/rumble = filtered `no.noise`; RIAA + head-bump + inner-groove HF-loss = biquads; LR mono-bass split (fx_ms_eq pattern).
- Verified vs DAFx-19 Chowdhury: Jiles-Atherton M_s=3.5e5, k=27kA/m, a=22kA/m, c=0.17; playback gap-loss FIR.

## Vocoder / talkbox / formant (fx_vocoder)
- `ve.vocoder(N, att, rel, BWRatio)` fed (modulator, carrier). N=16 classic / 20 Kraftwerk; att~0.005, rel~0.05, BWRatio~0.8.
- Carrier = reuse the analog-drift/unison saw stack (block #11) or FM-op (#7) or wavetable (#8) or a live synth bus.
- **ADD the sibilance path ve.vocoder LACKS:** `sib = modulator : fi.highpass(2,8000) : *(sibGain);` sum in = intelligibility.
- Talkbox = formant `fi.resonbp` vowel bank on the carrier. Formant-shift/gender-bend = scale the vowel centre freqs.
- LAW: top band centre = 12.8kHz; ~8.4-octave centre span at N=16.

## Reverb spaces (fx_plate / fx_jpverb / fx_spring / fx_shimmer / fx_gated / fx_reverse)
Wrap re.* -- do NOT reinvent:
- Algorithmic (extend existing fx_reverb): `re.zita_rev1_stereo`. Lush Lexicon = `re.jpverb`; modulated echo = `re.greyhole`.
- Plate = `re.dattorro_rev(predelay, 0.9995, ...)`. Jot band-split FDN = `re.fdnrev0(MAXDELAY, [coprime delays], ...)`.
- Spring = cascaded DISPERSIVE allpass chain (the boingy chirp). Shimmer = pitch-shift (+12) INSIDE the feedback path.
- Gated = reverb * noise-gate envelope (80s snare). Reverse = `rwtable` read-backwards, windowed.
- **LAW: the printed Stautner-Puckette 4x4 feedback matrix [[0,1,1,0],[-1,0,1,0],[-1,0,0,-1],[1,0,0,-1]] is NOT orthogonal** (row1.row2=1) -> use the correct JOS unitary matrix or the tail mistunes.

## Saturation & dynamics character (fx_1176 / fx_la2a / fx_fairchild / fx_ssl / fx_dbx160 + fx_tube/tape/xfmr/console)
All pure Faust (co.lib + ef.lib + ma.tanh) -- BEHAVIORAL wrappers, not SPICE:
- Core = `co.compressor_mono` / `co.limiter` with Giannoulis quadratic soft-knee `(L-thresh+knee/2)^2/(2*knee)`.
- CHARACTER = program-dependent ballistics: LA-2A opto two-stage memory release; SSL dual-RC auto-release; 1176 fast-FET + post-transient ratio creep; dbx160 Over-Easy knee; Fairchild vari-mu (M/S).
- Harmonic bloom = level-tracking drive: `an.amp_follower(t) -> ma.tanh`. Transformer = pre-tilt lows INTO the nonlinearity.
- Odd (tape/pentode) = symmetric `ma.tanh(drive*x)/ma.tanh(drive)`; even (tube) = asymmetry `ef.cubicnl(drive,offset)` + `fi.dcblocker`.
- Transient shaper (SPL) = attack/sustain independent of level via fast/slow `an.amp_follower` difference.

## Creative delays & spatial/immersive (fx_tapeecho / fx_pingpong / fx_pitchdelay + fx_width / fx_binaural / fx_ambi)
- Digital delay = `+~( de.sdelay(maxN, it, d) : fi.lowpass(1,cutoff) : *(fb) )` -- de.sdelay (no zipper) for tempo-sync, de.fdelay for smooth time sweeps. DERIVE times from the song tempoMap, never hardcode.
- Tape echo (RE-201) = de.fdelay + tape saturation + wow/flutter + filtered feedback + spring. **LAW: MN3005 BBD 204.8ms is at the SLOWEST clock; delay=N/(2*fc), raising the clock SHORTENS it.**
- Ping-pong = two cross-coupled lines, hard-pan A left / B right, `fi.lowpass` in each feedback.
- Haas = short (<25ms) one-side de.delay. M/S width = (mid,side) matrix + side gain (mono-bass below x).
- Synthetic binaural = ITD (de.fdelay) + ILD (head-shadow lowpass) -- ship this pure-Faust DEFAULT; true HRTF = optional partitioned-FFT convolution of a measured HRIR set (IRCAM LISTEN / MIT-KEMAR).
- Ambisonics = `hoa.lib` B-format encode -> rotate -> decode (head-tracked / Atmos orbit-pan).

Companions: faust-reusable-blocks (the 11+ blocks these reuse), fx-usage (bus placement), mastering,
mix-headroom, automation-motion (dub-throw / reverse-swell / auto-width / Ambisonic-orbit templates).
