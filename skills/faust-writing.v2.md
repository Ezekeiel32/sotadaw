---
name: faust-writing
version: 2
kind: language
tags: [faust, always]
hard_constraints:
  - Every instrument MUST expose zones named exactly: freq (hslider, if pitched), gain (hslider 0..1), gate (button). The host maps MIDI to these names.
  - Output MUST be stereo: end the process expression with `<: _,_` (or produce 2 channels).
  - `import("stdfaust.lib");` first line. Use namespaced stdlib: os.*, fi.*, en.*, no.*, ma.*, ve.*, pm.*, de.*.
  - Never let output exceed |1.0|. Voices play POLYPHONICALLY — scale so a 3-4 note CHORD stays under 0 dBFS (aim a single sustained note near -12..-16 dBFS for headroom); on resonant/formant/high-Q voices add `: ma.tanh` as a safety net (near-linear when quiet, catches peaks). The formant_vox lesson: three high-Q resonbp formants summed over a chord clipped at +0 dBFS until scaled 0.30 + tanh.
  - Keep per-sample CPU bounded: no unbounded recursion; Faust guarantees this if it compiles.
---
# Writing Faust instruments for this DAW (validated idioms)

Standard skeleton (all shipped instruments follow it):

```faust
import("stdfaust.lib");
freq = hslider("freq", 220, 20, 4000, 0.001);
gain = hslider("gain", 0.8, 0, 1, 0.01);
gate = button("gate");
env  = en.adsr(0.005, 0.2, 0.7, 0.2, gate);   // or en.ar(att, rel, gate) for one-shots
process = os.sawtooth(freq) * env * gain : fi.lowpass(2, 3000) <: _,_;
```

Validated building blocks:
- Oscillators: `os.osc` (sine), `os.sawtooth`, `os.square`, `os.triangle`, `os.pulsetrain(f,duty)` (all band-limited); noise: `no.noise`, `no.pink_noise`, `no.lfnoise0(rate)` (sample-hold).
- Envelopes: `en.ar(a,r,gate)` for drums/one-shots; `en.adsr(a,d,s,r,gate)` sustained; `en.asr(a,s,r,gate)` for late-blooming vibrato/swells.
- Filters: `fi.lowpass/highpass(order,hz)`, `fi.resonlp/resonbp(hz,q,gain)`, `fi.bandpass(order,lo,hi)`, `fi.svf.*`, `ve.moog_vcf(res,fr)` (4-pole ladder, self-oscillates near res=0.99).
- Saturation `: ma.tanh` after a gain boost = analog drive. Pitch env `os.osc(freq*(1+amt*en.ar(...)))` = the 808/kick drop.
- FM `os.osc(freq + os.osc(freq*ratio)*(freq*ratio)*indexEnv)`; ratio 2≈Rhodes, 3.5≈metallic bell. Detune stacks: sum `os.sawtooth(freq*(1+d))`, divide by count.

Compile-check discipline: the host validates with the Faust compiler and returns stderr on failure —
read the error line, fix, resubmit. Common errors: missing `;`, unbalanced parens, wrong arg counts.
Traps: `ceil` is reserved; prime identifiers (`x'`) break inside `with{}` (use `xp`). Iterate under a
name NOT yet in `faust_gen` — it JIT-renders instantly (no rebuild); promote with gen_faust.sh later.

## World / acoustic voice idioms (validated — the SOUND FOUNDRY, see docs/research_sound_foundry.md)

Cited numbers (formant table, modal ratios, musette cents, chip duties, reed frequencies) live in
`docs/research_sound_foundry.md` — read it before authoring a world voice; don't guess the acoustics.

- **Breath / air** (flutes, reeds): `no.noise*breathA : fi.resonbp(freq*k, Q, 1) : fi.lowpass(2, top)`.
  Make it a FEATURE, not noise — ney/shakuhachi are 20-40% air. A separate `en.ar` breath BURST at
  attack = the chiff (pan flute) / muraiki (shakuhachi) — "the tone swells up AFTER the chiff."
- **Formant filters** (vox, nasal reeds, bowed body): source `<: (fi.resonbp(F1,Q1,1)*g1, fi.resonbp(F2,Q2,1)*g2, ...) :> _`. F1/F2/F3 vowel table + Q=F/BW in the doc.
- **Bowed string** (erhu/fiddle): `os.sawtooth(f)` + bow-noise `no.noise:fi.resonbp` through a resonator formant; WIDE vibrato that blooms (`en.asr`); portamento = a 1-pole lowpass on freq (`freq:fi.lowpass(1, glideHz)`).
- **Double reed** (duduk/zurna): duduk = `os.square` (ODD harmonics, cylindrical) + a low reed resonance (~480 Hz) + dark lowpass; zurna = `os.sawtooth+os.square` (full series) + a NASAL formant (~2.8 kHz) + circular-breath sustain=1.0.
- **Free reed** (harmonica/bandoneon/accordion): 2-3 detuned reed banks (`os.pulsetrain`/saw) — the detune IS the tremolo (musette cents, not an LFO); `pow(2,cents/1200)` for the beat.
- **Drone + melody** (bagpipes): a fixed-pitch drone (`drone` zone in Hz = the tonic) summed under the chanter on `freq`; play notes legato so the drone sustains.

## Exotic / retro synth idioms

- **Chip pulse**: variable-duty square `(os.lf_sawpos(f) < duty) - 0.5` — use the NAIVE `os.lf_sawpos` (aliasing is period-authentic to the chip). NES duties 12.5/25/50%, GB adds 75%. PWM = LFO on duty; NES `drop` = downward `en.ar` pitch blip on attack.
- **Chip triangle**: quantize `os.triangle` to 16 levels: `floor((tri*0.5+0.5)*steps)/steps*2 - 1` (the 4-bit stairstep); near-flat env (chip has no volume control).
- **Chip noise**: `no.lfnoise0(clock)` for white; resonate through `fi.resonbp` for the short-LFSR metallic buzz.
- **Phase distortion (Casio CZ)**: cosine read by a warped phase — `p=os.lf_sawpos(f)`, two-segment warp toward a knee `m` (m=0.5→sine, lower→resonant), `cos(2*ma.PI*y)`; a bright attack settling to `m` = the DCW envelope.
- **Formant / vowel synth**: glottal saw → 3 parallel formant bandpasses; morph vowels with LOG-interp `F = Fa*pow(Fb/Fa, x)`. Automate the `vowel` zone to make it TALK.
- **Additive**: `sum(i, N, os.osc(freq*(i+1)) * amp(i+1) * pow(tilt,i))` — one `bright`/tilt knob scales upper partials; `int(n)%2` for odd/even balance.

## Anti-aliasing & level laws
- Naive `os.lf_*` oscillators alias by design — KEEP them for chip voices; use band-limited `os.sawtooth/square/triangle` everywhere else. The PD knee at very small `m` also aliases (oversample for a clean CZ lead).
- Scale for polyphony (chords sum) + `ma.tanh` safety on resonant voices. Prove every new voice with a render + analyze (0 clipped, in-tune) before shipping.
