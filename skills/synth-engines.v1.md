---
name: synth-engines
version: 1
kind: sound-design
tags: [faust, synthesis, west-coast, buchla, vector, additive, spectral, modular, generative, cookbook]
hard_constraints:
  - Voices expose zones freq/gain/gate and end `<: _,_`; FX are stereo-through. Build via write_instrument (instant JIT).
  - Wavefolders and complex-osc nonlinearities MUST be oversampled 4-8x + polyBLAMP/ADAA anti-aliased or the West-Coast brightness turns to digital hash.
  - Reuse skills/faust-reusable-blocks: wavetable it.frdtable (#8), VA-filter family (#4), FM operator (#7), analog drift/unison (#11), BBD chorus (#1).
  - The CORRECTION LAWS below are adversarially verified (docs/research_sound_foundry_ii.md) and OUTRANK common knowledge.
---
# Synth engines (Slice B) -- West-Coast/Buchla · vector · additive/spectral · modular-generative

The synthesis PARADIGMS beyond subtractive/FM/wavetable. Assume `import("stdfaust.lib");`.
Full DNA + sources: docs/research_sound_foundry_ii.md.

## West-Coast / Buchla (west_coast_complex.dsp + fx_wavefold + fx_lowpassgate)
TIMBRE by ADDING harmonics (fold/FM), not filtering them away.
- COMPLEX OSC (through-zero FM): integrate frequency so TZFM works --
  `phase = (+(freq*(1+index*mod)/ma.SR) ~ ma.frac); sig = sin(2*ma.PI*phase)`. Modulator = `os.osc(ratio*freq)` into BOTH the FM path and (AM) the timbre drive. Macros: ratio, fmIndex, timbre(=fold drive).
- WAVEFOLDER (Buchla 259) = 5 inverse-clipper cells (`ef.wavefold` or explicit `cell(th,slope)` sum). OVERSAMPLE 4-8x + polyBLAMP/first-order-antiderivative on the fold corners.
- LOW-PASS GATE (vactrol) = a 2-pole lowpass (`ve.*` / Sallen-Key) whose cutoff AND a parallel VCA are BOTH driven by one slew-limited opto envelope (`si.smooth`, asymmetric fast-attack/slow-decay) = the plucky "Buchla bongo".
- **LAW: the Make Noise DPO does NOT do through-zero FM -- its Linear-FM input is AC-COUPLED** (per the DPO manual). Linear FM (not TZFM) keeps perceived pitch stable under modulation; only implement TZFM where the source actually has it (Buchla 259 principal).
- fx_wavefold + fx_lowpassgate ship as a REUSABLE FX pair (fold a pad, gate a drum bus for opto-pluck dynamics).

## Vector synthesis (vector_synth.dsp -- Prophet VS / Wavestation)
- 4 single-cycle oscillators A/B/C/D: `p = os.phasor(TS,freq); slot_i = it.frdtable(TS, wave_i, p*TS)`.
- Generate the "96-wave ROM" ADDITIVELY (each wave = a fixed harmonic-amplitude spec summed with sines capped below Nyquist, per-octave mip tables) = inspectable Faust data, NO samples. Add tiny per-osc detune (block #11).
- VECTOR MIX (Prophet VS diamond) = bilinear blend by zones `vx,vy` in [-1,1]; automate the vector PATH with a looping 2-D envelope (source.vx/source.vy as automation lanes = the motion primitive).
- WAVE SEQUENCE (Wavestation) = a clocked, tempo-synced stepped index into a wave list with crossfade -- move it OUT of DSP into a `source.wavepos` automation (Faust tables are compile-time only).
- Filter = Curtis CEM3379/3389 24dB 4-pole (`ve.moog_vcf` pragmatic). Unlocks 80s/90s hybrid pads, morphing cinematic beds, rhythmic wave-sequence motion.

## Additive / spectral resynthesis (additive_bank.dsp -- K5000 / Synclavier / SMS)
- CORE: `par(i,N, os.oscrs((i+1)*f0)*hlvl(i)*henv(i)) :> _`. `os.oscrs` = coupled-form resonator = cheapest big sine bank (cap N~24-32 for CPU; K5000-scale = 64). Use `os.oscp` where start-phase matters.
- `hlvl(i)` = per-harmonic base gain (the static waveform, hslider group or it.frdtable). `henv(i)` = per-partial env, made LOOPING (K5000 cycling-decay) via `ba.pulsen`/`os.lf_sawpos` retrigger.
- MORPH = lerp two amplitude vectors A[],B[] by a timbre knob (automatable). Formant = spectral tilt / per-partial gain shaping. Add 2-op FM per partial for Synclavier shimmer.
- RESYNTHESIS = an OFFLINE Python STFT peak-tracker (McAulay-Quatieri: birth/death + residual) emitting per-partial breakpoints that drive the Faust bank -> artifact-free re-pitch, independent time-stretch, spectral freeze, cross-synthesis.
- **LAW: MQ interpolates amplitude LINEAR-IN-AMPLITUDE (NOT dB -- one secondary source is wrong) and phase with a maximally-smooth CUBIC polynomial.**

## Modular / Eurorack generative (control-module library + West-Coast voices)
Pure control-/audio-rate Faust; shift registers use explicit unit-delay feedback (letrec / `@`):
- `clock(bpm)` = `os.lf_sawpos(bpm/60)`, gate=(phase<duty), rising edge=(clk>clk'). `clockDiv(n)` = `ba.counter(edge)` %n (or a T-flip-flop chain for /2^k).
- `sAndH` = `ba.sAndH(trig,x)`. `randCV(clk)` = `no.noise:ba.sAndH(edge)` (decorrelate channels with distinct seeds/`no.noises`). `slew` = `si.smooth`.
- TURING MACHINE = an N-bit recirculating shift register (letrec/`@`) with probabilistic XOR feedback (the loop-vs-mutate "loop length" knob). RUNGLER = a chaotic shift-register from two cross-modulated oscillators.
- QUANTIZER = round-to-scale `it.frdtable` LOCKED TO THE SONG CHORD GRID = harmony-safe generative melody. Wire modules as SoundRecipes / song.json patch graphs = "patch = composition".
- Unlocks generative/ambient (Eno/Krell), Berlin-school, Autechre/IDM evolving sequences, no-input chaos drone.

Companions: faust-reusable-blocks (the blocks these reuse + the NEW wavefold+LPG, additive-bank,
generative-control blocks), sound-palette (a new synth voice class per engine), automation-motion
(2-D vector-envelope loop + wavepos-scan templates), faust-writing (voice skeleton).
