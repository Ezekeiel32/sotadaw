---
name: vocal-tuning
version: 1
kind: production
tags: [vocals, tuning, pitch, audio, context-tune]
hard_constraints:
  - tune_vocal works on audio clips (recorded takes, imported stems, generated vocals) — never on note tracks (fix those with surgical_edit).
  - Pick style by GENRE INTENT, not by default; tpain is an EFFECT, transparent is a repair.
  - Always render_song + hear after tuning; read the report's biggest moves — a >150c move usually means the singer meant a different note: re-run with guide_track.
  - Never chain tunes to "add more": tune_vocal always re-tunes from the ORIGINAL source (tuning provenance in the clip). To change the result, change style/strength/guide, not repetition.
  - The tuned wav replaces the clip file only in THIS song's JSON; the source wav is never touched.
---
# CONTEXT-TUNE: song-aware vocal tuning (tune_vocal, V45)

Unlike classic autotune (one static scale), tune_vocal reads the ARRANGEMENT: per-beat chord
field from every other track's notes (bass-weighted), the song scale (meta key or fitted),
optional guide melody. Targets picked by Viterbi over chord-tone/scale/contour; resynthesis
through the WORLD vocoder — formants preserved (T-Pain, not chipmunk), timing untouched.

## Style by intent (genre map)
- **tpain** — trap, drill, hyperpop, melodic rap hooks, autotune-as-instrument. 3ms retune,
  vibrato flattened, glides become yodel stairs. The EFFECT everyone means by "autotune".
- **hard** — pop hooks, dance toplines, K-pop: tight and shiny but breathing (12ms, some vibrato).
- **natural** — R&B, soul, indie, singer-songwriter: drift corrected, vibrato and scoops kept.
- **transparent** — jazz, gospel leads, anything precious: only repairs, never changes note
  identity; keeps blue notes (a clearly-sung out-of-scale note survives).

## The loop
1. `tune_vocal {song, track, style}` → read the summary: corrected/total + biggest moves + WHY
   (chord(F) / scale(F minor) / guide / nearest / held(quiet)).
2. `render_song` + `hear` — check the vocal sits on the harmony now.
3. Wrong TARGET on some note (singer intended something else)? Two surgical outs:
   - `guide_track`: point at any melody lane — its notes become the explicit target line
     (pitch-to-melody; write the intended melody in the piano roll first if needed).
   - `region [b0, b1]`: only correct that span, leave the rest untouched. Multiple calls with
     different regions/styles compose (verse natural + chorus tpain) because each call
     re-tunes from the original and applies only inside its region — BUT regions of later
     calls replace earlier results outside their span; for per-section styles, do the WIDEST
     region first, then narrower ones.
4. `strength` (0..1) scales correction amount when natural still feels too tuned (0.5-0.7).

## Reading the report (songs/_tuned_*.report.json)
Per note: beat span, sung (name+cents), target, cents_moved, reason. Median |cents| after a
good tpain pass ≈ 0-5c; natural leaves 10-25c of human. `held(quiet)` = breath/noise floor
passthrough (correct). Many `nearest` reasons = the song had no harmonic context at those
beats — add/unmute the harmony tracks or pass `key`.

## Limits (v1, honest)
- Monophonic sources only (lead/backing single voice). Stacked harmonies: tune each stem.
- Dry-ish sources tune cleanest; heavy reverb/delay should be applied AFTER tuning (fx on
  the track apply post-clip, so the standard chain is already correct).
- Vocal fry / whisper segments may sound vocoded at tpain settings — region-hold them.
- A held note over a chord change targets the chord it LANDS on (front-biased); mid-note
  retargeting is v2.
