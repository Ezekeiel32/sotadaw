---
name: synth-maps
version: 1
kind: sound-design
tags: [always, vst3, presets, sound-design]
hard_constraints:
  - vst3 source params are NATURAL units on PROCESSOR display names (the engine converts per-param). Use the ranges below — values outside them clamp.
  - Start from a factory preset (vst_presets get) and tweak 2-5 named params; never design a patch from init unless asked.
  - Filter cutoffs and envelope times are LOG-scaled (skewed) — musical moves are multiplicative (half/double), not linear steps.
---
# Synth maps: the knobs that matter (source-truth ranges)

Presets are STARTING POINTS. After inlining one, reshape it with these.

## Odin2 (260 presets; params dict; ranges from its own registration table)
The big five moves:
- DARKER/BRIGHTER: "Filter1 Frequency" [20..20000 Hz, log; default wide open] — the single
  strongest character knob. Pair with "Filter1 Resonance" [0..1] (0.3-0.6 = vocal peak).
- SHAPE: "AmpEnv Attack"/"Decay"/"Release" [0.001..10 s, log] + "AmpEnv Sustain" [0..1].
  Pad = attack 0.3-1.5s release 1-4s; stab = attack ≤5ms decay 0.2-0.5 sustain 0; pluck adds
  "Filter1 Envelope Amount" [-1..1] at +0.4-0.8 with FilterEnv decay 0.1-0.4s.
- MOTION: "LFO1 Frequency" [0.05..100 Hz] (0.1-0.5 = slow pad drift); "Osc1 Wavetble
  Position" [0..1] = timbre morph (automatable!).
- WEIGHT: "Osc1/2/3 Volume" [-60..12 dB] layer balance; "Osc1 Octave" [-4..4]; "Glide"
  [0..1] for 303-style lines (mono patches).
- SPACE/DIRT (prefer track fx, but native works): "Chorus Amount" [0..1], "Delay Wet" [0..1]
  + "Delay Time" [0.01..3 s], "Distortion Boost" [0..1], "Filter1 Saturation" [0..1].
- Master trim: "Amplifier Gain" [-30..12 dB], "Amplifier Panorama" [-1..1].

## TAL-NoiseMaker (256 presets; params dict; 0..1 normalized on display names)
- "Filter Cutoff" + "Filter Resonance" — same big-five role, 0..1 normalized.
- "Filter Attack/Decay/Sustain/Release" + "Amp Attack/Decay/Sustain/Release" — 0..1.
- "Filter Contour" = env→cutoff amount (0.5 = none, >0.5 positive).
- "Osc1 Volume"/"Osc2 Volume"/"Osc Mastertune"; "Lfo1 Rate"→filter, "Lfo2 Rate"→pitch.
- "Delay Wet"/"Reverb Wet" exist but prefer the fx rack/buses.

## Surge XT (3,559 presets; STATE BLOBS — tweak differently)
Surge loads whole patches (source.preset). To reshape: prefer track fx + automation, or pick
a closer patch (the vault is deep — search by name/category first). Its 'FX Type'/'FX
Parameter N' juce params exist but are unmapped generically — don't fish.

## The workflow
1. vst_presets list (category browse) → get → inline.
2. Render, hear/analyze. Too bright? Halve "Filter1 Frequency". Too stiff? +0.2s attack.
3. Big timbre asks (formant/FM/wavetable morph) → different preset, not knob surgery.
4. Motion beats static: `automate` any of these params (natural units in the points).
