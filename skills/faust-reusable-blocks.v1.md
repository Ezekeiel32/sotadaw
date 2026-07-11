---
name: faust-reusable-blocks
version: 1
kind: sound-design
tags: [faust, dsp, synthesis, cookbook, blocks, physical-modeling, analog, fm, wavetable, reference]
hard_constraints:
  - These are AUTHORING recipes. Build via write_instrument (JIT compiles instantly; .dsp edits re-JIT on mtime). Promote hot voices to AOT later (gen_faust.sh + rebuild).
  - Every voice still needs zones freq/gain/gate and ends `<: _,_` (see faust-writing). FX are stereo-through.
  - The CORRECTION LAWS here are adversarially verified (docs/research_sound_libraries_sota.md) and OUTRANK common knowledge. A wrong number makes the WRONG sound.
---
# Reusable DSP blocks -- build once, reuse everywhere

11 building blocks distilled from docs/research_sound_libraries_sota.md (31-agent deep research +
adversarial verify). Compose these instead of reinventing; each powers several legendary-gear voices.
Assume `import("stdfaust.lib");` (os./fi./ve./pm./de./ba./en./no./ma./si./ef./it. namespaces).

## 1. BBD chorus / ensemble -> fx_ensemble  (supersedes the single-LFO fx_widen)
Modulated fractional delay `de.fdelay/de.fdelay5` (~3ms nominal). JUNO mode: 2 lines, ONE triangle LFO
fed INVERTED to L/R (~0.5Hz Mode I / ~0.8Hz Mode II). SOLINA mode: 3 taps at 0/120/240 deg from two
rates (slow ~0.6Hz + fast ~6Hz, ~10:1), SHALLOW depth. BBD flavour = `fi.lowpass`~8kHz on the wet +
optional `ma.tanh` companding + faint `no.noise` floor. Failure mode = seasick vibrato: keep depth
shallow, phases correct. Reused by: analog-poly(4), string-machines(15).

## 2. Lo-fi degrade (bitcrush + decimate + reconstruction) -> fx_lofi
HARDWARE ORDER: `fi.lowpass(N,~15k)` anti-alias -> `ba.downSample(rate)` or `ba.sAndH` ZOH decimation
(LEAVE it un-anti-imaged = the brightness) -> `ba.bitcrusher(bits)` linear OR `ba.mulaw_bitcrusher(255,8)`
companded (EII/LM-1) -> 4-pole `ve.moog_vcf` reconstruction (SSM2044) OR omit for "bright" channels.
Drop-sample pitch = rdtable read with a TRUNCATED fractional increment (no interp). Presets: sp1200
26.04kHz/12-bit, eII 27.7kHz/mu-law, mpc60 40kHz/12-bit. Reused by: lo-fi(3), drum-machines(1), PPG(6), tape(11).
LAW: EII = INSTANTANEOUS mu-law (AM6072), NOT DPCM. SP grit = OUTPUT imaging + drop-sample repitch, NOT 12-bit quantization (that is ~72dB down, faint).

## 3. Tape wow/flutter + dropout + hiss -> fx_tape
`de.fdelayNa`/`de.sdelay`, d = d0 + depth*(`os.lf_triangle`(wow~0.7Hz) + `os.lf_triangle`(flutter~8Hz)
+ lowpassed `no.noise`) with INCOMMENSURATE periods and PER-VOICE decorrelated phase/seed -- the key to
NOT collapsing into a clean chorus. Then `ma.tanh` + `fi.peak_eq` head-bump (~80-120Hz) + HF rolloff
~9kHz. Dropout = `ba.sAndH(no.noise)` on a slow clock shaped to rare deep dips, multiplied in. Hiss =
always-on bandpassed `no.noise` floor. Reused by: Mellotron(11), cassette lo-fi(3), vintage hiss(1).
Ships as a tape character bus for vaporwave/hauntology.

## 4. Analog VA filter family (vaeffects.lib) -- normFreq = fc/(SR/2)
MS-20 = `ve.korg35LPF`/`ve.korg35HPF` in series (+ tanh in the resonance feedback = the creamy fuzz).
OB-Xa = `ve.oberheimLPF` (12dB SEM) cascaded x2 for 24dB, `select2` to switch slope. Ladder machines
(IR3109 / Serum-Mg / PPG-SSM2044) = `ve.moog_vcf` / `ve.moogLadder` (pragmatic 4-pole self-osc). 2-pole =
`fi.svf` lp / `ve.sallenKey2ndOrderLPF`. Non-res 6dB HPF = `fi.highpass(1)`. Push Q to top for
self-oscillation; soft-clip the output. Reused by: 4, 6, 9, 3, 14.
LAW: OB-Xa filter is dual CEM3320 (not the OB-X single SEM); OB-Xa VCOs are saw+pulse ONLY (no triangle).

## 5. Membrane modal synth (strike exciter + modal bank)
`pm.strikeModel(HP,LP,sharpness,gain,gate)` with exPos -> HP=40+exPos*500 / LP=500+exPos*15000. Resonator
`pm.modalModel(N, freqs, t60s, gains)` fed REAL ratios: BESSEL (1, 1.593, 2.135, 2.295, 2.653, ...) for
unloaded heads; LOADED near-harmonic (1,2,2,3,3,4,4,5,5, degenerate pairs micro-detuned) for tabla.
Strokes = presets of {exPos, sharpness, gain-vector, T60-vector}. Add one decoupled `fi.resonbp` for
Helmholtz/cavity modes. Reused by: world-perc(2), Rhodes tonebar(9: f0*{1,6.27,17.55}), santoor(8), metallic impacts(14).
LAW: NEVER `pm.djembeModel` (linear freq+200*i = a toy per its own source comment). 808 cowbell BP ~850-871Hz (NOT 2.6k); odaiko ~50-70Hz.

## 6. Karplus-Strong / digital-waveguide string core (EKS)
Kernel: average(x)=(x+x')/2; loop = `(+ : de.delay(4096,P)) ~ average`; excite `no.noise*gain*trigger(P)`.
Filter chain: pickdir, pickpos comb (1 - z^-floor(beta*P)), one-zero damping (b1=0.5*B, b0=1-B/2,
rho=pow(0.001,1/(freq*t60))), tuning ALLPASS, body IR via rdtable (commuted, LTI only). Reused by: all
plucked/struck world strings(8), Clavinet(9 -- literally a struck string).
LAW (highest-risk): tuning allpass H(z)=(eta+z^-1)/(1+eta*z^-1), pole at z=-eta -- the naive sign
detunes HIGH notes ~5x, and tuning error is worst at HIGH notes. Sitar jawari = amplitude-modulated
moving-boundary delay length (do NOT commute -- it is a geometric nonlinearity).

## 7. FM operator / phase-modulation core
`os.oscp(freq, phaseRadians)` IS phase modulation. `op(ratio,idx,modIn,env,f0) = os.oscp(ratio*f0,
modIn*idx)*env`; feedback op = single-sample self-loop with 2-sample output averaging; compose operators
per the 32 (DX7) / 8 (TX81Z) algorithm topologies. Operator level 0-99 -> radians (log-scaled) = idx.
Reused by: FM engine(5), cheap 2-op tine EP(9), metallic impacts(14), Serum FM-warp(6).
LAW: add the FIXED ~16kHz output reconstruction LPF (DX7 has one -- say "no VCF", not "no filter"). Lately
Bass = TX81Z 4-op algo 2 (waveform 5, feedback on OP4); DX7 BASS 1 = algo 16. Use 12-bit phase->sine.

## 8. Wavetable rdtable oscillator (2-axis interp + offline mip band-limit)
`os.phasor` -> idx, linear intra-frame interp (s0 + f*(s1-s0)). Frame morph = all Nf frames concatenated
in ONE rdtable, bilinear (sample x frame) lerp = Serum's crossfade. Anti-alias via an OFFLINE numpy
MIP-BANK (FFT -> null harmonics above each band's Nyquist -> iFFT, ~9-10 octave bands) baked as one big
rdtable; runtime picks band by clamp(floor(log2(freq/f0))). PPG mode = SKIP the band-limit, 8-bit quantize
floor(x*128)/128, and let it alias. Reused by: wavetable(6), riser/impact bodies(14), drop-sample(3), commuted body-IR(8).
LAW: use `it.frdtable` (interpolators lib), NOT os.frdtable; Serum's knob is Detune (not Range).

## 9. Rotary Leslie-Doppler -> fx_leslie
800Hz Linkwitz-Riley crossover (`fi.lowpass(3)` / `fi.highpass(3)`) -> drum/horn paths. Tube soft-clip
FIRST (`ma.tanh` / `ef.cubicnl`, drive). Per-path Doppler = `de.sdelay` modulated = base + (r/c)*sin(2*PI*
f_rot*t) (horn r~0.18m, drum r~0.15m). AM throb *(1 + amDepth*sin(...)). Stereo = 90-180 deg AM/FM phase
offset between L/R taps. INERTIA = `si.smooth` one-pole slew of the TARGET rotation freq with ASYMMETRIC
accel/decel time constants (horn 0.161/0.321s, drum 4.127/1.371s). Bipolar chorale<->tremolo control.
Reused by: organ(10), + standalone rotary on guitar/synth/vocal/drums.

## 10. Divide-down paraphonic saw bank + shared VCA
Always-running band-limited saw bank (`os.sawtooth` per active note, OR 12 top-octave master phasors +
exact /2 octave derivation for phase-lock and cheap foldback), summed to mono. Footages 16'/8'/4' by
summing at three octaves. ONE shared `en.asr` VCA gated by the OR of all held notes, with NO per-note
restart = the paraphonic signature. Fixed formant EQ voicing (`fi.peak_eq` / parallel `fi.resonbp` bells),
NO swept resonant VCF, no self-oscillation. Reused by: string-machines(15), tonewheel organ(10: the
additive cousin -- same always-running bank + key-gated taps), DCO phase-lock concept(4).

## 11. Analog drift / detune / unison stack + deterministic humanization
`par(i,Nv, voice(i))` with ratio(i)=2^(detCents*spread(i)/1200), spread symmetric in [-1,1]; constant-power
pan by width*spread(i); outer-voice gain taper toward "blend"; RANDOMIZE each voice's start phase on gate
(kills the laser-zap); scale the sum by ~1/sqrt(Nv). For choir/humanization add slow per-voice
noise-driven pitch/formant jitter + small onset stagger. Reused by: unison+DCO drift(4), 16-voice "magic
7"(6), ensemble beating(15), SATB(13), divisi smear(12), detuned tonal stacks(14).
LAW: seed per the generative-seed law -- unspecified = fresh roll (echo the seed), explicit = byte-exact.

---
Full per-product DNA + all sources: docs/research_sound_libraries_sota.md ("The 15"). Companions:
faust-writing (voice skeleton + zones), sound-palette (which voice when), fx-usage (bus placement).
More verified LAWs: Vintage-EP -- Hohner Pianet plucks on key DEPRESSION (pad mutes the reed at rest),
NOT on release; model EP "bell" as TWO parts (6.27x tine mechanical inharmonic vs pickup-generated 2nd
harmonic). Choir -- vowel /a/ is F1/F2 ~730/1090Hz (Peterson-Barney), not 1220. Trailer -- 375ms = the
dotted-8th at 120BPM; DERIVE delay/riser timing from the song tempoMap, never hardcode.
