---
name: a2m-byte-par
version: 1
kind: workflow
tags: [import, audio-to-midi, correction, fidelity, drums, vocals, byte-par]
hard_constraints:
  - "The record is the target, the stems are the ruler: after ANY edit wave on an imported song, run a2m_correct (closed loop) — it matches every lane group's LUFS to its stem, re-anchors drum hits to the stem's onsets (<=35ms), refits per-hit velocities through the sampler dB law and SALVAGES missing hits. Never hand-balance an imported product by ear alone."
  - "Fix level at the SOURCE, never the output: the 'heavily limited / mutilated' sound is the pre-master sum overshooting the record into the -1.2 truepeak wall (measured +4.8dBFS overshoot before correction). After correction the wall idles. Do not raise masterGainDb, do not touch the ceiling."
  - "Vocals are NEVER chopped record audio. The default vocal sound of an import is vocals_true (the record's own performance re-synthesized from parametric spectral capture — DETECTED replica, MIDI-shaped data). vocals_sung (DiffSinger) is the muted synth alternative; vocals_sketch stays the melody edit surface. Truth outranks synth."
  - "Drum kits are DRY REPLICAS, not wet slices: source_kit builds each voice as a phase-aligned median over <=24 instances (room/reverb/bleed vote out; the drum survives) with per-voice tail budgets (chat 80ms, perc 160, snare 280, kick 320, ohat 450, crash 1400). If a re-imported kit sounds echoey/far, rebuild it — do not EQ around a wet exemplar."
  - "Timeline stem references land UNWARPED (the song grid was born from the record; a ratio-1.0 warp still smears transients and drifts — measured onset F1 0.27 vs its own source). Launcher slots keep sourceBpm. Never A/B against a warped reference."
  - "Numbers or it didn't happen: fidelity claims come from spectral.verify_arrays (spectral_pct / wave_corr / SI-SDR / env_corr) vs the stem or stem-sum, drum truth from onset F1 +-30ms, echo from gap-spill (energy landing >120ms after the previous record onset). LUFS(warped clip) != LUFS(raw stem) — one ruler per campaign."
---
# A2M byte-par (v1) — audio ⇄ MIDI at record fidelity

The goal (Chezy): re-rendered MIDI ≈ the record — 98.9%. Everything detected,
symbolic, editable; nothing chopped or copied.

## The workflow

1. `import_song_audio(audio, song)` — stems (BS-Roformer vocals + demucs),
   specialist MIDI rails, named drum lanes on the record's own DRY-replica kit,
   unwarped muted stem refs, THE FINAL CORRECTION as the finale, then the
   finisher chain lands `vocals_true` (sounding) + `vocals_sung` (muted alt)
   in the background. Progress: `agent/ipc/import_progress.json`.
2. After edits (yours or the user's): `a2m_correct(song)` — one call re-trues
   gains, drum timing/velocities, missing hits. `iters=2` converges (≤0.5dB).
3. Vocal re-lands: `vocal_truth(song)` any time the vocal stem exists —
   phrase-windowed, RAM-gated; on a tight box it lands late, never dies loud.
4. Verify before claiming: render + `verify_arrays` vs the stem-sum, drum
   onset F1, gap-spill. Position tonight (aranyanyara, 206 bars): product
   LUFS −0.98dB of the record, drums F1 0.906 / recall 0.94, vocal window
   96.14% spectral / SI-SDR 37dB, drum echo energy 17.0% → 10.4%.

## Traps (measured)

- spectral capture's analyze allocates ~3.3GB per 45s mono — window it
  (vocal_truth does) or the OOM daemons kill the run silently through pipes
  (check PIPESTATUS, never trust `| tail` rc).
- `capture()` loads its WHOLE input before t0/t1 — hand it a window wav.
- A salvage/velocity pass changes lane loudness — always re-run the gain law
  after geometry (a2m_correct orders this correctly; keep it if you fork).
