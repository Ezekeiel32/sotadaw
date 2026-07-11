#!/usr/bin/env python3
"""STYLE_PROFILE — learn a producer's signature from their songs, score any track.

  style_profile.py extract <song> [<song> ...] [--out name]   # -> a fingerprint JSON
  style_profile.py score <song> <fingerprint.json>            # -> 0-100 match + breakdown

The MIDI-RWKV personalization lane ("learn my style from a handful of files"),
adopted SYMBOLICALLY (no trained model): a fingerprint is the inspectable set of
signatures the campaign already extracts — tempo, chord-quality mix, density &
register per role, groove (NOMML + velocity CV), swing, section count. score()
is a weighted similarity so 'is this on-brand for me?' is a number with receipts.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map, is_drum_track
from reharm import parse_chord
from expressive import nomml_level, expressiveness
import automix as M
import songname


def _role_stats(song):
    """density (notes/bar) and median register per role."""
    bars = max(1.0, float(song.get("lengthBars", 1)))
    out = {}
    for t in song.get("tracks", []):
        if not t.get("notes"):
            continue
        r = "drums" if is_drum_track(t) else M.role(t)
        d = out.setdefault(r, {"n": 0, "pitches": []})
        d["n"] += len(t["notes"])
        d["pitches"] += [n["pitch"] for n in t["notes"]]
    stats = {}
    for r, d in out.items():
        ps = sorted(d["pitches"])
        stats[r] = {"density": round(d["n"] / bars, 2),
                    "register": ps[len(ps) // 2] if ps else 60}
    return stats


def fingerprint_one(song):
    chords = song.get("chords") or chord_map(song)
    qual = {"maj": 0, "min": 0, "dom7": 0}
    for c in chords:
        r, q, d = parse_chord(c["chord"])
        qual["min" if q == "min" else "maj"] += 1
        if d:
            qual["dom7"] += 1
    tot = max(1, len(chords))
    melodic = [t for t in song.get("tracks", []) if not is_drum_track(t) and len(t.get("notes", [])) >= 8]
    nomml = sum(nomml_level(t["notes"])[0] for t in melodic) / max(1, len(melodic))
    velcv = sum(expressiveness(t["notes"]) for t in melodic) / max(1, len(melodic))
    return {"bpm": float(song.get("bpm", 120)),
            "chord_mix": {k: round(v / tot, 3) for k, v in qual.items()},
            "roles": _role_stats(song),
            "groove_nomml": round(nomml, 2), "expr": round(velcv, 1),
            "swing": float(song.get("swing", {}).get("amount", 0.5)) if isinstance(song.get("swing"), dict) else 0.5,
            "sections": len(song.get("sections", []))}


def extract(songs):
    fps = [fingerprint_one(s) for s in songs]
    n = len(fps)
    avg = {"bpm": sum(f["bpm"] for f in fps) / n,
           "chord_mix": {k: round(sum(f["chord_mix"][k] for f in fps) / n, 3) for k in ("maj", "min", "dom7")},
           "groove_nomml": round(sum(f["groove_nomml"] for f in fps) / n, 2),
           "expr": round(sum(f["expr"] for f in fps) / n, 1),
           "swing": round(sum(f["swing"] for f in fps) / n, 3),
           "sections": round(sum(f["sections"] for f in fps) / n, 1),
           "roles": {}, "n_songs": n}
    all_roles = set(r for f in fps for r in f["roles"])
    for r in all_roles:
        present = [f["roles"][r] for f in fps if r in f["roles"]]
        avg["roles"][r] = {"density": round(sum(p["density"] for p in present) / len(present), 2),
                           "register": round(sum(p["register"] for p in present) / len(present))}
    return avg


def score(song, fp):
    """0-100 match; higher = more on-brand. Weighted across dimensions."""
    f = fingerprint_one(song)
    parts = {}
    # tempo: within 8% = full; ratio distance
    parts["tempo"] = max(0.0, 1.0 - abs(f["bpm"] / max(fp["bpm"], 1) - 1.0) / 0.25)
    # chord mix: 1 - L1 distance / 2
    cd = sum(abs(f["chord_mix"][k] - fp["chord_mix"][k]) for k in ("maj", "min", "dom7")) / 2.0
    parts["harmony"] = max(0.0, 1.0 - cd)
    # groove + expr
    parts["groove"] = max(0.0, 1.0 - abs(f["groove_nomml"] - fp["groove_nomml"]) / 4.0)
    parts["dynamics"] = max(0.0, 1.0 - abs(f["expr"] - fp["expr"]) / 40.0)
    # role density/register overlap
    role_scores = []
    for r, ref in fp["roles"].items():
        if r in f["roles"]:
            cur = f["roles"][r]
            dd = max(0.0, 1.0 - abs(cur["density"] - ref["density"]) / max(ref["density"], 1.0))
            rr = max(0.0, 1.0 - abs(cur["register"] - ref["register"]) / 24.0)
            role_scores.append((dd + rr) / 2.0)
    parts["arrangement"] = sum(role_scores) / len(role_scores) if role_scores else 0.5
    W = {"tempo": 0.2, "harmony": 0.25, "groove": 0.15, "dynamics": 0.15, "arrangement": 0.25}
    total = sum(parts[k] * W[k] for k in W)
    return round(100 * total, 1), {k: round(100 * v, 1) for k, v in parts.items()}


def _load(name):
    n = songname.resolve(name)
    return json.load(open(os.path.join(ROOT, "songs", f"{n}.json")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["extract", "score"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--out", default="my_style")
    a = ap.parse_args()
    if a.cmd == "extract":
        fp = extract([_load(x) for x in a.args])
        out = os.path.join(ROOT, "songs", f"_style_{re.sub(r'[^a-z0-9_]','',a.out.lower())}.json")
        json.dump(fp, open(out, "w"), indent=1)
        print(f"[style] fingerprint from {fp['n_songs']} songs -> {out}")
        print(f"  {fp['bpm']:.0f}bpm, chords {fp['chord_mix']}, {fp['sections']} sections, "
              f"groove {fp['groove_nomml']}, roles {list(fp['roles'])}")
        print("STYLE_JSON " + json.dumps(fp))
    else:
        song = _load(a.args[0])
        fp = json.load(open(a.args[1] if a.args[1].endswith(".json") else os.path.join(ROOT, "songs", f"_style_{a.args[1]}.json")))
        s, breakdown = score(song, fp)
        print(f"[style] {a.args[0]} matches this style: {s}/100")
        for k, v in breakdown.items():
            print(f"    {k:12} {v}")
        print("STYLE_SCORE " + json.dumps({"score": s, "breakdown": breakdown}))


if __name__ == "__main__":
    main()
