#!/usr/bin/env python3
"""THE PHASE INTERLOCK — kick and 808 must ADD, never cancel (wave 36;
R-5 item 254).

The r-5 kernel, verbatim law: cross-correlate kick and 808 in the sub
band; find the sub-ms offset (0.1-1ms grid) and polarity maximizing the
summed low-end; COURT-FAIL when the SUM loses sub versus the louder
stem alone (destructive phase — the kick vanishes on mono fold-down);
HEAL symbolically: flip polarity (fx_polarity, minted this wave) and/or
nudge the 808 lane by the winning sub-ms offset. ON-DEMAND stems lane
(render-stems cost — never per-proposal), one ruler with lowend_ears'
sub filter.

  interlock(kick, e808, sr)      -> {loss_db, best: {offset_ms,
                                     polarity, gain_db}, overlap_frames}
  court_phase(stems_dir, song)   -> conviction on destructive summing
  heal_phase(song, verdict)      -> fx_polarity flip and/or note nudge
                                     (<=1ms, once per lane)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOSS_DB_FAIL = -1.0        # the sum must never LOSE vs the louder alone
OFFSET_GRID_MS = [round(x * 0.1, 1) for x in range(-10, 11)]  # ±1ms, 0.1


def _sub(x, sr):
    import lowend_ears as LE
    return LE._butter_lp(x.reshape(-1, 1), sr, LE.SUB_HZ)[:, 0]


def _overlap_mask(a, b, sr, frame=2048):
    """Frames where BOTH stems carry sub energy."""
    n = min(len(a), len(b))
    ga = np.sqrt(np.convolve(a[:n] ** 2, np.ones(frame) / frame, "same"))
    gb = np.sqrt(np.convolve(b[:n] ** 2, np.ones(frame) / frame, "same"))
    return (ga > ga.max() * 0.15) & (gb > gb.max() * 0.15)


def interlock(kick, e808, sr):
    """The kernel: loss now + the best (offset, polarity) recovery."""
    ks, bs = _sub(kick, sr), _sub(e808, sr)
    n = min(len(ks), len(bs))
    ks, bs = ks[:n], bs[:n]
    m = _overlap_mask(ks, bs, sr)
    if m.sum() < sr // 10:
        return {"overlap_frames": int(m.sum()), "skipped": "no overlap"}

    def rms(x):
        return float(np.sqrt(np.mean(x[m] ** 2)) + 1e-12)
    alone = max(rms(ks), rms(bs))
    now = rms(ks + bs)
    loss_db = 20.0 * np.log10(now / alone)
    best = {"offset_ms": 0.0, "polarity": 1, "rms": now}
    for pol in (1, -1):
        for off_ms in OFFSET_GRID_MS:
            k = int(round(off_ms * sr / 1000.0))
            if k >= 0:
                sh = np.concatenate([np.zeros(k), bs[:n - k]])
            else:
                sh = np.concatenate([bs[-k:], np.zeros(-k)])
            r = rms(ks + pol * sh)
            if r > best["rms"]:
                best = {"offset_ms": off_ms, "polarity": pol, "rms": r}
    return {"loss_db": round(float(loss_db), 2),
            "overlap_frames": int(m.sum()),
            "best": {"offset_ms": best["offset_ms"],
                     "polarity": best["polarity"],
                     "gain_db": round(20.0 * np.log10(
                         best["rms"] / now), 2)}}


def _find_stem(stems_dir, words):
    for f in sorted(os.listdir(stems_dir)):
        if f.endswith(".wav") and any(w in f.lower() for w in words):
            return os.path.join(stems_dir, f)
    return None


def court_phase(stems_dir, song=None):
    """Destructive kick+808 summing convicts; the verdict carries the
    measured recovery recipe. ON-DEMAND (stems renders are expensive —
    never per-proposal)."""
    kp = _find_stem(stems_dir, ("kick",))
    bp = _find_stem(stems_dir, ("808", "sub", "bass"))
    if not kp or not bp:
        return {"court": "phase", "ok": True,
                "skipped": "needs kick + 808/bass stems"}
    import soundfile as sf
    k, sr = sf.read(kp, always_2d=True, dtype="float64")
    b, _ = sf.read(bp, always_2d=True, dtype="float64")
    r = interlock(k.mean(axis=1), b.mean(axis=1), sr)
    if r.get("skipped"):
        return {"court": "phase", "ok": True, "skipped": r["skipped"]}
    flags = []
    if r["loss_db"] < LOSS_DB_FAIL:
        flags.append({
            "kind": "destructive_sum", "loss_db": r["loss_db"],
            "best": r["best"],
            "why": f"kick+808 SUM sits {r['loss_db']:+.1f}dB vs the louder "
                   "stem alone — destructive phase (the kick vanishes on "
                   f"mono fold-down); recovery measured: polarity "
                   f"{'FLIP' if r['best']['polarity'] < 0 else 'keep'}"
                   f" + {r['best']['offset_ms']:+.1f}ms nudge = "
                   f"{r['best']['gain_db']:+.1f}dB back"})
    return {"court": "phase", "ok": not flags, "flags": flags,
            "loss_db": r["loss_db"], "best": r["best"]}


def heal_phase(song, verdict):
    """Apply the MEASURED winning move to the 808/sub lane: fx_polarity
    when the recovery wants the flip; a <=1ms note nudge when it wants
    the offset. Once per lane (phase_healed marker). Mutates."""
    if verdict.get("ok", True) or not verdict.get("flags"):
        return []
    best = (verdict.get("best") or
            verdict["flags"][0].get("best") or {})
    edits = []
    bpm = float((song or {}).get("bpm", 120) or 120)
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if not any(w in nm for w in ("808", "sub", "bass")) or \
                nm.endswith(("_sketch", "_identity")):
            continue
        if t.get("phase_healed"):
            continue
        if int(best.get("polarity", 1)) < 0:
            fx = t.setdefault("fx", [])
            if not any(str(f.get("id")) == "fx_polarity" for f in fx):
                fx.insert(0, {"id": "fx_polarity",
                              "params": {"flip": 1}})
                edits.append({"track": t.get("name"),
                              "kind": "polarity_flip"})
        off_ms = float(best.get("offset_ms", 0.0))
        if abs(off_ms) >= 0.1:
            d_beats = round(off_ms * bpm / 60000.0, 6)
            for n in t.get("notes") or []:
                n["start"] = round(float(n.get("start", 0)) + d_beats, 6)
            edits.append({"track": t.get("name"), "kind": "nudge",
                          "ms": off_ms, "beats": d_beats})
        if edits:
            t["phase_healed"] = True
            break                      # one 808 lane owns the interlock
    return edits


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE PHASE INTERLOCK "
                                             "(wave 36)")
    ap.add_argument("stems_dir")
    ap.add_argument("--song", default=None)
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song)) if args.song else None
    v = court_phase(args.stems_dir, song)
    if args.heal and song is not None and not v.get("ok", True):
        v["heals"] = heal_phase(song, v)
        if v["heals"]:
            json.dump(song, open(args.song, "w"), indent=1)
            v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v.get("ok") or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
