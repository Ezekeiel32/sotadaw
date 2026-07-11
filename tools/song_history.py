#!/usr/bin/env python3
"""song_history.py — the TIME MACHINE's semantic eyes: per-commit TRACK truth.

For every commit that touched songs/<song>.json, diff the song JSON at <sha> vs its
parent and report WHICH TRACKS changed and by how much: notes added/removed per track,
property-level changes (gain/pan/fx/source/sends/automation), tracks added/removed.
Diff-truth covers ALL history since day one — including commits older than the SCALPEL
receipts. Output: one JSON line per commit (newest first), consumed by HistoryPanel.

  tools/song_history.py <song> [--limit 100]
  -> {"sha","age","subject","kind","added","removed","tracks":{name:{"a":n,"r":n,"p":[...]}},
      "touched":[names]}   (kind: 0 accept · 1 agent/sweep · 2 named-milestone)
"""
import argparse, json, os, subprocess, sys, time

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                      text=True).stdout.strip()


def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else ""


def load_at(sha, path):
    txt = git("show", f"{sha}:{path}")
    if not txt:
        return None
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return None


def note_key(n):
    return (round(float(n.get("start", 0)), 4), int(n.get("pitch", 60)),
            round(float(n.get("len", 0.25)), 4), round(float(n.get("vel", 0.8)), 3))


def track_props(t):
    """Comparable fingerprint of everything that is not notes."""
    return {
        "gainDb": t.get("gainDb", 0), "pan": t.get("pan", 0),
        "muted": t.get("muted", False),
        "source": json.dumps(t.get("source", {}), sort_keys=True),
        "fx": json.dumps(t.get("fx", []), sort_keys=True),
        "sends": json.dumps(t.get("sends", []), sort_keys=True),
        "automation": json.dumps(t.get("automation", []), sort_keys=True),
        "audioClips": json.dumps(t.get("audioClips", []), sort_keys=True),
    }


GRID_W = 240  # time cells per strip — density is TRUE at any song length

def _pts(notes):
    """notes -> compact [beat, pitch, len] triplets for the filmstrip."""
    return [[round(float(n.get("start", 0)), 2), int(n.get("pitch", 60)),
             round(float(n.get("len", 0.25)), 2)] for n in notes]


def _sample(lst, n):
    if n <= 0:
        return []
    if len(lst) <= n:
        return lst
    step = len(lst) / n
    return [lst[int(i * step)] for i in range(n)]


def _grid(kept, clips, beats):
    """Kept material as hex intensity rows (pitch thirds when melodic).

    Sampling points would paint a sparse LIE on dense songs — a grid keeps
    density true at fixed cost. Rows: [low,mid,high] pitch thirds, or one
    row for flat-pitch (drum) lanes. Cell 0..f, sqrt curve for visibility."""
    if not kept and not clips:
        return []
    pitches = [int(n.get("pitch", 60)) for n in kept]
    lo, hi = (min(pitches), max(pitches)) if pitches else (60, 60)
    nrows = 3 if hi - lo >= 3 else 1
    cells = [[0.0] * GRID_W for _ in range(nrows)]
    scale = GRID_W / max(beats, 1e-6)
    for n in kept:
        c = min(GRID_W - 1, int(float(n.get("start", 0)) * scale))
        row = 0 if nrows == 1 else min(2, (int(n.get("pitch", 60)) - lo) * 3 // max(1, hi - lo + 1))
        cells[(nrows - 1) - row if nrows == 3 else 0][c] += 1.0   # top row = high pitch
    for c in clips:  # audio clips: sustained energy across their whole span
        a = max(0, min(GRID_W - 1, int(float(c.get("startBeat", 0)) * scale)))
        b = max(a, min(GRID_W - 1, int((float(c.get("startBeat", 0))
                                        + float(c.get("lengthBeats", 4))) * scale)))
        for i in range(a, b + 1):
            cells[nrows // 2][i] += 0.75
    peak = max(max(r) for r in cells) or 1.0
    return ["".join("%x" % min(15, int(15 * (v / peak) ** 0.5 + 0.5)) for v in row)
            for row in cells]


def diff_songs(base, prop):
    """(tracks{name:{a,r,p[]}}, total_added, total_removed, strips[])
    strips = the WHOLE song at this version painted with the diff:
    per track {n, pr, k(ept)/a(dded)/r(emoved): [[beat,pitch,len]...]} — base may be None."""
    bt = {t.get("name", f"#{i}"): t for i, t in enumerate((base or {}).get("tracks", []))}
    pt = {t.get("name", f"#{i}"): t for i, t in enumerate((prop or {}).get("tracks", []))}
    # strip order = the song's own lane order at this version, removed lanes appended
    order = [t.get("name", f"#{i}") for i, t in enumerate((prop or {}).get("tracks", []))]
    order += [n for n in bt if n not in pt]
    out = {}
    strips = []
    ta = tr = 0
    for name in order:
        b, p = bt.get(name), pt.get(name)
        kept, added, removed, props = [], [], [], []
        if b is None and p is not None:
            added = list(p.get("notes", []))
            props = ["track added"]
        elif p is None and b is not None:
            removed = list(b.get("notes", []))
            props = ["track removed"]
        else:
            bk = {}
            for n in b.get("notes", []):
                bk[note_key(n)] = bk.get(note_key(n), 0) + 1
            for n in p.get("notes", []):
                k = note_key(n)
                if bk.get(k, 0) > 0:
                    bk[k] -= 1
                    kept.append(n)
                else:
                    added.append(n)
            pk = {}
            for n in p.get("notes", []):
                pk[note_key(n)] = pk.get(note_key(n), 0) + 1
            for n in b.get("notes", []):
                k = note_key(n)
                if pk.get(k, 0) > 0:
                    pk[k] -= 1
                else:
                    removed.append(n)
            props = [k for k, v in track_props(b).items() if track_props(p)[k] != v]
        if added or removed or props:
            out[name] = {"a": len(added), "r": len(removed), "p": props}
            ta += len(added)
            tr += len(removed)
        strips.append({"n": name, "_kept": kept, "_clips": (p or {}).get("audioClips", []),
                       "_pr": bool(props and set(props) - {"track added", "track removed"}),
                       "a": _pts(added), "r": _pts(removed)})
    beats = 0.0
    for s in strips:
        for n in s["_kept"]:
            beats = max(beats, float(n.get("start", 0)) + float(n.get("len", 0.25)))
        for c in s["_clips"]:
            beats = max(beats, float(c.get("startBeat", 0)) + float(c.get("lengthBeats", 4)))
        for src in (s["a"], s["r"]):
            for b_, _, l_ in src:
                beats = max(beats, b_ + l_)
    final = []
    for s in strips:
        g = _grid(s["_kept"], s["_clips"], beats)
        strip = {"n": s["n"], "g": g,
                 "a": _sample(s["a"], 350), "r": _sample(s["r"], 350)}
        if s["_pr"]:
            strip["pr"] = 1
        if g or strip["a"] or strip["r"]:
            final.append(strip)
    # global diff budget: birth commits are ALL added — keep rows bounded (~1200 pts)
    dtot = sum(len(s["a"]) + len(s["r"]) for s in final)
    if dtot > 1200:
        for s in final:
            s["a"] = _sample(s["a"], max(1, len(s["a"]) * 1200 // dtot) if s["a"] else 0)
            s["r"] = _sample(s["r"], max(1, len(s["r"]) * 1200 // dtot) if s["r"] else 0)
    return out, ta, tr, final


def song_extent(song):
    """(beats, mass) — length of the tape and how many notes live on it."""
    beats, mass = 0.0, 0
    for t in (song or {}).get("tracks", []):
        for n in t.get("notes", []):
            beats = max(beats, float(n.get("start", 0)) + float(n.get("len", 0.25)))
        for c in t.get("audioClips", []):
            beats = max(beats, float(c.get("startBeat", 0)) + float(c.get("lengthBeats", 4)))
        mass += len(t.get("notes", []))
    return round(beats, 2), mass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--limit", type=int, default=100)
    a = ap.parse_args()
    path = f"songs/{a.song}.json"
    log = git("log", f"--format=%h|%ct|%ar|%s", f"-{a.limit}", "--", path)
    shas = [l.split("|", 3) for l in log.splitlines() if l.count("|") >= 3]
    cache = {}

    def songat(sha, p=path):
        if (sha, p) not in cache:
            cache[(sha, p)] = load_at(sha, p)
        return cache[(sha, p)]

    rows = []
    for i, (sha, ct, age, subject) in enumerate(shas):
        parent = shas[i + 1][0] if i + 1 < len(shas) else None
        cur = songat(sha)
        prev = songat(parent) if parent else None
        tracks, added, removed, strips = diff_songs(prev, cur)
        beats, mass = song_extent(cur)
        kind = 0 if subject.startswith("accept proposal on ") \
            else 2 if a.song.lower() in subject.lower() else 1
        rows.append({"sha": sha, "epoch": int(ct), "age": age, "subject": subject,
                     "kind": kind, "path": path, "added": added, "removed": removed,
                     "beats": beats, "mass": mass, "strips": strips,
                     "tracks": tracks, "touched": sorted(tracks)})

    # REJECTED / SUPERSEDED TAKES: version control covers the whole conversation.
    # Each take commit ADDS one file under songs/.takes/<song>/ — diffed vs the
    # BASE at that same commit (what the take would have changed).
    tlog = git("log", f"--format=C|%h|%ct|%ar|%s", "--name-only",
               "--diff-filter=A", f"-{a.limit}", "--", f"songs/.takes/{a.song}")
    meta = None
    for line in tlog.splitlines():
        if line.startswith("C|"):
            meta = line.split("|", 4)[1:]
        elif line.strip().startswith(f"songs/.takes/{a.song}/") and meta:
            sha, ct, age, subject = meta
            tp = line.strip()
            take = songat(sha, tp)
            base = songat(sha)
            tracks, added, removed, strips = diff_songs(base, take)
            beats, mass = song_extent(take)
            rows.append({"sha": sha, "epoch": int(ct), "age": age, "subject": subject,
                         "kind": 3 if "_rejected" in tp else 4, "path": tp,
                         "added": added, "removed": removed,
                         "beats": beats, "mass": mass, "strips": strips,
                         "tracks": tracks, "touched": sorted(tracks)})

    # JOURNAL MOMENTS (R7): the crash net's unsaved saves join the timeline.
    # The ring keeps ~15 crumbs/song seconds apart — ONE row per minute (latest
    # wins) or the drawer is all crumbs and no story; a crumb identical to HEAD
    # is silence, not history. sha "journal<epoch>" marks a DISK-backed row
    # (previewHistory reads the file, not git).
    jdir = os.path.join(ROOT, "songs", ".journal")
    if os.path.isdir(jdir):
        by_min = {}
        for f in sorted(os.listdir(jdir)):
            if f.startswith(a.song + "-") and f.endswith(".json"):
                stamp = f[len(a.song) + 1:-5]
                if stamp.isdigit():
                    by_min[int(stamp) // 60000] = f
        head = songat(shas[0][0]) if shas else None
        now = int(time.time())
        for f in by_min.values():
            ct = int(f[len(a.song) + 1:-5]) // 1000
            try:
                cur = json.load(open(os.path.join(jdir, f)))
            except Exception:
                continue
            tracks, added, removed, strips = diff_songs(head, cur)
            if not tracks and not added and not removed:
                continue                       # the moment IS the head — no row
            beats, mass = song_extent(cur)
            mins = max(0, now - ct) // 60
            age = (f"{mins} minutes ago" if mins < 60 else
                   f"{mins // 60} hours ago" if mins < 1440 else
                   f"{mins // 1440} days ago")
            rows.append({"sha": f"journal{ct}", "epoch": ct, "age": age,
                         "subject": "journal moment (crash net, unsaved)",
                         "kind": 4, "path": f"songs/.journal/{f}",
                         "added": added, "removed": removed, "beats": beats,
                         "mass": mass, "strips": strips, "tracks": tracks,
                         "touched": sorted(tracks)})

    rows.sort(key=lambda r: -r["epoch"])
    for r in rows:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
