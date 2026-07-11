---
name: surgical-edits
version: 1
kind: workflow
tags: [always, surgical, edit, selection, scalpel]
hard_constraints:
  - "SCOPED ASK => SCALPEL: when the user points at a sound/moment/notes ('this note', 'the hats in the drop', 'at 1:23', 'the 3rd kick', a SELECTION or TRANSPORT block in context) use locate -> select_notes -> surgical_edit. NEVER resend a whole track's notes (update_track) or the whole song (write_song) for a scoped ask - the sidecar diffs the proposal against edit receipts and flags every unreceipted change OUT OF SCOPE to the user."
  - "0 matches = STOP and re-locate. Never 'fix' a selector miss by editing something similar elsewhere."
  - "SELECTED NOTES in context ship note indices - selector {\"tracks\":\"<track>\",\"indices\":[...]} hits exactly them; prefer it over rebuilding the address from beats/pitches."
---

# Surgical edits — THE SCALPEL

Producers point: *"the 3rd kick of the drop"*, *"those hats right there"*, *"the note at 1:23"*,
*"make the bass at bar 17 longer"*. Touch EXACTLY that and NOTHING else. The sidecar
semantic-diffs your whole proposal against your edit receipts — unreceipted changes are shown
to the user as **OUT OF SCOPE**. Surgical is enforced, not vibes.

## The protocol (3 cheap calls)

1. **locate** — resolve the human coordinate. Timestamps (`"1:23"`) become beats through the
   tempoMap; section names become bar ranges; a sound description ("the squelchy bass") returns
   ranked track candidates with evidence + a ready selector; the response shows WHAT IS SOUNDING
   at that moment per track (pitch names, clips, live automation values). If context already has
   a TRANSPORT/NOW or SELECTION block, that IS your locate — skip to 2.
2. **select_notes** — dry-run the selector; read the exact matches back (track/beat/pitch/vel).
   Count or span surprising? FIX THE SELECTOR, don't widen the ops.
3. **surgical_edit** — ops on the matched set. Use `preview:true` first when destructive
   (delete/replace) or when matched count > 32.

## Selector fields (AND-ed)

- `tracks`: `"808"` | `["kick","hats"]` | `{"match":"bass"}` | `{"role":"kick|bass|snare|hat|perc|pad|lead|keys|chords|vocal|fx"}`
- range: `bars:[16,18]` | `beats:[64,72]` | `section:"drop"` (`{"name":"drop","occurrence":2}` for repeats) | `time:"1:23"` or `["1:20","1:28"]` | `around:{"beat":66.5,"widthBeats":4}`
- `pitch`: `29` | `"F#1"` | `[36,48]` | `{"classes":["F","Ab"]}` · `vel`/`len`: `{"min":..,"max":..}`
- `grid:{"step":0.5,"phase":0.25,"tol":0.06}` — notes ON a grid slot (offbeat 8ths: step 1, phase 0.5)
- `nth: 3` — 3rd matching ONSET (a chord = one onset; -1 = last) · `every:{"step":2}` · `count: N`
- `indices:[...]` — the UI selection's exact note indices (one track)

## Ops (in order, on the matched set)

`{"op":"shift","pitch":+2}` transpose · `{"op":"shift","start":+0.25}` nudge ·
`{"op":"set","vel":0.9}` · `{"op":"scale","vel":0.8}` ·
`{"op":"quantize","grid":0.25,"strength":0.7}` · `{"op":"humanize","timing":0.02,"vel":0.05}`
(deterministic per seed) · `{"op":"stretch","factor":2}` (half-time in place) ·
`{"op":"velocity_ramp","from":0.4,"to":1.0}` (crescendo across the range) · `{"op":"delete"}` ·
`{"op":"insert","notes":[...]}` (must land inside the range) · `{"op":"replace","notes":[...]}`
(rewrite the riff) · `{"op":"retrack","to":"perc"}` (move notes).

## Craft

- Gains/pans/fx/params/automation keep their own surgical tools (`set_track_param`, `automate`,
  `set_track_fx`) — those file receipts too. The scalpel is for NOTES.
- Ambiguity: cut the top candidate only, and name the alternative you did NOT touch in your
  summary — one cheap redirect beats a wrong guess.
- Quote your receipts in the final bullets ("hats: vel×0.8 on 5 notes in bars 4–8") — the user
  sees the same receipt in the UI; matching words build trust.
