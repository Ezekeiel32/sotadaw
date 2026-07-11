#!/usr/bin/env python3
"""INFILL_REGION — regenerate a track's chosen BARS, conditioned on context.

  infill_region.py <song> <track> <from_bar> <to_bar> [--seed N] [--write]

The MIDI-GPT lane (AAAI 2025, deep-research firing 66), adopted SYMBOLICALLY:
"infill musical material at the track and bar level, conditioned on surrounding
context." No trained model (the free-diffusion shortcut was refuted) — we
condition on what we already extract: the WINDOW'S CHORDS (harmony continuity),
the SURROUNDING density on this track (feel continuity), and the track's ROLE
+ register. Only the window changes; everything else is byte-identical.

Spec (battery-verified, verify-100% discipline):
  I1 only [from_bar,to_bar) on <track> changes; all else byte-identical
  I2 regenerated notes fall inside the window
  I3 new notes play the window's chords (chord-tone rate on strong beats)
  I4 density continuity: within 0.5x-2x of the surrounding bars' notes/bar
  I5 valid song, renders clean
  I6 deterministic per seed; seed varies
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map
import harmonize as H
import automix as M
import songname

GEN = {"bass": H.bass_notes, "pad": H.pad_notes, "melody": H.melody_notes,
       "focal": H.melody_notes, "other": H.melody_notes}
DEFRHY = {"bass": "straight", "pad": "whole", "melody": "flowing",
          "focal": "flowing", "other": "flowing"}


def infill(song, track_name, from_bar, to_bar, seed=0, density=None, duration=None, style=None):
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None:
        raise SystemExit(f"no track '{track_name}'")
    if tr.get("locked"):
        raise SystemExit(f"track '{track_name}' is LOCKED")
    # STYLE APPLY (personalization loop's third verb): a fingerprint's per-role
    # density + register bias generation toward the producer's signature. Explicit
    # density=/register still win; style fills what they leave unset.
    style_reg = None
    if style is not None:
        srole = M.role(tr)
        rstats = (style.get("roles", {}) or {}).get(srole) or (style.get("roles", {}) or {}).get("other")
        if rstats:
            if density is None:
                density = rstats.get("density")
            style_reg = rstats.get("register")
    a, b = float(from_bar - 1) * 4.0, float(to_bar) * 4.0      # window in beats (1-indexed bars)
    chords = song.get("chords") or chord_map(song)
    if not chords:
        raise SystemExit("no chords to condition on")
    win_chords = [c for c in chords if a <= (c["bar"] - 1) * 4.0 < b]
    if not win_chords:
        raise SystemExit(f"no chords in bars {from_bar}..{to_bar}")
    # re-index window chords to bar 1.. for the generator, remember the offset
    off_bar = int(a // 4)
    gen_chords = [{"bar": c["bar"] - off_bar, "chord": c["chord"], "conf": c.get("conf", 0.9)}
                  for c in win_chords]

    role = M.role(tr)
    # CONTEXT: register + density of this track OUTSIDE the window
    outside = [n for n in tr.get("notes", []) if not (a <= n["start"] < b)]
    if outside:
        pitches = sorted(n["pitch"] for n in outside)
        base = pitches[len(pitches) // 2]                     # median register anchor
        span_bars_out = max(1.0, float(song.get("lengthBars", 1)) - (to_bar - from_bar + 1))
        dens = len(outside) / span_bars_out                    # notes/bar around it
    else:
        base = H.BASE.get(role, 60)
        dens = 4.0
    if style_reg is not None:
        base = int(round(style_reg))                          # the fingerprint's register wins
    gen = GEN.get(role, H.melody_notes)
    rhythm = DEFRHY.get(role, "flowing")
    # EXPLICIT density attribute (MIDI-GPT's effective control) overrides context;
    # else the surrounding density picks the feel
    eff_dens = float(density) if density is not None else dens
    if role in ("melody", "focal", "other"):
        rhythm = "busy" if eff_dens > 6 else ("sparse" if eff_dens < 2 else "flowing")
    elif role == "bass" and density is not None:
        rhythm = "roll" if eff_dens > 5 else ("offbeat" if eff_dens > 3 else "straight")
    elif role == "pad" and density is not None:
        rhythm = "pulse" if eff_dens > 3 else "whole"
    if role == "melody" or gen is H.melody_notes:
        new = H.melody_notes(gen_chords, base, rhythm, seed)
    else:
        new = gen(gen_chords, base, rhythm)
    # shift generated notes into the window's absolute position; clamp to window.
    # EXPLICIT duration attribute (MIDI-GPT's other effective control) scales note
    # lengths (clamped so a note never runs past the window or overlaps its bar).
    dscale = float(duration) if duration is not None else 1.0
    placed = []
    for n in new:
        s = round(n["start"] + a, 4)
        if a <= s < b:
            ln = round(min(n["len"] * dscale, b - s), 4) if dscale != 1.0 else n["len"]
            placed.append(dict(n, start=s, len=max(0.05, ln)))
    # replace ONLY the window's notes on this track
    tr["notes"] = [n for n in tr.get("notes", []) if not (a <= n["start"] < b)] + placed
    tr["notes"].sort(key=lambda n: n["start"])
    return {"track": track_name, "role": role, "bars": f"{from_bar}..{to_bar}",
            "new_notes": len(placed), "context_density": round(dens, 1),
            "rhythm": rhythm, "chords": [c["chord"] for c in win_chords[:8]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("track")
    ap.add_argument("from_bar", type=int); ap.add_argument("to_bar", type=int)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--density", type=float, default=None, help="target notes/bar (MIDI-GPT control)")
    ap.add_argument("--duration", type=float, default=None, help="note-length scale (MIDI-GPT control)")
    ap.add_argument("--style", default=None, help="style fingerprint name (personalization)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    style_fp = None
    if a.style:
        import glob
        sp = os.path.join(ROOT, "songs", f"_style_{re.sub(r'[^a-z0-9_]','',a.style.lower())}.json")
        if os.path.exists(sp):
            style_fp = json.load(open(sp))
    rep = infill(song, a.track, a.from_bar, a.to_bar, a.seed, a.density, a.duration, style_fp)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
        rep["written"] = f"songs/{name}.json"
    print(f"[infill] {rep['track']} ({rep['role']}) bars {rep['bars']}: {rep['new_notes']} "
          f"new notes, {rep['rhythm']} feel (context {rep['context_density']} n/bar), "
          f"over {' '.join(rep['chords'])}" + (f" -> {rep['written']}" if a.write else ""))
    print("INFILL_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
