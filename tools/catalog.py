#!/usr/bin/env python3
"""THE CATALOG BRAIN (A4-T2, docs/SPEC_TRANSCENDENCE.md) — the user's whole
body of work as ONE queryable corpus. Every project ever made becomes
memory: motifs, sounds, keys, tempos, scale of the catalog.

INDEX: songs/.catalog/index.json (gitignored, derived — rebuildable from the
tree at any time; incremental by mtime). Proposal/temp files never index
(_prop_/_mt_/_mtc_ prefixes are working state, not the catalog).

QUERIES:
  self_echo(song)  — THE NOVELTY COURT POINTED AT YOURSELF (N44's twin):
                     which OTHER songs share this song's melodic motifs?
                     A reprise is a feature; an accidental self-clone is a
                     warning — the caller decides, the brain reports.
  find(term)       — where did I use that sound/track/voice? (source ids +
                     track names, substring, case-folded)
  stats()          — the body of work in numbers (songs, notes, keys, bpm
                     spread, most-played voices)

CLI: catalog.py build | self-echo <song> | find <term> | stats
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_REL = os.path.join("songs", ".catalog", "index.json")
_SKIP = ("_prop_", "_mt_", "_mtc_", "_ensure_prop", "_bench_", "_tourn_",
         "_a2m", "_vtprobe", "_ux_", "_sec_test", "_podium")


def _grams(doc):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import record_court
        iv = record_court._lead_intervals(doc)
        return sorted(list(g) for g in record_court._grams(iv))
    except Exception:
        return []


def _entry(path):
    try:
        doc = json.load(open(path))
    except Exception:
        return None
    if not isinstance(doc, dict) or not isinstance(doc.get("tracks"), list):
        return None
    tracks = []
    notes_total = 0
    for t in doc["tracks"]:
        if not isinstance(t, dict):
            continue
        src = t.get("source") or {}
        n = len(t.get("notes") or [])
        notes_total += n
        tracks.append({"name": str(t.get("name", "")),
                       "source": str(src.get("id", ""))[:60], "notes": n})
    return {"key": str(doc.get("key", "")), "bpm": doc.get("bpm"),
            "bars": doc.get("lengthBars"), "notes": notes_total,
            "tracks": tracks, "grams": _grams(doc),
            "mtime": round(os.path.getmtime(path), 1)}


def build_index(root=None, force=False):
    """Incremental by mtime; returns the index dict."""
    root = root or ROOT
    ipath = os.path.join(root, INDEX_REL)
    idx = {}
    if not force and os.path.exists(ipath):
        try:
            idx = json.load(open(ipath)).get("songs", {})
        except Exception:
            idx = {}
    sdir = os.path.join(root, "songs")
    live = {}
    for fn in sorted(os.listdir(sdir) if os.path.isdir(sdir) else []):
        if not fn.endswith(".json") or fn.startswith("."):
            continue
        name = fn[:-5]
        if any(name.startswith(p) or p in name[:len(p) + 2] for p in ()) \
           or any(name.startswith(p) for p in _SKIP):
            continue
        path = os.path.join(sdir, fn)
        old = idx.get(name)
        if old and abs(old.get("mtime", 0) - os.path.getmtime(path)) < 0.5:
            live[name] = old
            continue
        e = _entry(path)
        if e:
            live[name] = e
    out = {"v": 1, "songs": live}
    os.makedirs(os.path.dirname(ipath), exist_ok=True)
    tmp = ipath + ".tmp"
    json.dump(out, open(tmp, "w"))
    os.replace(tmp, ipath)
    return out


def _load_index(root=None):
    ipath = os.path.join(root or ROOT, INDEX_REL)
    if os.path.exists(ipath):
        try:
            return json.load(open(ipath))
        except Exception:
            pass
    return build_index(root)


def self_echo(song, root=None, min_shared=2):
    """Other catalog songs sharing >= min_shared interval motifs with
    THIS song. -> {song, echoes: [{song, shared}], note}."""
    idx = _load_index(root)["songs"]
    me = idx.get(song)
    if me is None:
        return {"error": f"'{song}' not in the catalog (build first?)"}
    mine = {tuple(g) for g in me.get("grams", [])}
    echoes = []
    for other, e in idx.items():
        if other == song:
            continue
        shared = mine & {tuple(g) for g in e.get("grams", [])}
        if len(shared) >= min_shared:
            echoes.append({"song": other, "shared": len(shared)})
    echoes.sort(key=lambda x: -x["shared"])
    return {"song": song, "echoes": echoes,
            "note": (f"this melody echoes {len(echoes)} of your own songs "
                     "(a reprise is a feature; an accidental self-clone is "
                     "a warning)" if echoes else
                     "no other song of yours shares these motifs — fresh "
                     "material")}


def find(term, root=None):
    """Substring search over source ids + track names, case-folded."""
    t = str(term).lower()
    idx = _load_index(root)["songs"]
    hits = []
    for name, e in sorted(idx.items()):
        where = []
        for tr in e.get("tracks", []):
            if t in tr["name"].lower() or t in tr["source"].lower():
                where.append(tr["name"] + (f" ({tr['source']})"
                                           if tr["source"] else ""))
        if where:
            hits.append({"song": name, "lanes": where[:6]})
    return {"term": term, "hits": hits, "n": len(hits)}


def stats(root=None):
    idx = _load_index(root)["songs"]
    keys, voices = {}, {}
    bpms = []
    notes = 0
    for e in idx.values():
        k = e.get("key") or "?"
        keys[k] = keys.get(k, 0) + 1
        if isinstance(e.get("bpm"), (int, float)) and e["bpm"]:
            bpms.append(float(e["bpm"]))
        notes += int(e.get("notes") or 0)
        for tr in e.get("tracks", []):
            s = tr.get("source") or ""
            if s:
                voices[s] = voices.get(s, 0) + 1
    return {"songs": len(idx), "notes": notes,
            "keys": dict(sorted(keys.items(), key=lambda x: -x[1])[:8]),
            "bpm": ({"min": min(bpms), "max": max(bpms),
                     "median": sorted(bpms)[len(bpms) // 2]} if bpms else {}),
            "voices": dict(sorted(voices.items(), key=lambda x: -x[1])[:10])}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "build":
        out = build_index(force="--force" in a)
        print(f"catalog: {len(out['songs'])} songs indexed -> {INDEX_REL}")
    elif a[0] == "self-echo" and len(a) > 1:
        print(json.dumps(self_echo(re.sub(r"\.json$", "", a[1])), indent=1))
    elif a[0] == "find" and len(a) > 1:
        print(json.dumps(find(a[1]), indent=1))
    elif a[0] == "stats":
        print(json.dumps(stats(), indent=1))
    else:
        print(__doc__)
