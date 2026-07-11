---
name: import-mix
version: 1
kind: mixing
tags: [import, stems, sketches, reference, mix, remix]
hard_constraints:
  - "RECOGNIZE THE IMPORT before touching it (get_song_summary): stems_import songs carry audio STEM lanes (source kind \"audio\", 0 notes — often just vocals) + *_sketch lanes (basic-pitch score on sample voices) + named drum lanes (Kick/Snare/Hats/Perc/Cymbals). In EDIT-FIRST imports the MIDI lanes ARE the sound and the vocals stem is the record's actual voice. Never add a new voice playing a sketch's same notes (double-sound); re-voice via source_swap so exactly ONE of {sketch, new voice} sounds."
  - "EARS BEFORE HANDS: on \"make it better / mix this / clean it up\", run the analysis ladder BEFORE any fx or note move — use_tool(stem_callouts, {song, sections:true}) says who fights, who is inaudible, and WHERE; doctor names standing traps; energy_curve shows the arc. Then ONE proposal per callout theme. Six identical set_track_fx chains with no ear consulted is the anti-pattern this skill exists to kill (2026-07-10 evidence)."
  - "THE REFERENCE CIRCLE: \"like the original\" is a TOOL CALL, not a vibe — import_song_audio banked the record's production DNA as a KG (:Reference) node named after the song. use_tool(match_reference, {song:<name>, reference:<name>}) returns per-band/LUFS/groove gaps vs the actual record; turn each gap into ONE move (groove_move is apply_groove-ready). KG down or node missing -> analyze_reference with any wav of the record."
  - "HARMONY TRUTH ON IMPORTS: sketches carry transcription noise — before reharmonize/harmonize/tune_vocal, run chords_from_audio({song, wav: songs/<name>_stems/other.wav}) to fuse the audio witness into song.chords[]; the chord lane outranks any single sketch's notes."
  - "STRUCTURE IS MEASURED: sections[] came from the audio (Foote novelty). Generic \"part N\" names mean the withhold law fired (every mid-section reads hot) — the BOUNDARIES are still real; target them with edit_section/energy moves and never invent new boundaries without segment evidence (use_tool(song_structure) on a render to re-measure)."
  - "THE VOCAL STEM IS SACRED: never chop or re-trigger it (detached auto-sing law owns swaps). Tuning: tune_vocal with f0:\"fcpe\" on wet/bleedy stems. Mix moves on the vocal lane: eq/delay/reverb/widen with 1-4k presence protected — the record's voice stays forward."
  - "Finish gate unchanged: auto_master(song, genre) then master_report until pass:true (mix-headroom.v8 owns the wall; fx_truepeak ceiling law rides every proposal)."
---
# Mixing an IMPORTED song (stems + sketches) — the journey

The failure mode this kills: an agent asked to "make it better as-is like the
original" fired six uniform `set_track_fx` chains, consulted zero ears, and
rendered once. Every ear it needed already exists — this skill is the routing.

## The pass, in order

1. **See the shape** — `get_song_summary`. Spot the import: audio stem lanes +
   `*_sketch` lanes + named drum lanes. Note which lanes actually sound
   (EDIT-FIRST: sketches audible, stems mostly replaced except vocals).
2. **Hear the field** — `use_tool(stem_callouts, {song, sections:true})`:
   masking fights (with the kick/808 exception), inaudible lanes, solo clippers,
   phase risk — each callout names its fix tool and its bars. `doctor` for
   zone-traps; `energy_curve` for the arc.
3. **Match the record** — when the ask references the original or any record:
   `use_tool(match_reference, {song:<name>, reference:<name>})` (the import
   banked the DNA). Each gap line -> ONE proposal move; re-render; re-check.
4. **Harmony work?** — `chords_from_audio` first (audio witness -> song.chords[]),
   then reharmonize/harmonize/tune_vocal ride the fused lane.
5. **Targeted proposals** — one theme per proposal (a masking fight, a level
   story, a vocal seat), never a blanket chain on every lane. The deck's WHY
   feedback rides the next prompt; respect held_back notes.
6. **Finish** — `auto_master(song, genre)` -> `master_report` gate to pass:true.

## Don'ts (all evidenced)

- Don't chain fx on every lane in one take "to be thorough" — that's paint over
  a mix nobody diagnosed, and it reads as FULL REWRITE on the scalpel badge.
- Don't mute/unmute stems vs sketches ad hoc — swaps go through source_swap /
  the detached-sing lane so exactly one voice per part sounds.
- Don't normalize output or push masterGainDb — staging happens at sources and
  trims (mix-headroom law).
- Don't re-transcribe what the import already measured: bpm/key/sections/groove
  and the Reference DNA are all banked; re-measure only NEW renders.
