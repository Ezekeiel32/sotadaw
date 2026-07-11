---
name: live-performance
version: 1
kind: workflow
tags: [always, performance, scenes, live]
hard_constraints:
  - Scene stories are AUTHORED THEN VERIFIED: after set_clip_slot writing, scene_bounce at least the drop scene and confirm it hits (analysis attached to the bounce).
  - Every performable session ships the strip staples: scene_strips(song) after the scene story is written (Drums only / No drums / Bass+Drums) — the performer's panic buttons.
  - Scene columns tell ONE story left-to-right (groove bed -> build -> drop -> strips at the end); name every scene.
---
# The live-performance workflow (scenes → strips → bounce → hands)

The DAW's launcher is a playable instrument: pads launch scenes (MIDI hands are live),
jam-capture turns a performance back into editable notes. The agent's job is to hand the
human a PLAYABLE story, verified by ear.

## The flow
1. **Author the story**: set_clip_slot per track × scene — scene 0 = groove bed, 1 = build
   (add layers/risers), 2 = drop (full weight), 3+ = variations. scene_name each one.
   Audio loops go in with audio_file + source_bpm (warped to the song grid).
2. **Add the panic buttons**: scene_strips(song) — appends Drums-only / No-drums /
   Bass+Drums from the fullest column. These are what a performer reaches for mid-set.
3. **Verify by ear**: scene_bounce(song, scene) for the drop and any scene you're unsure
   of — the render+analysis is the proof the story lands (builds grow, drops hit).
4. **Hand it over**: the human performs in the Live view; jam-capture records their scene
   launches as an arrangement. That captured take is editable notes — treat a re-prompt
   over it as an edit of THEIR performance, not yours.

## Loop-machine sessions
build_loop_machine output is already a story (Drums -> +Bass -> +Keys -> FULL);
scene_strips extends it; loop_variations(song, track, ...) fills empty columns with
6 instant variations when the performer wants more material.

## Taste
- 4-8 scenes is a set; 16 is a mess.
- Strips come LAST in the column order (performance tools, not story beats).
- A drop scene that bounces quieter than the build is a bug — fix weights before shipping.
