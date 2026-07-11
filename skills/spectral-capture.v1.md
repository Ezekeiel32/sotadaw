---
name: spectral-capture
version: 1
kind: tooling
tags: [audio, midi, reconstruction, capture, resynthesis, sampling]
hard_constraints:
  - audio_to_midi is RECONSTRUCTION MIDI (the sound itself as notes); import_song_audio sketches are MUSICAL MIDI (what was played). Choose by intent — "edit the notes" wants sketches, "own this sound as editable material" wants spectral capture.
  - NEVER hand-add notes to spectral_noise (band rows, not pitches) — edit its dynamics via velocity only.
  - After ANY edit to spectral_* lanes, call midi_to_audio — the lanes are silent sketches; spectral_mix is what plays. An un-rerendered edit is an inaudible edit.
  - Lossless truth is FILE-level (render+residual == original bytes via tools/spectral.py render --lossless). Engine playback of mix+residual is float-transparent (~86dB SI-SDR measured), not literally byte-checked.
  - Deleting or editing partial notes leaves the residual UNTOUCHED — in lossless sessions mute spectral_residual when you reshape heavily, or the old sound bleeds through.
---
# Spectral capture: audio ⇄ MIDI at reconstruction fidelity

`audio_to_midi` turns ANY audio into MIDI that renders back to (nearly) the same
audio. Every partial in the sound becomes ONE note whose pitch-bend + gain
envelopes live in `songs/<name>_spectral/capture.json`; transients ride
`spectral_clicks` (each note carries its exact waveform snippet); the noise
floor rides `spectral_noise` (pitch row = mel band). The audible truth is the
`spectral_mix` clip; `mode=lossless` adds `spectral_residual` so mix+residual
IS the original file.

Measured (2026-07-07 battery): synthetics 98-100% spectral (tone SI-SDR 82dB),
real music 92-95% spectral pure-MIDI, lossless byte-exact True, engine
roundtrip of a real mp3 99.99% / SI-SDR 86.7dB. Deterministic: same capture →
md5-identical render.

## The verbs
- `audio_to_midi {audio_path, song?, mode?, bpm?, t0?, t1?}` — capture. Use
  `t0/t1` (seconds) for SURGICAL grabs: one horn stab, one 808 slide, one
  vocal phrase. bpm stamps the beat grid so envelopes warp with tempo edits.
- `midi_to_audio {song}` — re-render the CURRENT lanes (your edits included),
  swap spectral_mix in place, report fidelity vs source. Unedited = identical.
- `roundtrip_verify {a, b}` — the honest scorecard between any two files.
- CLI equivalents + MPE export:
  `tools/spectral.py capture|render|verify|roundtrip|export-mpe|selftest`.

## What edits mean
- move / transpose / stretch / velocity on a partial note → its envelopes ride
  along (transpose shifts the whole harmonic; stretch time-scales the bend).
- delete → that partial vanishes from the render (surgical de-noising: kill
  the whistle, keep the voice).
- add a plain note → clean sine with AD envelope (no envelopes to inherit).
- clicks lane: moving a note moves THAT drum hit; pitch edit = rate-shift.
- Full remix moves (new key, half-time): capture per STEM after
  import_song_audio, then reshape each stem's spectral lanes.

## When NOT to use it
- You want playable/loopable musical material → import_song_audio sketches.
- You want a synth patch that *sounds like* it → sound-palette / write_instrument.
- File is >2min and you only need a moment → always pass t0/t1 (capture is
  ~6s per 10s of audio; JSON grows with density).

## Sound-aware correction (why it's tight)
Capture runs an analysis-by-synthesis loop: it RENDERS the note layers, measures
the true residual vs the original, pulls back tonal content the render missed as
correction notes, and fits the noise (magnitudes + phases) to that real residual —
so the model is tuned to what actually plays, not an optimistic estimate. Real
music re-renders at 98.9-99% pure-MIDI; vocals 98.5% + 100% byte-exact (lossless).

## LIVE monitoring (SpectralVoicePlugin)
Partial lanes carry source {"kind":"spectral"} — UNMUTE a lane (and mute
P_mix) to hear edits immediately: the engine synthesizes each note's partial
with its envelopes live (~81% mel monitor quality; block-quantized timing,
no clicks/noise lanes). It is a MONITOR — for the real thing re-render via
midi_to_audio, and lossless truth always = mix+residual.

## The loop that makes it surgical
1) `audio_to_midi` (region!) → read the fidelity line it returns.
2) Edit exactly the notes that need to change (select_notes/surgical_edit work
   on spectral lanes like any other).
3) `midi_to_audio` → listen (spectral_mix) → `roundtrip_verify` if the claim
   matters.
