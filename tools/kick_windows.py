#!/usr/bin/env python3
"""THE BRAIN BR-C wave 2 — GENRE KICK WINDOWS (measured, never guessed).

The oracle's generic kick window convicted kick_psy for being bright — but a
psy kick is bright BY DESIGN; the refusal named this rung. Windows must come
from MEASURED references, and the corpus has them: every library/gold
exemplar points at its EARS-PASSED source song (accept:/eval:/crate:), whose
kick lane still carries the accepted take's voice + params + fx chain. This
tool renders each gold genre's kick lane SOLO (2 bars from the gold window,
densest-span fallback), measures it with the house ears (analyze2), and
banks per-genre (centroid, crest) windows to telemetry/kick_windows.json —
personal, never ships (PRIVACY LAW).

Gold genres without a kick lane (blues, gospel, swing, vaporwave, ambient)
bank NOTHING — an unmeasured genre gets the generic window plus an honest
line, never an invented number.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")
BANK_NAME = "kick_windows.json"
PROBE_BEATS = 8.0            # 2 bars
CENT_PAD = (0.70, 1.45)      # window = measured envelope padded
CREST_PAD = (4.0, 6.0)
CENT_FLOOR = 120.0

# family aliases: an unmeasured genre may ride a MEASURED family member; an
# alias to the wrong family is worse than the generic window — keep it tight
ALIAS = {
    "psytrance": "goa", "psy": "goa", "fullon": "goa", "full_on": "goa",
    "psybient": "goa", "goa_trance": "goa",
    "uk_garage": "ukgarage", "garage": "ukgarage", "2step": "ukgarage",
    "speed_garage": "ukgarage",
    "hiphop": "boombap", "hip_hop": "boombap", "memphis": "memphis_rap",
    "dubtechno": "dub_techno", "bigband": "swing_bigband",
    "big_band": "swing_bigband", "deep_house": "house", "tech_house": "house",
}


def norm_genre(g):
    return str(g or "").strip().lower().replace(" ", "_").replace("-", "_")


def window_for(genre, bank):
    """Measured window for a genre (exact, then family alias) or None."""
    if not bank:
        return None
    genres = bank.get("genres") or {}
    n = norm_genre(genre)
    hit = genres.get(n)
    if hit is None and n in ALIAS:
        hit = genres.get(ALIAS[n])
        if hit is not None:
            hit = dict(hit, via=ALIAS[n])
    return hit


def rows_to_window(rows):
    """Measured rows (one per reference) -> a padded envelope window."""
    cents = [r["spectral_centroid_hz"] for r in rows
             if isinstance(r.get("spectral_centroid_hz"), (int, float))]
    crests = [r["crest_factor_db"] for r in rows
              if isinstance(r.get("crest_factor_db"), (int, float))]
    if not cents or not crests:
        return None
    return {
        "spectral_centroid_hz": [round(max(CENT_FLOOR,
                                           min(cents) * CENT_PAD[0]), 1),
                                 round(max(cents) * CENT_PAD[1], 1)],
        "crest_factor_db": [round(min(crests) - CREST_PAD[0], 1),
                            round(max(crests) + CREST_PAD[1], 1)],
    }


def densest_span(notes, beats=PROBE_BEATS, step=4.0):
    """Start beat of the densest [s, s+beats) span — the gold window can sit
    on a breakdown where the kick rests."""
    if not notes:
        return 0.0
    starts = sorted(float(n.get("start", 0.0)) for n in notes)
    best_s, best_c = 0.0, -1
    s = 0.0
    while s <= starts[-1]:
        c = sum(1 for x in starts if s <= x < s + beats)
        if c > best_c:
            best_s, best_c = s, c
        s += step
    return best_s


def slice_shift(notes, b0, beats=PROBE_BEATS):
    out = []
    for n in notes:
        st = float(n.get("start", 0.0))
        if b0 <= st < b0 + beats:
            m = dict(n)
            m["start"] = round(st - b0, 4)
            m["len"] = round(min(float(n.get("len", 0.5)),
                                 b0 + beats - st), 4)
            out.append(m)
    return out


def bank_path(root=None):
    return os.path.join(root or ROOT, "telemetry", BANK_NAME)


def load_bank(root=None):
    try:
        return json.load(open(bank_path(root)))
    except Exception:
        return None


def _kick_track(song, gold_kick_name):
    tracks = song.get("tracks") or []
    for t in tracks:
        if str(t.get("name")) == gold_kick_name:
            return t
    for t in tracks:
        if "kick" in str(t.get("name", "")).lower():
            return t
    for t in tracks:
        src = t.get("source") or {}
        if "kick" in str(src.get("id", "")).lower():
            return t
    return None


def _resolve_song(source):
    name = source.split(":", 1)[-1] if ":" in source else source
    for p in (os.path.join(ROOT, "songs", f"{name}.json"),
              os.path.join(ROOT, "songs", "crate", f"{name}.json")):
        if os.path.exists(p):
            return p
    return None


def _probe_doc(song, track, start_beat):
    tr = {k: v for k, v in track.items() if k not in ("sends", "muted")}
    tr["notes"] = slice_shift(track.get("notes") or [], start_beat)
    tr["gainDb"] = float(track.get("gainDb", 0.0))
    return {"version": 2, "bpm": float(song.get("bpm", 120.0)),
            "key": song.get("key") or "C minor", "lengthBars": 2,
            "masterGainDb": 0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [tr]}


def _measure(doc, workdir):
    sj = os.path.join(workdir, "kickref.json")
    wav = os.path.join(workdir, "kickref.wav")
    with open(sj, "w") as f:
        json.dump(doc, f)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True,
                       text=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(wav):
        return None
    a = subprocess.run([PY, os.path.join(HERE, "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=120)
    if a.returncode != 0:
        return None
    try:
        d = json.loads(a.stdout)
    except json.JSONDecodeError:
        return None
    return {k: d.get(k) for k in ("spectral_centroid_hz", "crest_factor_db",
                                  "rms_db", "peak_dbfs")}


def bank_references(root=None, verbose=True):
    import glob
    import tempfile
    root = root or ROOT
    rows, skipped = [], []
    for f in sorted(glob.glob(os.path.join(root, "library", "gold", "*.json"))):
        if f.endswith("_index.json"):
            continue
        try:
            gold = json.load(open(f))
        except Exception:
            continue
        genre = norm_genre(gold.get("genre") or
                           os.path.basename(f)[:-5])
        gk = next((t for t in gold.get("tracks") or []
                   if "kick" in str(t.get("name", "")).lower()
                   or "kick" in str(t.get("voice", "")).lower()), None)
        if gk is None:
            skipped.append((genre, "no kick lane in the exemplar"))
            continue
        sp = _resolve_song(str(gold.get("source", "")))
        if sp is None:
            skipped.append((genre, f"source {gold.get('source')} unresolvable"))
            continue
        try:
            song = json.load(open(sp))
        except Exception:
            skipped.append((genre, f"{sp} unparseable"))
            continue
        track = _kick_track(song, str(gk.get("name")))
        if track is None or not track.get("notes"):
            skipped.append((genre, "kick lane missing/empty in source song"))
            continue
        w = gold.get("window") or {}
        b0 = float(w.get("startBar", 0)) * 4.0
        notes = slice_shift(track["notes"], b0)
        if len(notes) < 4:
            b0 = densest_span(track["notes"])
        with tempfile.TemporaryDirectory(prefix="kickwin_") as wd:
            feats = _measure(_probe_doc(song, track, b0), wd)
        if not feats or feats.get("spectral_centroid_hz") is None:
            skipped.append((genre, "render/measure failed"))
            continue
        row = {"genre": genre, "song": os.path.basename(sp),
               "voice": str((track.get("source") or {}).get("id")
                            or gk.get("voice")), "start_beat": b0}
        row.update(feats)
        rows.append(row)
        if verbose:
            print(f"  {genre:14s} {row['voice']:18s} "
                  f"centroid={feats['spectral_centroid_hz']} "
                  f"crest={feats['crest_factor_db']}")
    genres = {}
    for r in rows:
        genres.setdefault(r["genre"], []).append(r)
    bank = {"version": 1,
            "rows": rows,
            "skipped": [{"genre": g, "why": w} for g, w in skipped],
            "genres": {g: rows_to_window(rs) for g, rs in genres.items()}}
    bank["genres"] = {g: w for g, w in bank["genres"].items() if w}
    p = bank_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(bank, f, indent=1)
    os.replace(tmp, p)
    return bank


def main():
    ap = argparse.ArgumentParser(description="GENRE KICK WINDOWS (BR-C wave 2)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("bank", help="render + measure every gold kick reference")
    wi = sub.add_parser("window")
    wi.add_argument("genre")
    a = ap.parse_args()
    if a.cmd == "bank":
        if not os.path.exists(M1):
            print("m1 binary missing — build first")
            return 2
        bank = bank_references()
        print(json.dumps({"measured": len(bank["rows"]),
                          "genres": sorted(bank["genres"]),
                          "skipped": bank["skipped"]}, indent=1))
        return 0 if bank["rows"] else 1
    if a.cmd == "window":
        w = window_for(a.genre, load_bank())
        print(json.dumps(w, indent=1) if w
              else f"no measured window for {a.genre!r} — generic stands")
        return 0 if w else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
