#!/usr/bin/env python3
"""THE WORDS battery — beat mapping must ride the surgical TempoClock (tempoMap
included), lyric landing must clamp to the song, --find must be case/punctuation
blind, absence must degrade clean, and the REAL leg (SKIP-green without the ASR
runtime) must transcribe an actual rap stem into monotonic beat-stamped words
that land as write_lyrics-shaped lyrics[].
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))
from lyrics_from_audio import map_words, to_lyrics, find_word, _clock

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


# 1-2 beat mapping through the surgical clock — flat grid then a tempoMap step
flat = _clock({"bpm": 120.0, "lengthBars": 64})
w = map_words([{"text": " go ", "start": 2.0, "end": 2.5, "prob": 0.9}], flat)[0]
ok(abs(w["beat"] - 4.0) < 1e-6 and abs(w["beats"] - 1.0) < 1e-6 and w["text"] == "go",
   "flat 120: word at 2.0s lands on beat 4, half a second = 1 beat, text stripped")

stepped = _clock({"bpm": 120.0, "lengthBars": 64,
                  "tempoMap": [{"bar": 1, "bpm": 60, "curve": 1}]})
w = map_words([{"text": "later", "start": 3.0, "end": 3.0, "prob": 1.0}], stepped)[0]
ok(abs(w["beat"] - 5.0) < 1e-3,
   f"tempoMap step 120->60 at bar 1: 3.0s = beat 5 (the clock integrates, got {w['beat']})")

# 3 lyric landing clamps to the song
lines = [{"beat": 0.0, "text": " first "}, {"beat": 8.0, "text": "second"},
         {"beat": 99.0, "text": "outside"}, {"beat": 4.0, "text": ""}]
lyr, outside = to_lyrics(lines, 16.0)
ok(lyr == [{"beat": 0.0, "text": "first"}, {"beat": 8.0, "text": "second"}] and outside == 1,
   "lyrics land sorted+stripped inside the song; the outside line is counted, empty dropped")

# 4 find: case + punctuation blind, occurrence-numbered
words = map_words([{"text": " Yeah,", "start": 0.5, "end": 0.7, "prob": .8},
                   {"text": "go", "start": 1.0, "end": 1.2, "prob": .9},
                   {"text": " yeah!", "start": 2.0, "end": 2.2, "prob": .7}], flat)
hits = find_word(words, "YEAH")
ok(len(hits) == 2 and hits[0]["n"] == 1 and abs(hits[1]["beat"] - 4.0) < 1e-6,
   "--find 'YEAH' matches 'Yeah,' and 'yeah!' — the second at beat 4")

# 5 determinism of the pure surface
a = json.dumps({"w": map_words(
    [{"text": "x", "start": 1.0, "end": 1.5, "prob": 0.5}], flat)}, sort_keys=True)
b = json.dumps({"w": map_words(
    [{"text": "x", "start": 1.0, "end": 1.5, "prob": 0.5}], flat)}, sort_keys=True)
ok(a == b, "deterministic: same words, same grid, byte-identical")

# 6 absence degrades clean
from lyrics_from_audio import hear_words
out = hear_words(os.path.join(ROOT, "songs", "_no_such.wav"), model="__no_such_model__")
ok(out["available"] is False and "unavailable" in out["reason"].lower() or not out["available"],
   "a dead runtime/model returns available:false, never a traceback")

# 7-10 REAL leg: an actual rap stem onto its actual grid (SKIP without runtime)
stem = os.path.join(ROOT, "songs", "_anxrofo_stems", "vocals.wav")
sj = os.path.join(ROOT, "songs", "_anxrofo.json")
ran = False
if os.path.exists(stem) and os.path.exists(sj):
    try:
        import faster_whisper  # noqa: F401
        song = json.load(open(sj))
        out = hear_words(stem, song=song, model="small")
        if out.get("available"):
            ran = True
            ws = out["words"]
            ok(len(ws) >= 30 and len(out["lines"]) >= 5,
               f"real rap stem: {len(ws)} words / {len(out['lines'])} lines heard")
            ok(all(ws[i]["start_s"] <= ws[i + 1]["start_s"] + 0.5 for i in range(len(ws) - 1))
               and all(0 <= w["conf"] <= 1 for w in ws)
               and all(w["beat"] >= 0 for w in ws),
               "words near-monotonic, confidences in [0,1], beats non-negative")
            total = float(song.get("lengthBars", 4)) * 4.0
            lyr, _ = to_lyrics(out["lines"], total)
            ok(len(lyr) >= 5 and all(
                isinstance(l["beat"], float) and 0 <= l["beat"] < total and l["text"]
                for l in lyr),
               f"{len(lyr)} lines land write_lyrics-shaped inside the {total:.0f}-beat song")
            bpm = float(song.get("bpm", 120))
            last_ok = ws[-1]["beat"] <= (out["duration_s"] / 60.0 * bpm) * 1.05 + 4
            ok(last_ok, f"grid honesty: last word beat {ws[-1]['beat']} consistent with "
                        f"{out['duration_s']}s at {bpm} bpm")
    except ImportError:
        pass
if not ran:
    for m in ["real leg SKIP (faster-whisper absent) — pure legs carry the law"] * 4:
        ok(True, m)

# 11 CLI leg with --find on the same stem (cheap re-use via cached model) — pure
#    CLI shape only when the runtime exists; else SKIP
if ran:
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lyrics_from_audio.py"),
                        stem, "--song", "_anxrofo", "--model", "small"],
                       capture_output=True, text=True, cwd=ROOT, timeout=1800)
    line = next((l for l in r.stdout.splitlines() if l.startswith("WORDS_JSON ")), "")
    j = json.loads(line[11:]) if line else {}
    ok(r.returncode == 0 and j.get("available") and j["n_words"] == len(j["words"]),
       f"CLI leg: WORDS_JSON parses, {j.get('n_words')} words, rc=0")
else:
    ok(True, "CLI leg SKIP (runtime absent)")

print(f"PASS {N}/{N} lyrics_from_audio battery")
