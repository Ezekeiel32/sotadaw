#!/usr/bin/env python3
"""CHORDS FROM THE SYMBOLS — bar-wise chord voting over a song's own notes.

  chordvote.py <song> [--write] [--tracks a,b]

The firing-31 verdict: audio-HMM harmony fails our material (maj/min vocabs
meet all-dominant blues; drums bury chroma). But this DAW OWNS the symbols —
imports carry basic-pitch sketches + a bass stem, authored songs carry truth.
So: per bar, weigh every sounding pitch class (duration x velocity, bass
witnesses x2.5 — keyvote's method, per-bar), score maj/min templates on every
root, read the b7 for dominant color ('7' suffix). Zero deps, drum-proof
(drum tracks skipped by name/kit), sustained notes credited per-bar slice.

--write persists song["chords"] = [{"bar", "chord", "conf"}] — a chord lane
the agent and UI can read (the Logic-11 chord-track law, populated by vote).
Machine line: CHORDS_JSON {...}
"""
import argparse, json, os, re, sys
import songname

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PC = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
DRUMISH = re.compile(r"drum|kick|snare|hat|perc|clap|shaker|cymbal|tom|ride|crash|808$", re.I)


def is_drum_track(t):
    name = str(t.get("name", ""))
    src = t.get("source", {}) or {}
    sid = str(src.get("id") or src.get("kit") or "")
    if DRUMISH.search(name) or DRUMISH.search(sid):
        return True
    return src.get("kind") == "sample" and "drum" in sid.lower()


def bar_weights(song, tracks_filter=None):
    """per-bar pitch-class weight vectors (+ separate bass witness vectors)."""
    bars = int(round(float(song.get("lengthBars", 4))))
    W = [[0.0] * 12 for _ in range(bars)]
    B = [[0.0] * 12 for _ in range(bars)]
    for t in song.get("tracks", []):
        sketch = "sketch" in str(t.get("name", "")).lower()
        if is_drum_track(t) or (t.get("muted") and not sketch):
            continue                       # muted SKETCHES still vote: on imports
                                           # they are the only symbols we have
        if tracks_filter and t.get("name") not in tracks_filter:
            continue
        notes = t.get("notes", [])
        if not notes:
            continue
        med = sorted(n["pitch"] for n in notes)[len(notes) // 2]
        bassy = ("bass" in str(t.get("name", "")).lower()) or med < 48
        for n in notes:
            s, ln = float(n["start"]), float(n.get("len", 0.25))
            vel = float(n.get("vel", 0.8))
            pc = int(n["pitch"]) % 12
            b = int(s // 4)
            while b < bars and b * 4 < s + ln:
                dur_in = min(s + ln, (b + 1) * 4) - max(s, b * 4)
                if dur_in > 0:
                    W[b][pc] += dur_in * vel
                    if bassy:
                        B[b][pc] += dur_in * vel
                b += 1
    return W, B


def vote_bar(w, b):
    tot = sum(w) + 1e-9
    best = (-1e9, None, None)
    for r in range(12):
        for q, third in (("maj", 4), ("min", 3)):
            other = 3 if q == "maj" else 4
            score = (1.5 * w[r] + 2.5 * b[r]                  # root (+bass witness)
                     + 1.2 * w[(r + third) % 12]
                     + 0.8 * w[(r + 7) % 12]
                     + 0.35 * w[(r + 10) % 12]                # b7 = color, mild pull
                     - 0.8 * w[(r + other) % 12]
                     - 0.5 * b[(r + 1) % 12] - 0.5 * b[(r + 11) % 12])
            if score > best[0]:
                best = (score, r, q)
    _, r, q = best
    if r is None or tot < 0.2:
        return None, 0.0
    dom7 = w[(r + 10) % 12] > 0.22 * (w[r] + 1e-9) and q == "maj"
    label = PC[r] + ("" if q == "maj" else "m") + ("7" if dom7 else "")
    conf = round(min(1.0, best[0] / (3.5 * tot)), 2)
    return label, conf


def chord_map(song, tracks_filter=None, audio_wav=None, audio_bpm=None, audio_gain=1.0):
    """Bar-wise chords from the song's SYMBOLS, optionally FUSED with an AUDIO
    witness (V54): audio_wav's per-bar CQT chroma is scaled to each bar's symbolic
    magnitude and ADDED to W/B, so a demucs harmonic stem reinforces the vote where
    transcription is weak. Best-effort — a missing/unreadable wav is ignored (the
    symbolic vote alone still returns). Backward-compatible: audio_wav=None = old."""
    W, B = bar_weights(song, tracks_filter)
    if audio_wav:
        try:
            import chords_audio
            bpm = float(audio_bpm or song.get("bpm", 120))
            AW, AB = chords_audio.chroma_per_bar(audio_wav, bpm, len(W))
            for i in range(len(W)):
                aw = chords_audio._scale(AW[i], (sum(W[i]) or 4.0) * audio_gain)
                ab = chords_audio._scale(AB[i], (sum(B[i]) or 2.5) * audio_gain)
                W[i] = [W[i][k] + float(aw[k]) for k in range(12)]
                B[i] = [B[i][k] + float(ab[k]) for k in range(12)]
        except Exception:
            pass                                   # audio witness is best-effort
    out = []
    for i, (w, b) in enumerate(zip(W, B)):
        label, conf = vote_bar(w, b)
        if label:
            out.append({"bar": i + 1, "chord": label, "conf": conf})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--write", action="store_true", help="persist song['chords']")
    ap.add_argument("--tracks", default=None, help="comma-separated track filter")
    ap.add_argument("--all", action="store_true", help="machine line carries EVERY bar (rail food), not the 16-bar preview")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    tf = [x.strip() for x in a.tracks.split(",")] if a.tracks else None
    chords = chord_map(song, tf)
    run = []
    for c in chords:                                  # compress runs for reading
        if run and run[-1][1] == c["chord"]:
            run[-1][2] = c["bar"]
        else:
            run.append([c["bar"], c["chord"], c["bar"]])
    print(f"[chordvote] {name}: " + "  ".join(
        (f"{a0}-{b0}" if b0 > a0 else f"{a0}") + f":{ch}" for a0, ch, b0 in run))
    if a.write:
        song["chords"] = chords
        json.dump(song, open(path, "w"), indent=1)
        print(f"[chordvote] chords[] written into songs/{name}.json")
    print("CHORDS_JSON " + json.dumps({"song": name, "bars": len(chords),
                                       "chords": chords if a.all else chords[:16]}))


if __name__ == "__main__":
    main()
