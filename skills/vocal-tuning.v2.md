---
name: vocal-tuning
version: 2
kind: production
tags: [vocals, tuning, pitch, audio, context-tune]
hard_constraints:
  - tune_vocal works on audio clips (recorded takes, imported stems, generated vocals) — never on note tracks (fix those with surgical_edit).
  - Pick style by GENRE INTENT, not by default; tpain is an EFFECT, transparent is a repair.
  - Always render_song + hear after tuning; read the report's biggest moves — a >150c move usually means the singer meant a different note: re-run with guide_track.
  - Never chain tunes to "add more": tune_vocal always re-tunes from the ORIGINAL source (tuning provenance in the clip). To change the result, change style/strength/guide, not repetition.
  - WET/in-mix sources (demucs stems, reverb-soaked takes, bleed): pass f0:"fcpe" — harvest silently drops ~1/3 of the notes on wet material; fcpe recovers ~98%.
  - The offline rail (tune_vocal) is the PRECISION tool; fx_retune is the LIVE/monitor path — do not use fx_retune to master a final vocal that tune_vocal could process offline.
---
# CONTEXT-TUNE: song-aware vocal tuning (tune_vocal + fx_retune, V45)

Unlike classic autotune (one static scale), CONTEXT-TUNE reads the ARRANGEMENT: per-beat chord
field from every other track's notes (bass-weighted), the song scale (meta key or fitted),
optional guide melody. Offline: Viterbi targets + WORLD resynthesis, formants preserved,
timing untouched, and the SURGICAL SPLICE — only spans whose pitch audibly changes go through
the vocoder; consonants/breaths/silence stay bit-exact original (real vocals: ~74% passthrough).

## Style by intent (genre map)
- **tpain** — trap, drill, hyperpop, melodic rap hooks. 3ms retune, vibrato flattened,
  glides become yodel stairs. The EFFECT everyone means by "autotune".
- **hard** — pop hooks, dance toplines, K-pop: tight and shiny but breathing.
- **natural** — R&B, soul, indie: drift corrected, vibrato and scoops kept.
- **transparent** — jazz, gospel leads: only repairs, never changes note identity; blue notes survive.

## The loop
1. `tune_vocal {song, track, style}` (+ `f0:"fcpe"` if the clip is a wet stem) → read summary:
   corrected/total + biggest moves + WHY (chord(F) / scale(F minor) / guide / nearest / held(quiet)).
2. `render_song` + `hear` — the vocal should sit on the harmony now.
3. Wrong TARGET on a note? Surgical outs: `guide_track` (a melody lane = explicit target line
   — pitch-to-melody) or `region [b0,b1]` (only correct that span). Per-section styles: widest
   region first, then narrower.
4. `strength` (0..1) when natural still feels too tuned (0.5–0.7).

## LIVE: fx_retune (the chord-following insert)
`set_track_fx` with `{"id":"fx_retune","params":{"amount":1.0,"retuneMs":8}}` on a vocal/audio
track. The engine compiles the OTHER tracks' notes into a per-half-beat chord grid at load;
live input (or the clip, in renders) is YIN-detected and shifted to the nearest allowed pitch
— chord tones pull, scale stays reachable, formants preserved (signalsmith-stretch). Latency
~140ms, PDC-compensated in renders (fine for monitoring/performance; NOT for final masters —
use tune_vocal offline). amount + retuneMs are automatable (`fx[i].amount`). Proven: renders
land targets at ~14c median and beat chromatic snapping on the same traps as the offline rail.

## Reading the report (songs/_tuned_*.report.json)
Per note: beat span, sung, target, cents_moved, reason; stats now include `f0_mode`,
`resynth_pct`/`passthrough_pct` (how much audio the vocoder touched — lower = cleaner).
`held(quiet)` = breath/noise floor passthrough (correct). Many `nearest` reasons = no harmonic
context at those beats — add/unmute harmony tracks or pass `key`.

## Limits (v2, honest)
- Monophonic sources only; stacked harmonies = tune each stem.
- fx_retune targets by nearest-allowed (no lookahead Viterbi); big interval intent needs the
  offline rail or a guide track.
- Vocal fry / whisper may vocode at tpain settings — region-hold them.
- A held note over a chord change targets the chord it LANDS on (front-biased); mid-note
  retargeting is v3 territory.
