#!/usr/bin/env python3
"""THE GENRE MATCH — the delta-spectrum heal vs the GENRE's own target
(wave 35; R-16 item 134).

master_match.py (the sibling session's import finale, 2026-07-15)
matches a product against a specific RECORD on the 8-band ruler +
fx_match_eq bells. THIS module is the genre-target variant the backlog
asked for: family band-shape targets MEASURED FROM THE CORPUS WINNERS
(self-measure law — never a blog curve), banked deterministically, and
a bounded fx_match_eq heal pulling a take toward its family shape.

ONE RULER: measure/band_profile are IMPORTED from master_match — this
file re-encodes no DSP. ON-DEMAND lane (CLI / explicit asks / the
deck's 'match my genre' path); the per-proposal audio pass gets only an
ADVISORY (family averages are coarse — auto-EQing every master toward
the mean would sand off intent).

  seed_targets()             measure eval winners per translation
                             family -> library/genre_band_targets.json
  target_for(genre)          the banked family shape (8 bands, dB)
  court_genre_shape(wav, genre)   advisory when any band sits >6dB off
  heal_genre_match(song, wav, genre)  bounded fx_match_eq (+-3dB/bell)
                             inserted PRE-WALL; explicit-ask tool
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS_PATH = os.path.join(ROOT, "library", "genre_band_targets.json")

ADVISORY_DB = 6.0
HEAL_MAX_DB = 3.0


def _family(genre):
    import translation_court
    return translation_court.family_for(genre)


def seed_targets(say=print):
    """Bank per-family mean band shapes from the eval winners
    (deterministic: sorted file list, shape-only profiles)."""
    import glob
    import master_match as MM
    hist = {}
    try:
        for line in open(os.path.join(ROOT, "eval", "history.jsonl")):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("song"):
                hist[os.path.basename(str(r["song"]))] = r.get("genre", "")
    except FileNotFoundError:
        pass
    fams = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "songs", "eval_*.wav"))):
        b = os.path.basename(p)
        g = hist.get(b.replace(".wav", ".json"), "") or \
            b[5:].split(".")[0]
        try:
            x, sr = MM._stereo(p)
            m = MM.measure(x, sr)
        except Exception:
            continue
        fams.setdefault(_family(g), []).append(m["bands"])
    out, stds = {}, {}
    for fam, rows in fams.items():
        if len(rows) < 2:
            continue
        arr = np.array(rows)
        out[fam] = [round(float(v), 2) for v in arr.mean(axis=0)]
        stds[fam] = [round(float(v), 2) for v in arr.std(axis=0)]
        say(f"  {fam}: {len(rows)} winners -> {out[fam]} (std {stds[fam]})")
    json.dump({"made_from": "eval winners (self-measure law)",
               "bands": out, "stds": stds},
              open(TARGETS_PATH, "w"), indent=1)
    say(f"banked {len(out)} family targets -> {TARGETS_PATH}")
    return out


def target_for(genre):
    try:
        bank = json.load(open(TARGETS_PATH))
    except Exception:
        return None, None
    fam = _family(genre)
    return bank["bands"].get(fam), (bank.get("stds") or {}).get(fam)


def court_genre_shape(wav, genre=""):
    """ADVISORY-only: family averages are coarse; the recipe rides."""
    tgt, std = target_for(genre)
    if not tgt:
        return {"court": "genre_shape", "ok": True,
                "skipped": "no banked family target"}
    import master_match as MM
    x, sr = MM._stereo(wav)
    m = MM.measure(x, sr)
    delta = [round(t - b, 2) for t, b in zip(tgt, m["bands"])]
    # the advisory edge is the family's OWN spread (2 sigma, floor 6dB):
    # winners sit inside their family by construction — a fixed 6dB
    # advised eval_house against its own family mean (electronic spans
    # house..phonk; band variance is the family's honest width)
    edges = [max(ADVISORY_DB, 2.0 * s) for s in (std or [0] * len(tgt))]
    overs = [abs(d) - e for d, e in zip(delta, edges)]
    worst = max(overs)
    advisories = []
    if worst > 0:
        i = int(np.argmax(overs))
        advisories.append({
            "kind": "off_family_shape", "worst_band": i,
            "delta_db": delta,
            "why": f"band {i + 1}/8 sits {delta[i]:+.1f}dB off the "
                   f"family's measured winner shape (worst of "
                   f"{worst:.1f}dB) — genre_match can pull it in "
                   "(bounded +-3dB) on an explicit ask"})
    return {"court": "genre_shape", "ok": True, "advisories": advisories,
            "delta_db": delta}


def heal_genre_match(song, wav, genre=""):
    """The bounded pull: fx_match_eq bells = clip(delta, +-3dB),
    inserted PRE-WALL. Explicit-ask tool — never per-proposal.
    Mutates; returns ledger."""
    v = court_genre_shape(wav, genre)
    delta = v.get("delta_db")
    if not delta:
        return []
    gains = [round(max(min(d, HEAL_MAX_DB), -HEAL_MAX_DB), 2)
             for d in delta]
    if all(abs(g) < 0.5 for g in gains):
        return []
    master = song.setdefault("master", [])
    idx = len(master)
    for i, f in enumerate(master):
        if str(f.get("id", f.get("type", "")) or "").startswith(
                ("fx_truepeak", "fx_brickwall")):
            idx = i
            break
    zones = ("g85", "g171", "g344", "g691", "g1389", "g2790", "g5609",
             "g11272")               # fx_match_eq's own band-center names
    params = {z: g for z, g in zip(zones, gains)}
    for f in master:
        if str(f.get("id", "")) == "fx_match_eq":
            f.setdefault("params", {}).update(params)
            return [{"kind": "genre_match_update", "gains": gains}]
    master.insert(idx, {"id": "fx_match_eq", "params": params})
    return [{"kind": "genre_match_insert", "gains": gains}]


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE GENRE MATCH (wave 35)")
    ap.add_argument("target", nargs="?",
                    help="song.json to court/heal (omit with --seed)")
    ap.add_argument("--genre", default="")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    if args.seed:
        seed_targets()
        return 0
    song = json.load(open(args.target))
    wav = args.target[:-5] + ".wav"
    if args.heal:
        eds = heal_genre_match(song, wav, args.genre)
        if eds:
            json.dump(song, open(args.target, "w"), indent=1)
        print(json.dumps({"healed": eds}, indent=1))
    else:
        print(json.dumps(court_genre_shape(wav, args.genre), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
