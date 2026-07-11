#!/usr/bin/env python3
"""ARC QUALITY SWEEP — does the arc make release-shaped music ACROSS GENRES?

Firing 80 proved it on one house loop. This sweeps diverse genres (real loop_gen
DNA per style) through finish+prescribe+render and asserts the UNIVERSAL release
invariants hold for each: 0 clipped, headroom, mono-safe, no dominant band. LUFS
is reported per-genre (genre taste, not a fixed target). Exit 1 if any genre's
output isn't release-shaped."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv/bin/python")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import finish as F
import prescribe as P
from chordvote import chord_map

GENRES = [g for g in sys.argv[1:] if not g.startswith("-")] or ["house", "ambient", "trap", "funk", "dnb"]
FAIL, ROWS = [], []


def analyze(wav):
    r = subprocess.run([PY, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)


def one(genre):
    name = f"_arcsweep_{genre}"
    # real genre DNA as the rough input
    r = subprocess.run([PY, os.path.join(ROOT, "tools", "loop_gen.py"), genre, name, "--bars", "8", "--seed", "3"],
                       capture_output=True, text=True, timeout=120)
    p = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(p):
        return {"genre": genre, "error": "loop_gen failed: " + (r.stdout + r.stderr)[-120:]}
    song = json.load(open(p))
    song.setdefault("chords", chord_map(song))
    try:
        F.finish(song)
        P.prescribe(song)
    except Exception as e:
        return {"genre": genre, "error": f"arc failed: {e}"}
    json.dump(song, open(p, "w"), indent=1)
    wav = os.path.join(SONGS, f"{name}.wav")
    rr = subprocess.run([M1, "render", p, wav], capture_output=True, text=True, timeout=600)
    if "ok=1" not in (rr.stdout + rr.stderr):
        return {"genre": genre, "error": "render failed"}
    m = analyze(wav)
    bands = m.get("band_energy_pct", {})
    row = {"genre": genre, "bars": song["lengthBars"], "lufs": m["lufs_integrated"],
           "dbtp": m["true_peak_dbtp"], "clipped": m["clipped_samples"],
           "corr": m["lr_correlation"], "max_band": round(max(bands.values()), 1) if bands else None}
    for f in (p, wav):
        os.path.exists(f) and os.remove(f)
    return row


def main():
    print(f"== sweeping {len(GENRES)} genres through the full arc ==")
    for g in GENRES:
        row = one(g)
        ROWS.append(row)
        if "error" in row:
            print(f"  {g:8} ERROR: {row['error']}")
            FAIL.append(f"{g}:error")
            continue
        # universal release invariants (per genre)
        inv = []
        if row["clipped"] != 0: inv.append("clipped")
        if row["dbtp"] > -1.0: inv.append(f"dbtp {row['dbtp']}")
        if row["corr"] < 0.3: inv.append(f"corr {row['corr']}")
        if row["max_band"] is not None and row["max_band"] >= 80: inv.append(f"band {row['max_band']}%")
        if not (-30 <= row["lufs"] <= -5): inv.append(f"lufs {row['lufs']}")
        status = "OK" if not inv else "FAIL(" + ",".join(inv) + ")"
        if inv: FAIL.append(f"{g}:" + ",".join(inv))
        print(f"  {g:8} {row['bars']}bars  LUFS {row['lufs']:>7}  dBTP {row['dbtp']:>6}  "
              f"clip {row['clipped']}  corr {row['corr']:>5}  maxband {row['max_band']}%  -> {status}")
    print(f"\n== SWEEP: {len(GENRES) - len([f for f in FAIL])} / {len(GENRES)} genres release-shaped ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL)); sys.exit(1)
    print("THE ARC MAKES RELEASE-SHAPED MUSIC ACROSS THE GENRE SPACE")


if __name__ == "__main__":
    main()
