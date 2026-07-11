#!/usr/bin/env python3
"""VARIATIONS — N DISTINCT options for a region, for the producer to pick.

  variations.py <song> <track> <from_bar> <to_bar> [--n 3] [--write]

The propose-and-pick verb (2026's AI-tool UX: propose options, human decides).
infill regenerates ONCE; variations generates N candidates with a DIVERSITY
guarantee — each pairwise-distinct (rejects near-duplicate seeds), all playing the
window's chords, all valid. --write emits _<song>_var1.. proposal copies the app
can audition/Accept. Composes infill; nothing outside the window ever changes.
"""
import argparse, copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import infill_region as IR
import songname


def _region_key(notes, a, b):
    """the set that identifies a region's content (pitch + quantized start)."""
    return frozenset((n["pitch"], round(n["start"] * 4)) for n in notes if a <= n["start"] < b)


def _distinct(ka, kb, thresh=0.6):
    """Jaccard similarity < thresh => distinct enough."""
    if not ka and not kb:
        return False
    inter = len(ka & kb); union = len(ka | kb) or 1
    return (inter / union) < thresh


def variations(song, track_name, from_bar, to_bar, n=3, max_tries=40, **infill_kw):
    a, b = float(from_bar - 1) * 4.0, float(to_bar) * 4.0
    tr0 = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr0 is None:
        raise SystemExit(f"no track '{track_name}'")
    kept = []                                    # [(seed, region_key, song_copy)]
    seed = 0
    while len(kept) < n and seed < max_tries:
        cand = copy.deepcopy(song)
        try:
            # vary density across candidates too, so options differ in FEEL not just seed
            kw = dict(infill_kw)
            if "density" not in kw or kw["density"] is None:
                kw = {**infill_kw, "density": [None, 3.0, 8.0, 1.5, 6.0][len(kept) % 5]}
            IR.infill(cand, track_name, from_bar, to_bar, seed=seed, **kw)
        except SystemExit:
            seed += 1
            continue
        tr = next(t for t in cand["tracks"] if t["name"] == track_name)
        key = _region_key(tr["notes"], a, b)
        if all(_distinct(key, k) for _, k, _ in kept) and key:
            kept.append((seed, key, cand))
        seed += 1
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("track")
    ap.add_argument("from_bar", type=int); ap.add_argument("to_bar", type=int)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--style", default=None)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    style_fp = None
    if a.style:
        sp = os.path.join(ROOT, "songs", f"_style_{re.sub(r'[^a-z0-9_]','',a.style.lower())}.json")
        if os.path.exists(sp):
            style_fp = json.load(open(sp))
    kept = variations(song, a.track, a.from_bar, a.to_bar, a.n, style=style_fp)
    a0, b0 = (a.from_bar - 1) * 4.0, a.to_bar * 4.0
    print(f"[variations] {len(kept)} distinct option(s) for '{a.track}' bars {a.from_bar}..{a.to_bar}:")
    written = []
    for i, (seed, key, cand) in enumerate(kept, 1):
        cnt = len(key)
        if a.write:
            out = f"_{name}_var{i}"
            json.dump(cand, open(os.path.join(ROOT, "songs", f"{out}.json"), "w"), indent=1)
            written.append(out)
        print(f"  option {i}: {cnt} notes in the window (seed {seed})" +
              (f" -> songs/_{name}_var{i}.json" if a.write else ""))
    print("VARIATIONS_JSON " + json.dumps({"count": len(kept), "written": written}))


if __name__ == "__main__":
    main()
