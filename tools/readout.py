#!/usr/bin/env python3
"""AMAZING PART V — THE READOUT (the model's eyes, one stable page).

The canonical, STABLE-FIELD, <=2K-char numeric snapshot of any take —
composition becomes a closed conversation in NUMBERS a tiny model can
follow. Field order never changes; deviations lead their lines; every
unknown says so instead of vanishing.

  TAKE    order echo (bpm/key/bars/tracks/notes)
  EARS    the render's numbers (or 'unrendered — render_song first')
  GATE    the five-gate states, hard reasons first (release_gate parts,
          render-free: judges the wav it is GIVEN, never renders)
  COURTS  every court verdict: bad first, then flagged, then ok
  DIFF    vs the PREVIOUS readout of the same song (stamped under
          songs/.readout/): note deltas per lane, LUFS drift, courts that
          flipped, gate flips — the conductor's "what changed since I
          last looked"

Every call stamps the current snapshot for the next diff. Pure read —
the song is never touched."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MAX_CHARS = 2000


def _ears(analysis):
    a = analysis or {}
    if not a:
        return "unrendered — render_song first, then re-read", {}
    keys = (("lufs", "lufs_integrated", 1), ("dbtp", "true_peak_dbtp", 2),
            ("psr", "psr", 1), ("lra", "lra", 1),
            ("crest", "crest_factor_db", 1), ("width", "stereo_width_db", 1),
            ("centroid", "spectral_centroid_hz", 0),
            ("clipped", "clipped_samples", 0))
    vals = {}
    parts = []
    for label, k, nd in keys:
        v = a.get(k)
        if isinstance(v, (int, float)):
            vals[label] = round(v, nd)
            parts.append(f"{label} {vals[label]}")
    return " | ".join(parts) or "no metrics", vals


def _gate_line(gates):
    order = ("census", "reference", "taste", "novelty", "blind")
    short = {"census": "G1", "reference": "G2", "taste": "G3",
             "novelty": "G4", "blind": "G5"}
    parts, states = [], {}
    for k in order:
        g = gates.get(k) or {}
        if k in ("census", "reference"):
            ok = bool(g.get("pass"))
            why = (g.get("hard") or [""])[0]
            states[k] = "ok" if ok else "FAIL"
            parts.append(f"{short[k]} {'ok' if ok else 'FAIL(' + why[:40] + ')'}")
        else:
            st = g.get("state", "not-run")
            states[k] = st
            why = g.get("why", "")
            parts.append(f"{short[k]} {st}"
                         + (f"({why[:30]})" if st in ("fail", "skip") and why
                            else ""))
    return " | ".join(parts), states


def _court_lines(courts):
    bad, flagged, ok = [], [], []
    for name in sorted(courts or {}):
        v = courts[name]
        if not isinstance(v, dict):
            continue
        nf = len(v.get("flags") or v.get("advisories") or [])
        if v.get("ok") is False:
            bad.append(name)
        elif nf:
            flagged.append(f"{name} {nf}")
        else:
            ok.append(name)
    parts = []
    if bad:
        parts.append("bad: " + " ".join(bad))
    if flagged:
        parts.append("flags: " + ", ".join(flagged))
    parts.append("ok: " + (" ".join(ok) or "none"))
    return " | ".join(parts), {"bad": bad, "flagged": flagged, "ok": ok}


def _lane_counts(song):
    return {str(t.get("name")): len(t.get("notes") or [])
            for t in song.get("tracks") or []}


def _diff(prev, cur):
    if not prev:
        return "first readout of this take (no previous stamp)"
    parts = []
    pl, cl = prev.get("lanes") or {}, cur.get("lanes") or {}
    deltas = []
    for lane in sorted(set(pl) | set(cl)):
        d = cl.get(lane, 0) - pl.get(lane, 0)
        if d:
            deltas.append(f"{lane} {d:+d}")
    total = sum(cl.values()) - sum(pl.values())
    if deltas:
        parts.append(f"notes {total:+d} ({', '.join(deltas[:5])})")
    pe, ce = prev.get("ears") or {}, cur.get("ears") or {}
    if "lufs" in pe and "lufs" in ce and abs(ce["lufs"] - pe["lufs"]) >= 0.1:
        parts.append(f"lufs {ce['lufs'] - pe['lufs']:+.1f}")
    pc, cc = prev.get("courts") or {}, cur.get("courts") or {}
    for name in sorted(set(cc.get("bad") or []) - set(pc.get("bad") or [])):
        parts.append(f"{name} court NEW-BAD")
    for name in sorted(set(pc.get("bad") or []) - set(cc.get("bad") or [])):
        parts.append(f"{name} court healed")
    pg, cg = prev.get("gate") or {}, cur.get("gate") or {}
    for k in sorted(set(pg) & set(cg)):
        if pg[k] != cg[k]:
            parts.append(f"{k} {pg[k]}->{cg[k]}")
    return " | ".join(parts) if parts else "no change since the last readout"


def _stamp_path(song_path, name):
    # beside the song, never a fixed dir — bench fixtures in a tmp root
    # must stamp in that root, not in the real songs/
    return os.path.join(os.path.dirname(os.path.abspath(song_path)),
                        ".readout", f"{name}.json")


def readout(song_path, wav=None, genre=None, root=None, stamp=True):
    """(text, data). Render-free: judges the wav it is given (a stale/absent
    wav is SAID, never guessed)."""
    root = root or ROOT
    try:
        song = json.load(open(song_path))
    except Exception as e:
        return f"READOUT unavailable: song unreadable ({e})", {}
    name = os.path.basename(song_path)[:-5] if song_path.endswith(".json") \
        else os.path.basename(song_path)
    g = str(genre or (song.get("_loop") or {}).get("genre")
            or song.get("genre") or "")
    analysis = {}
    if wav and os.path.exists(wav):
        try:
            import analyze2
            analysis = analyze2.analyze(wav)
        except Exception:
            analysis = {}
    try:
        import music_court as mc
        courts = mc.run_courts(song, g, heal=False) or {}
    except Exception:
        courts = {}
    import release_gate as rg
    gold, _gn = rg.gold_for(g, root)
    base = os.path.basename(song_path)
    v = rg.assemble(
        rg.g1_census(song, g, analysis or None),
        rg.g2_reference(analysis, gold, g),
        rg.g3_taste(wav if analysis else None, root=root),
        rg.g4_novelty(song, self_ids={f"songs/{base}", f"songs/crate/{base}"},
                      root=root),
        song_name=base, genre=g)
    lanes = _lane_counts(song)
    ears_txt, ears_vals = _ears(analysis)
    gate_txt, gate_states = _gate_line(v["gates"])
    court_txt, court_data = _court_lines(courts)
    cur = {"t": time.time(), "lanes": lanes, "ears": ears_vals,
           "courts": court_data, "gate": gate_states,
           "pass": bool(v["pass"])}
    sp = _stamp_path(song_path, name)
    prev = None
    try:
        prev = json.load(open(sp))
    except Exception:
        pass
    diff_txt = _diff(prev, cur)
    if stamp:
        try:
            os.makedirs(os.path.dirname(sp), exist_ok=True)
            tmp = sp + ".tmp"
            with open(tmp, "w") as f:
                json.dump(cur, f)
            os.replace(tmp, sp)
        except OSError:
            pass
    total = sum(lanes.values())
    lines = [
        f"TAKE {name} | {song.get('bpm')}bpm {song.get('key') or '?'} | "
        f"{song.get('lengthBars')} bars | {len(lanes)} tracks / {total} notes"
        + (f" | genre {g}" if g else ""),
        f"EARS {ears_txt}",
        f"GATE {gate_txt}" + ("" if v["pass"] else " => NOT RELEASABLE"),
        f"COURTS {court_txt}",
        f"DIFF {diff_txt}",
    ]
    text = "\n".join(lines)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 12] + "\n[truncated]"
    return text, {"snapshot": cur, "gate": v, "text_chars": len(text)}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE READOUT (AMAZING PART V)")
    ap.add_argument("song")
    ap.add_argument("--wav", default=None)
    ap.add_argument("--genre", default=None)
    ap.add_argument("--no-stamp", action="store_true")
    a = ap.parse_args()
    txt, _ = readout(a.song, wav=a.wav, genre=a.genre,
                     stamp=not a.no_stamp)
    print(txt)
