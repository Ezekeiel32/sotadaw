#!/usr/bin/env python3
"""dj_mix.py — THE AI DJ primitive: beat-matched blend of two songs.

  dj_mix.py deck_a.wav deck_b.wav <out_name> [--bpm N] [--bpm-a N] [--bpm-b N]
            [--blend-bars 8] [--gain-a 0] [--gain-b 0]

Both decks are WARPED (sourceBpm) onto one tempo grid, so beat-match is exact by
construction. The blend is phrase-aligned (4-bar snapped) with the classic DJ
transition: incoming deck rides the highpass side of fx_djfilter (bass killed),
gains crossfade linearly in dB, and at the swap point the bass changes hands —
outgoing deck's lows are killed the moment the incoming deck's arrive.

All output is a plain song.json: every automation point of the transition is
inspectable and editable, in the DAW or by the agent. No black box."""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stems_import import estimate_bpm


def wav_seconds(path):
    import wave
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        import soundfile as sf
        info = sf.info(path)
        return info.frames / float(info.samplerate)


NOTE_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
           "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def deck_key(path):
    """(key, camelot, confidence) via analyze2's Krumhansl-Schmuckler estimator."""
    import numpy as np
    import soundfile as sf
    from analyze2 import estimate_key
    x, sr = sf.read(path, always_2d=True)
    key, conf = estimate_key(x.mean(axis=1), sr)
    if not key or conf < 0.15:
        return key, None, conf
    note, mode = key.rsplit(" ", 1)
    pc = NOTE_PC.get(note)
    if pc is None:
        return key, None, conf
    base = (pc - 9) * 7 if mode == "minor" else pc * 7
    num = (base % 12 + 8 - 1) % 12 + 1
    return key, f"{num}{'A' if mode == 'minor' else 'B'}", conf


def harmonic_verdict(ca, cb):
    """Camelot rule: same number, or same letter one step apart, mixes clean."""
    if not ca or not cb:
        return "unknown (low key confidence) — no harmonic constraint applied"
    na, la, nb, lb = int(ca[:-1]), ca[-1], int(cb[:-1]), cb[-1]
    if na == nb:
        return f"{ca} x {cb}: COMPATIBLE (same slot/relative)"
    if la == lb and (na % 12 + 1 == nb or nb % 12 + 1 == na):
        return f"{ca} x {cb}: COMPATIBLE (adjacent on the wheel)"
    return (f"{ca} x {cb}: KEY CLASH — shorten the blend or filter one deck hard "
            f"(fx_djfilter knob +/-0.7 throughout)")


def rms_db(path):
    """Whole-file RMS in dB — the deck trim reference (real DJs gain-match channels)."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    x = x.mean(axis=1)
    return float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9))


def build_mix(a_path, b_path, name, bpm=None, bpm_a=None, bpm_b=None,
              blend_bars=8, gain_a=0.0, gain_b=0.0):
    a_path, b_path = os.path.abspath(a_path), os.path.abspath(b_path)
    if bpm_a is None:
        bpm_a, ca = estimate_bpm(a_path)
    else:
        ca = 1.0
    if bpm_b is None:
        bpm_b, cb = estimate_bpm(b_path)
    else:
        cb = 1.0
    target = float(bpm or bpm_a)

    key_a, cam_a, kca = deck_key(a_path)
    key_b, cam_b, kcb = deck_key(b_path)
    harmonic = harmonic_verdict(cam_a, cam_b)

    # gain-match the decks (trim B to A's level, clamp +/-12 dB) — a 6 dB level
    # jump at the handover reads as a mistake no matter how tight the beat-match
    trim_b = max(-12.0, min(12.0, rms_db(a_path) - rms_db(b_path)))
    gain_b = gain_b + trim_b

    # warp maps source-beats onto timeline-beats 1:1 — all arithmetic in beats
    len_a = wav_seconds(a_path) * bpm_a / 60.0
    len_b = wav_seconds(b_path) * bpm_b / 60.0
    blend = blend_bars * 4.0
    if len_a < blend + 16:
        blend = max(8.0, (len_a // 8) * 4 / 2)   # short deck A: shrink the blend
    b_start = max(0.0, math.floor((len_a - blend) / 16.0) * 16.0)  # 4-bar phrase snap
    b_end = b_start + blend
    swap = b_start + round(blend / 8.0) * 4.0    # bass swap: blend midpoint, bar-snapped
    swap = min(max(swap, b_start + 4.0), b_end - 4.0)

    rel = lambda p: os.path.relpath(p, ROOT) if p.startswith(ROOT) else p
    deck = lambda dname, path, sbpm, g: {
        "name": dname, "source": {"kind": "audio", "id": dname}, "gainDb": g,
        "fx": [{"id": "fx_djfilter", "params": {"knob": 0.0, "res": 1.1}}],
        "notes": [],
        "audioClips": [{"file": rel(path), "startBeat": 0.0 if dname == "deck_a" else b_start,
                        "sourceBpm": round(sbpm, 2)}]}
    da, db = deck("deck_a", a_path, bpm_a, gain_a), deck("deck_b", b_path, bpm_b, gain_b)

    # NB: a gainDb automation curve OVERRIDES the static track gain — the deck
    # trims must live INSIDE the fade values or they silently vanish
    # staggered handover (no energy valley): B reaches FULL level BY the bass
    # swap; A holds full until the swap, then exits. One deck is always carrying.
    da["automation"] = [
        {"target": "gainDb", "points": [{"beat": 0, "v": gain_a}, {"beat": swap, "v": gain_a},
                                        {"beat": b_end, "v": -60}]},
        {"target": "fx[0].knob", "points": [{"beat": b_start, "v": 0.0}, {"beat": swap, "v": 0.0},
                                            {"beat": swap + 0.25, "v": 0.5}]}]  # A's bass leaves
    db["automation"] = [
        {"target": "gainDb", "points": [{"beat": b_start, "v": round(-21 + gain_b, 1)},
                                        {"beat": swap, "v": round(gain_b, 1)}]},
        {"target": "fx[0].knob", "points": [{"beat": b_start, "v": 0.62},        # lows held back
                                            {"beat": swap - 0.25, "v": 0.62},
                                            {"beat": swap, "v": 0.0}]}]          # BASS DROPS IN

    total_beats = b_start + len_b
    song = {"version": 2, "bpm": round(target, 2), "lengthBars": int(math.ceil(total_beats / 4.0)),
            "masterGainDb": 0.0,
            "master": [{"id": "fx_brickwall", "params": {"ceiling": -1.0}}],
            "sections": [{"name": "deck A", "startBar": 0},
                         {"name": "blend", "startBar": int(b_start // 4)},
                         {"name": "deck B", "startBar": int(b_end // 4)}],
            "tracks": [da, db]}
    out = os.path.join(ROOT, "songs", f"{name}.json")
    json.dump(song, open(out, "w"), indent=1)
    plan = (f"deck A {bpm_a:.1f}bpm (conf {ca:.2f}) x deck B {bpm_b:.1f}bpm (conf {cb:.2f}) "
            f"-> {target:.1f}bpm grid | blend bars {int(b_start//4)}-{int(b_end//4)} "
            f"({int(blend//4)} bars), bass swap at bar {int(swap//4)} | deck B trim "
            f"{trim_b:+.1f} dB (gain-matched) | {song['lengthBars']} bars total"
            f"\n[dj] harmonic: A={key_a or '?'} B={key_b or '?'} -> {harmonic}")
    print(f"[dj] {out}\n[dj] {plan}")
    return out, plan


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("deck_a"); ap.add_argument("deck_b"); ap.add_argument("name")
    ap.add_argument("--bpm", type=float, default=None, help="target grid (default: deck A's bpm)")
    ap.add_argument("--bpm-a", type=float, default=None)
    ap.add_argument("--bpm-b", type=float, default=None)
    ap.add_argument("--blend-bars", type=int, default=8)
    ap.add_argument("--gain-a", type=float, default=0.0)
    ap.add_argument("--gain-b", type=float, default=0.0)
    a = ap.parse_args()
    build_mix(a.deck_a, a.deck_b, a.name, a.bpm, a.bpm_a, a.bpm_b,
              a.blend_bars, a.gain_a, a.gain_b)
