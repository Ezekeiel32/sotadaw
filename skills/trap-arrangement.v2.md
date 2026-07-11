---
name: trap-arrangement
version: 2
kind: arrangement
tags: [trap, drill, hiphop, arrangement]
hard_constraints:
  - Tempo 130-160 BPM, halftime — snare/clap on beat 2.0 of each bar (musical beat 3), NOT 1 and 3.
  - Use song-level swing ({"grid":"16th","amount":0.54-0.60}) — the engine swings on-grid notes; keep manual off-grid placement only for special pushes (laid-back snare +0.02).
  - 808 (faust kick_808) = the bassline, tuned to key, MIDI 24-40; note starts define the low-end rhythm.
  - Real drums from gm_drums: clap 39 (or snare 38) for the backbone, closed hat 42 grid, open hat 46 at phrase ends.
  - Sparse: 5-8 tracks, space is the genre.
song_format_reminder: >
  v1: {"version":1, "bpm", "key", "lengthBars", "swing":{"grid","amount"},
  "sections":[{"name","startBar"}], "masterGainDb", "master":[{"type":"limiter","params":{"ceiling":-1}}],
  "tracks":[{"name", "source":{"kind":"faust|sample|vst3","id":...}, "gainDb","pan",
  "notes":[{"start","len","pitch","vel"}]}]} — start/len in BEATS (bar = 4).
---
# Trap arrangement v2 (hybrid palette era)

Per bar (beats 0..4):
- 808: downbeat 0 anchor (len 1.0-1.5); syncopated moves near 1.5 / 2.5 / 3.5; change pitch on the
  moves (walk the key: root, b3, 4, 5, b7). Two-bar patterns, vary the second pair.
- Clap/snare (sample 39/38): beat 2.0 every bar. Optional ghost (vel 0.35) at 3.75 occasionally.
- Closed hats (sample 42): 8th grid base (0, 0.5, ...), vel 0.75 downbeats / 0.45 off; 16th rolls
  (0.25 steps) into bar ends; occasional 32nd stutter (0.125 steps) once per 4 bars; open hat 46
  on the last 8th of a phrase, vel 0.5.
- Kick attack layer (sample 36) doubling SOME 808 hits (vel 0.8) — not all, keep bounce.
- Melody: ONE lead (piano/epiano/Dexed) sparse motif octave 5-6, 3-6 notes per 2 bars, minor key,
  placed off the 808's moves. ONE pad (strings/warmpad/choir) whole/half-note chords at -10 to -14 dB.
- Structure (8+ bars): bars 1-2 reduced intro (no hats or no 808), full by bar 3, strip one element
  for a 1-bar breath around bar 7, fill (hat roll / open hat) into the loop point.

Groove: song swing 0.56 as the default pocket; velocities always humanized (±0.05-0.1);
never two identical consecutive hat velocities.
Keys that sit dark: F minor, G minor, C minor. 808 roots: F1=29, G1=31, C2=36.
