---
name: band-seat
version: 2
kind: performance
tags: [jam, band, live-jam, band-member, follow, session, play-along, improvise]
hard_constraints:
  - "The human OWNS the root: any follow context (their pitch classes) automatically silences the harmonic journey and masks the band's voicing. Never fight the soloist's key — and never 'fix' it afterward by transposing jam: lanes."
  - "ZERO TOKENS in the loop: jam/jam_live's brain is pure math + the KG. Your job is the EDGES — map the user's words to genre + vibe arc + follow weight, then let the machinery play. Never micro-drive phrase decisions with repeated tool calls."
  - "A kept take reaches the BASE SONG only through keep_jam -> proposal -> user accept (the verb lane wires this). Never write jam material into a song file directly."
  - "After keep_jam the take's FEEL rides the song's tempo (beats carry exactly); a >1 bpm delta is called out in the tool reply — SURFACE it to the user, never silently retempo either side."
  - "B6 THE ROOM'S WORLD: when the user is jamming OVER an existing song, pass its bpm + key to jam/jam_live — the band must enter the room's world, not the DNA's. Key transposes harmonic rungs only (drums sacred); an unparseable key transposes nothing and never lies about the label."
---

# THE BAND SEAT — leading the AI band member (docs/THE_BAND_SEAT.md is the constitution)

## The decision tree (what the user said -> which door)
- "jam WITH me / I'll play along" (hardware in the room): the APP is the door —
  Live view, THE JAM POD: its own genre box + vibe box (both LIVE mid-set),
  JAM = an ENDLESS set; pressing again ends ON the phrase and the take is
  ALWAYS kept (press while ENDING = discard). MIC toggles the audio ear at the
  room ANY time, mid-set included; BAND level balances the band vs the player.
  You PREPARE (genre, vibe) and explain the pod.
- "make the band jam / N phrases of X": `jam {genre, vibe, phrases, seed?}` —
  a full composed take, journey + pocket-evolution on, faster than realtime.
  Add `bpm`/`key` when the jam should live in an existing song's world.
- "jam around my riff / my take": get the riff as NOTES first — a Rec take
  already is; an audio take goes through `audio_follow` (file mode; `--f0 fcpe`
  for wet/reverby sources) into a notes JSONL. Then
  `jam {genre, vibe, human: <file>, follow: 0.5-0.8}`.
- realtime behavior itself (scheduling, latency): `jam_live` — same follow
  surface plus `bars` (phrase length; the conversation law may shorten it)
  and `bpm`/`key`. CLI-only extras: `--phrases 0` = endless until
  `<ipc>/stop`; `<ipc>/vibe.txt` = live arc switch (the UI pod drives both).

## What the band hears in a human file (the follow surface)
density (busy -> 1-bar answers, SPACE: melody comps out), energy (target bend
+ TOUCH: the band's velocities shade to the player's), pitch_classes (voicing
snaps <=2 semitones; the journey pauses), swing (the band stamps the human's
measured feel), register. Beats are SET-RELATIVE: 0 = the set's downbeat;
pre-roll noodling at negative beats steers the opener too.

## Keeping what was played
A finished OR stopped set self-keeps as `jam_<genre>_<n>.json` (the graceful
STOP keeps; the take also autosaves every phrase, so even a crash leaves the
tape). `keep_jam {song, take, at_bar?}` merges it INTO the working song as
`jam:<role>` lanes + a section marker — notes AND automation beat-offset,
sends filtered to real buses, receipts filed. Driven through the verb lane it
lands as a NORMAL PROPOSAL: ghosts on lanes, the deck decides, accept is the
one door.

## Mapping words to the machinery (vibe is an ENERGY ARC, nothing else)
"build it up slowly" -> build (phrases 8+) · "keep it rolling" -> steady ·
"take it up then bring it home" -> wave · "wind it down" -> breakdown ·
"push to a peak" -> peak. Dark/bright/moody words are NOT vibes — they are
genre/brightness choices (pick the darker genre, or say what you chose).
In an ENDLESS set build/breakdown are one-shot journeys (8 phrase-equivalents,
then hold) and wave cycles — a live vibe switch restarts the arc from the
switch, which is exactly how the user rides it.
`follow`: 0.3 = the band mostly keeps its own arc, 0.8 = glued to the player.
