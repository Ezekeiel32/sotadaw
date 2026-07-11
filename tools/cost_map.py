#!/usr/bin/env python3
"""A5 — THE PRICE OF EVERY SOUND (docs/THE_PHYSICS.md §6; gap G5; laws E7/E10).

"Bake frequently-used voices when convenient" was folklore; this prices it.
Per-track solo render walltime -> realtime factor; JIT/AOT census straight from
faust_gen/faust_registry.h vs instruments/*.dsp; usage counted across songs/;
the promotion worklist sorted by (usage x cost) exactly as E7 demands.

usage:
  cost_map.py [--song songs/x.json]      price one song per-track (default: eval_funk)
  cost_map.py --voices [--top N]         price voices standalone (1-note probe each)
  cost_map.py --census                   JIT/AOT census + usage counts only (fast)
Prints COST_JSON <payload>.
"""
import json
import math
import os
import re
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
REGISTRY = os.path.join(ROOT, "app", "faust_gen", "faust_registry.h")


def aot_names():
    if not os.path.exists(REGISTRY):
        return set()
    src = open(REGISTRY).read()
    return set(re.findall(r'"([a-z0-9_]+)"\s*,?\s*\n?\s*(?:==|\))', src)) \
        or set(re.findall(r'name == "([a-z0-9_]+)"', src))


def all_dsp():
    d = os.path.join(ROOT, "instruments")
    return sorted(os.path.splitext(f)[0] for f in os.listdir(d) if f.endswith(".dsp"))


def usage_counts():
    """How many songs use each voice/fx (source id + fx id, tracks/buses/master)."""
    counts = {}
    for f in os.listdir(SONGS):
        if not f.endswith(".json") or f.startswith(("_bench_", "_null_")):
            continue
        try:
            s = json.load(open(os.path.join(SONGS, f)))
        except Exception:
            continue
        used = set()
        def fx_ids(fx):
            for e in fx or []:
                i = e.get("id", "")
                if isinstance(i, str) and not i.startswith("vst3:"):
                    used.add(i)
        for t in s.get("tracks", []):
            src = t.get("source") or {}
            if src.get("kind") == "faust":
                used.add(src.get("id") or src.get("name") or "")
            fx_ids(t.get("fx"))
        for b in s.get("buses", []):
            fx_ids(b.get("fx"))
        fx_ids(s.get("master"))
        for u in used:
            if u:
                counts[u] = counts.get(u, 0) + 1
    return counts


def _render_timed(song_path, out):
    t0 = time.monotonic()
    r = subprocess.run([M1, "render", song_path, out], capture_output=True,
                       text=True, timeout=1200)
    dt = time.monotonic() - t0
    ok = "ok=1" in (r.stdout + r.stderr)
    m = re.search(r"len=([\d.]+)s", r.stdout + r.stderr)
    return (dt, float(m.group(1)) if m else None) if ok else (None, None)


def price_song(song_path):
    song = json.load(open(song_path))
    aot = aot_names()
    tmp = os.path.join(SONGS, "_cost_solo.json")
    out = os.path.join(SONGS, "_cost_solo.wav")
    rows = []
    # baseline: full song
    full_dt, song_len = _render_timed(song_path, out)
    for i, t in enumerate(song.get("tracks", [])):
        solo = json.loads(json.dumps(song))
        for j, tt in enumerate(solo["tracks"]):
            tt["muted"] = (j != i)
        with open(tmp, "w") as f:
            json.dump(solo, f)
        dt, ln = _render_timed(tmp, out)
        src = (t.get("source") or {})
        voice = src.get("id") or src.get("name") if src.get("kind") == "faust" else src.get("kind")
        rows.append({
            "track": t.get("name"), "voice": voice,
            "jit": (voice not in aot) if (voice and src.get("kind") == "faust") else None,
            "n_fx": len(t.get("fx") or []),
            "solo_render_s": round(dt, 2) if dt else None,
            "rt_factor": round(dt / ln, 3) if dt and ln else None,
        })
    for p in (tmp, out):
        if os.path.exists(p):
            os.remove(p)
    rows.sort(key=lambda r: -(r["solo_render_s"] or 0))
    return {"song": os.path.basename(song_path), "song_len_s": song_len,
            "full_render_s": round(full_dt, 2) if full_dt else None,
            "full_rt_factor": round(full_dt / song_len, 3) if full_dt and song_len else None,
            "tracks_by_cost": rows, "machine": socket.gethostname()}


def price_voices(top=None):
    aot = aot_names()
    use = usage_counts()
    tmp = os.path.join(SONGS, "_cost_v.json")
    out = os.path.join(SONGS, "_cost_v.wav")
    names = all_dsp()
    if top:
        by_use = sorted(names, key=lambda n: -use.get(n, 0))[:top]
        jit_used = [n for n in names if n not in aot and use.get(n, 0) > 0]
        names = sorted(set(by_use) | set(jit_used),
                       key=lambda n: -use.get(n, 0))   # candidates ALWAYS priced
    rows = []
    for n in names:
        if n.startswith("fx_") or n == "master_limiter":
            continue
        song = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0,
                "master": [],
                "tracks": [{"name": "p", "source": {"kind": "faust", "id": n},
                            "gainDb": 0.0,
                            "notes": [{"start": b, "len": 0.45, "pitch": 60,
                                       "vel": 0.9} for b in range(8)]}]}
        with open(tmp, "w") as f:
            json.dump(song, f)
        dt, ln = _render_timed(tmp, out)
        rows.append({"voice": n, "jit": n not in aot, "usage": use.get(n, 0),
                     "render_s": round(dt, 2) if dt else None,
                     "rt_factor": round(dt / ln, 3) if dt and ln else None})
        print(f"  [{len(rows):2d}] {n:24s} {'JIT' if n not in aot else 'AOT'} "
              f"{(dt or 0):6.2f}s  use={use.get(n, 0)}", flush=True)
    for p in (tmp, out):
        if os.path.exists(p):
            os.remove(p)
    # E7: promotion worklist = JIT voices by (usage x cost); freeze list = unused AOT
    jit = [r for r in rows if r["jit"] and r["render_s"]]
    for r in jit:
        r["promote_score"] = round((r["usage"] + 0.5) * r["render_s"], 2)
    jit.sort(key=lambda r: -r["promote_score"])
    return {"voices": rows,
            "promotion_worklist": [r["voice"] for r in jit[:12]],
            "machine": socket.gethostname(),
            "law": "E7: promote by usage x cost, not by memory"}


def census():
    aot = aot_names()
    use = usage_counts()
    names = all_dsp()
    jit = [n for n in names if n not in aot]
    return {"total_dsp": len(names), "aot": len(names) - len(jit),
            "jit": sorted(jit),
            "jit_used": sorted([n for n in jit if use.get(n, 0) > 0],
                               key=lambda n: -use.get(n, 0)),
            "usage_top": dict(sorted(use.items(), key=lambda kv: -kv[1])[:20]),
            "machine": socket.gethostname()}


def main():
    a = sys.argv[1:]
    if "--census" in a:
        print("COST_JSON " + json.dumps(census()))
        return 0
    if "--voices" in a:
        top = int(a[a.index("--top") + 1]) if "--top" in a else None
        print("COST_JSON " + json.dumps(price_voices(top)))
        return 0
    song = a[a.index("--song") + 1] if "--song" in a else os.path.join(SONGS, "eval_funk.json")
    print("COST_JSON " + json.dumps(price_song(song)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
