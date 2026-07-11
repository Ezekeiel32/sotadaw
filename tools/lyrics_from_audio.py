#!/usr/bin/env python3
"""THE WORDS — a recorded vocal becomes beat-timed lyrics (ASR onto the grid).

  lyrics_from_audio.py <vocal.wav> [--song name] [--write] [--find "word"]
                       [--model small] [--language xx] [--cpu]

The DAW sings (sing.py) and tunes (retune.py) but could not HEAR WORDS: an
imported vocal stem had melody sketches and no text. This rail transcribes it
(faster-whisper, word timestamps, GPU->CPU elastic) and lands every word on the
song's OWN grid via the surgical TempoClock (bpm + tempoMap integration — the
same clock locate uses). Lines are whisper segments; --write lands them as
song.lyrics[] = [{beat, text}] — exactly write_lyrics's shape, so the imported
song's words become editable, alignable (align_lyrics) and re-singable (sing.py).
--find "word" answers "where is the second 'yeah'" in beats — locate for words.

Degrades clean (exit 3, available:false) when the ASR runtime is absent.
Honesty: sung/rapped ASR is imperfect — every word carries its confidence, and
nothing asserts text it isn't sure of; the beats are the product, the words are
evidence. Machine line: WORDS_JSON {...}
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))


def _clock(song):
    from surgical import TempoClock
    return TempoClock(song)


# ------------------------------------------------------------------ pure kernel
def map_words(raw_words, clock):
    """[{text,start,end,prob}] + TempoClock -> beat-stamped words (sorted)."""
    out = []
    for w in sorted(raw_words, key=lambda q: float(q["start"])):
        s, e = float(w["start"]), float(w["end"])
        b0, b1 = clock.beat_at(s), clock.beat_at(max(e, s))
        out.append({"text": str(w["text"]).strip(), "start_s": round(s, 3),
                    "end_s": round(e, 3), "beat": round(b0, 3),
                    "beats": round(max(0.0, b1 - b0), 3),
                    "conf": round(float(w.get("prob", 1.0)), 3)})
    return out


def to_lyrics(lines, total_beats):
    """lines [{beat,text}] -> song.lyrics[] entries inside the song + drop count."""
    keep, outside = [], 0
    for ln in lines:
        b, t = float(ln["beat"]), str(ln["text"]).strip()
        if not t:
            continue
        if 0 <= b < total_beats:
            keep.append({"beat": round(b, 3), "text": t})
        else:
            outside += 1
    return sorted(keep, key=lambda l: l["beat"]), outside


def find_word(words, query):
    """case/punctuation-insensitive word match -> occurrences with beats."""
    q = re.sub(r"[^\w']", "", query.lower())
    hits = []
    for i, w in enumerate(words):
        if re.sub(r"[^\w']", "", w["text"].lower()) == q:
            hits.append({"n": len(hits) + 1, "index": i, "beat": w["beat"],
                         "beats": w["beats"], "start_s": w["start_s"], "conf": w["conf"]})
    return hits


# ------------------------------------------------------------------ ASR engine
def transcribe(path, model="small", language=None, cpu=False):
    """-> (raw_words, lines_raw, meta) or raises. GPU->CPU elastic."""
    from faster_whisper import WhisperModel
    last = None
    tries = [("cpu", "int8")] if cpu else [("cuda", "float16"), ("cpu", "int8")]
    for device, ctype in tries:
        try:
            wm = WhisperModel(model, device=device, compute_type=ctype)
            segs, info = wm.transcribe(path, language=language, word_timestamps=True,
                                       vad_filter=True, condition_on_previous_text=False)
            raw_words, lines = [], []
            for s in segs:
                for w in (s.words or []):
                    raw_words.append({"text": w.word, "start": w.start, "end": w.end,
                                      "prob": w.probability})
                txt = s.text.strip()
                if txt:
                    lines.append({"start": float(s.start), "end": float(s.end), "text": txt})
            meta = {"engine": f"faster-whisper:{device}", "model": model,
                    "language": info.language, "language_prob": round(info.language_probability, 3),
                    "duration_s": round(float(info.duration), 2)}
            return raw_words, lines, meta
        except Exception as e:
            last = e
    raise RuntimeError(f"ASR failed on every device: {last}")


def hear_words(path, song=None, model="small", language=None, cpu=False):
    song = song or {"bpm": 120.0, "lengthBars": 1e9}
    try:
        raw_words, raw_lines, meta = transcribe(path, model=model, language=language, cpu=cpu)
    except Exception as e:
        return {"available": False, "reason": f"ASR unavailable: {e}"}
    clock = _clock(song)
    words = map_words(raw_words, clock)
    lines = [{"beat": round(clock.beat_at(l["start"]), 3), "text": l["text"],
              "start_s": round(l["start"], 3), "end_s": round(l["end"], 3)}
             for l in raw_lines]
    return {"available": True, **meta, "file": os.path.basename(path),
            "n_words": len(words), "words": words, "lines": lines,
            "text": " ".join(l["text"] for l in lines)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--song", default=None, help="song whose grid maps the words (bpm+tempoMap)")
    ap.add_argument("--write", action="store_true", help="land lines as song.lyrics[]")
    ap.add_argument("--find", default=None, help='locate a word: --find "yeah"')
    ap.add_argument("--model", default="small")
    ap.add_argument("--language", default=None)
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()

    song, name, sp = None, None, None
    if a.song:
        import songname
        name = songname.resolve(a.song)
        sp = os.path.join(ROOT, "songs", f"{name}.json")
        song = json.load(open(sp))

    out = hear_words(a.audio, song=song, model=a.model, language=a.language, cpu=a.cpu)
    if not out.get("available"):
        print(f"[words] unavailable: {out.get('reason', '?')}")
        print("WORDS_JSON " + json.dumps(out))
        sys.exit(3)

    print(f"[words] {out['file']}: {out['n_words']} words / {len(out['lines'])} lines "
          f"({out['language']} p={out['language_prob']}, {out['engine']}, {out['duration_s']}s)")
    for ln in out["lines"][:16]:
        print(f"  beat {ln['beat']:8.2f}  {ln['text']}")
    if len(out["lines"]) > 16:
        print(f"  ... {len(out['lines']) - 16} more lines")

    if a.find:
        hits = find_word(out["words"], a.find)
        print(f"[find] '{a.find}' x{len(hits)}: " +
              ", ".join(f"#{h['n']} beat {h['beat']} ({h['start_s']}s)" for h in hits[:12]))
        out["found"] = {"query": a.find, "hits": hits}

    if a.write and song is not None:
        total = float(song.get("lengthBars", 4)) * 4.0
        lyr, outside = to_lyrics(out["lines"], total)
        if lyr:
            song["lyrics"] = lyr
            json.dump(song, open(sp, "w"), indent=1)
            print(f"  WROTE {len(lyr)} lyric lines -> songs/{name}.json"
                  + (f" ({outside} outside the song dropped)" if outside else ""))
        else:
            print("  nothing to write (no lines inside the song)")

    print("WORDS_JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
