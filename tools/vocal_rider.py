#!/usr/bin/env python3
"""VOCAL RIDER — the level fight gets a FIX, not just a callout (gain-ride AI).

  vocal_rider.py <song> [--track name] [--stems dir] [--target 0] [--range 4] [--write]

stem_callouts DETECTS "vocal buried in the chorus"; this GENERATES the ride:
per-half-beat vocal-vs-backing margin from the song's own stems (m1 render-stems,
or --stems for already-split imports), a slew-limited bounded gain curve toward
--target dB of margin, thinned to real automation points on the vocal track's
gainDb — the classic studio rider (VocalRider/Nectar class), landed as
inspectable song.json automation the engine already plays. Fader riding, not
compression: the waveform is untouched, the move is visible on the lane, and
one undo removes it.

Read-only by default (prints RIDE_JSON; the MCP mount stays read-only — the
agent applies via `automate`, which files receipts). --write lands the curve
directly (CLI precedent: chordvote --write).
"""
import argparse, glob, json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
VOCAL_WORDS = ("vocal", "vox", "voice", "choir", "topline", "lead_voc", "rap", "sing", "acapella")


# ------------------------------------------------------------------ pure kernel
def ride(v_db, b_db, target=0.0, rng=4.0, slew=1.5, gate_db=45.0):
    """per-window vocal/backing dB -> slew-limited, bounded gain deltas (dB).

    Active windows (vocal within gate_db of its own peak) pull toward
    `target` margin over the backing, clamped to ±rng; inactive windows decay
    to 0 (the fader comes home — silence is never boosted). Median-3 smoothing
    kills single-window spikes before the slew."""
    v = np.asarray(v_db, dtype=float)
    b = np.asarray(b_db, dtype=float)
    peak = float(v.max()) if len(v) else -120.0
    active = v > (peak - gate_db)
    want = np.clip(target - (v - b), -rng, rng)
    want[~active] = 0.0
    if len(want) >= 3:                      # median-3
        w = want.copy()
        w[1:-1] = np.median(np.stack([want[:-2], want[1:-1], want[2:]]), axis=0)
        want = w
    out = np.zeros_like(want)
    cur = 0.0
    for i, w in enumerate(want):
        cur += float(np.clip(w - cur, -slew, slew))
        out[i] = cur
    return out, active


def thin(beats, values, eps=0.25, hard_cap=400):
    """keep first/last + points that a straight line misses by > eps dB."""
    n = len(values)
    if n <= 2:
        return list(range(n))
    keep = [0]
    i = 0
    while i < n - 1:
        j = i + 1
        while j < n - 1:
            # can we skip straight from i to j+1?
            span = slice(i, j + 2)
            xs = np.asarray(beats[span]) - beats[i]
            seg = values[i] + (values[j + 1] - values[i]) * (
                xs / max(xs[-1], 1e-9))
            if np.abs(seg - np.asarray(values[span])).max() > eps:
                break
            j += 1
        keep.append(j)
        i = j
    if keep[-1] != n - 1:
        keep.append(n - 1)
    if len(keep) > hard_cap:
        keep = keep[:: max(1, len(keep) // hard_cap)] + [n - 1]
    return sorted(set(keep))


# ------------------------------------------------------------------ stems + song
def _load_wav(path):
    from scipy.io import wavfile
    sr, x = wavfile.read(path)
    if x.dtype == np.int16:
        x = x.astype(np.float64) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float64) / 2147483648.0
    else:
        x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return sr, x


def _stem_map(d):
    """dir -> {trackname: path}; accepts NN_name.wav (render-stems) and name.wav."""
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.wav"))):
        base = os.path.basename(f)[:-4]
        name = base.split("_", 1)[1] if base[:2].isdigit() and "_" in base else base
        out[name] = f
    return out


def _win_db(x, sr, hop_s, n_win):
    """windowed RMS dB, exactly n_win windows (zero-pad the tail)."""
    hop = max(1, int(hop_s * sr))
    out = np.full(n_win, -120.0)
    for i in range(n_win):
        seg = x[i * hop:(i + 1) * hop]
        if len(seg) == 0:
            break
        r = float(np.sqrt(np.mean(seg ** 2)))
        out[i] = 20 * np.log10(r) if r > 1e-9 else -120.0
    return out


def plan(song, stems_dir, track=None, target=0.0, rng=4.0, slew=1.5):
    names = [t.get("name", "") for t in song.get("tracks", [])]
    if track is None:
        track = next((n for n in names
                      if any(w in n.lower() for w in VOCAL_WORDS)), None)
    if track is None or track not in names:
        return {"available": False,
                "reason": f"no vocal-ish track (have: {', '.join(names) or 'none'}) — pass --track"}
    stems = _stem_map(stems_dir)
    if track not in stems:
        return {"available": False, "reason": f"no stem for '{track}' in {stems_dir} "
                f"(have: {', '.join(sorted(stems)) or 'none'})"}
    sr, v = _load_wav(stems[track])
    backing = None
    for n, f in stems.items():
        if n == track:
            continue
        s2, x = _load_wav(f)
        if s2 != sr:
            continue
        if backing is None:
            backing = np.zeros(max(len(v), len(x)))
        if len(x) > len(backing):
            backing = np.pad(backing, (0, len(x) - len(backing)))
        backing[:len(x)] += x
    if backing is None:
        return {"available": False, "reason": "no backing stems to ride against"}

    bpm = float(song.get("bpm", 120.0))
    hop_s = (60.0 / bpm) / 2.0                       # half a beat
    n_win = int(np.ceil(max(len(v), len(backing)) / (hop_s * sr)))
    v_db = _win_db(v, sr, hop_s, n_win)
    b_db = _win_db(backing, sr, hop_s, n_win)
    deltas, active = ride(v_db, b_db, target=target, rng=rng, slew=slew)

    tr = next(t for t in song["tracks"] if t.get("name") == track)
    base = float(tr.get("gainDb", 0.0))
    beats = np.arange(n_win) * 0.5
    keep = thin(beats, deltas + base)
    points = [{"beat": round(float(beats[i]), 2), "v": round(float(base + deltas[i]), 2)}
              for i in keep]
    boosts = deltas[active & (deltas > 0.1)]
    cuts = deltas[active & (deltas < -0.1)]
    return {"available": True, "track": track, "baseGainDb": base, "target": target,
            "range": rng, "windows": n_win, "active_pct": round(100.0 * active.mean(), 1),
            "mean_boost": round(float(boosts.mean()), 2) if len(boosts) else 0.0,
            "mean_cut": round(float(cuts.mean()), 2) if len(cuts) else 0.0,
            "n_points": len(points),
            "automation": {"target": "gainDb", "points": points}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--track", default=None)
    ap.add_argument("--stems", default=None, help="existing stems dir (else m1 render-stems)")
    ap.add_argument("--target", type=float, default=0.0, help="vocal-over-backing margin dB")
    ap.add_argument("--range", dest="rng", type=float, default=4.0)
    ap.add_argument("--slew", type=float, default=1.5, help="max dB change per half-beat")
    ap.add_argument("--write", action="store_true", help="land the ride on the track's automation")
    a = ap.parse_args()

    import songname
    name = songname.resolve(a.song)
    sp = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(sp))

    tmp = None
    stems_dir = a.stems
    if stems_dir is None:
        if not os.path.exists(M1):
            print("RIDE_JSON " + json.dumps({"available": False, "reason": "m1 not built and no --stems"}))
            sys.exit(3)
        tmp = tempfile.mkdtemp(prefix="rider_")
        r = subprocess.run([M1, "render-stems", sp, tmp], capture_output=True, text=True)
        if r.returncode != 0 or not glob.glob(os.path.join(tmp, "*.wav")):
            shutil.rmtree(tmp, ignore_errors=True)
            print("RIDE_JSON " + json.dumps({"available": False,
                  "reason": f"render-stems failed: {(r.stdout + r.stderr)[-200:]}"}))
            sys.exit(3)
        stems_dir = tmp

    try:
        out = plan(song, stems_dir, track=a.track, target=a.target, rng=a.rng, slew=a.slew)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

    if out.get("available"):
        print(f"[rider] {name}/{out['track']}: {out['windows']} half-beat windows, "
              f"{out['active_pct']}% active, boost ~{out['mean_boost']} / cut ~{out['mean_cut']} dB "
              f"-> {out['n_points']} points around base {out['baseGainDb']} dB")
        if a.write:
            tr = next(t for t in song["tracks"] if t.get("name") == out["track"])
            autos = [x for x in tr.get("automation", []) if x.get("target") != "gainDb"]
            autos.append(out["automation"])
            tr["automation"] = autos
            json.dump(song, open(sp, "w"), indent=1)
            print(f"  WROTE gainDb ride ({out['n_points']} points) -> songs/{name}.json")
    else:
        print(f"[rider] unavailable: {out.get('reason')}")
    print("RIDE_JSON " + json.dumps(out))
    if not out.get("available"):
        sys.exit(3)


if __name__ == "__main__":
    main()
