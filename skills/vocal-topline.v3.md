---
name: vocal-topline
version: 3
kind: performance
tags: [vocals, sing, hum, topline, lyrics, voice, words]
hard_constraints:
  - "ATTRIBUTION RIDES EVERY SUNG DELIVERABLE: the voice is 'Gahata Meiji from LUNAI Project' (non-commercial creative use). Say it when you deliver."
  - "hum_topline / sing_lyrics need a MELODY track (default 'lead' — make_track/generate_loop write one). No melody = nothing to sing; make the take first."
  - "lyrics[] word count must equal the melody's note count EXACTLY per section (one word per note, {beat, text}). Count phrases from the note map FIRST, then write."
  - "On IMPORTED records the sung take lands on 'vocals_sung' and NEVER clobbers the record's own 'vocals' stem (truth outranks synth)."
  - "The rail self-heals vocoder memory pressure (windows split + retry). If it still exits with the 1-note-floor line, free RAM and retry — never ship a half-sung take."
---
# The vocal topline (make the DAW sing)

When the ask mentions vocals / singing / a topline / "with a voice", the take
is not done until it sings. Two rails, both landing a REPLACEABLE audio track
(the melody stays the edit surface). **WORDS FIRST** — the arrangement-level
ladder (below) puts real words above the hum above silence, every time it has
been measured.

## 1. Real words — write lyrics[], then `sing_lyrics` (the default rail)
1. Run `use_tool(phrase_map, {"song": ..., "track": "lead"})` (or
   tools/phrase_map.py) — it prints the EXACT word count + phrase shape per
   section AND names the shared hook shapes. Never hand-count.
2. Write `lyrics[]` = `[{beat: note_start, text: word}]` — ONE word per note.
   Monosyllables sing cleanest. The HOOK sings the SAME words every chorus
   (that repetition is what makes it a song); verses may vary.
3. `sing_lyrics(song, track)` renders and lands the vocal, level-matched.

Short on time or words? `tools/lyric_bank.py` holds seeded family-routed
phrase streams (bright/warm/dark/drift) — the zero-token words the MAKE
button sings. Your OWN writing outranks the bank; the bank outranks a hum.

## 2. Instant wordless hook — `hum_topline` (the fallback)
`hum_topline(song, track="lead", syllable=...)` sings a neutral syllable on
every melody note. Deterministic, no lyrics needed, ~1s of synthesis per 2.5s
of voice. Use when the ask is explicitly wordless or the melody is still in
flux. **Syllable is a genre statement:**
- pop / synth genres — `ooh` (the airy pad vowel)
- gospel / soul / rnb — `oh` (the open church vowel)
- laid-back / lofi / rnb verses — `mmm`
- dance / chant cultures — `ey` or `ah`

## The measured truth (2026-07-11, both levels)
Loop level: instrumental CLAP 0.5253 → hum 0.5339 → real words 0.5455.
ARRANGEMENT level (psybient, CLAP AB vs real records): loop 0.5041/68.6-close
→ full arrangement 0.5288/72.0 → +hum 0.5741/78.1 → **+WORDS 0.5899/80.3 —
the board's crown**. The voice is the biggest single realism lever and words
are the top of the voice; it also fills the 500–2k presence band every mix
critique flags as empty.

## After the voice lands
- The sung lane arrives with comp + delay + a verb send when buses exist —
  check `get_song_summary`; ride its gainDb against the lead if it fights.
- Vocal-forward genres may ease the lead −2 dB under the voice (the voice IS
  the topline now; the instrument becomes the double).
