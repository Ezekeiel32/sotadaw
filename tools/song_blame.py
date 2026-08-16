#!/usr/bin/env python3
"""BLAME, PER NOTE (THE_UTMOST §14.4 + §6 authorship ledger: every note answers
who / when / which ask).

Accept = git commit is the house law, so the data has always existed — this is
the surface. Walk the song file's git history oldest->newest; a note's birth is
its most recent absent->present transition (a re-added note blames its re-add,
not its ancestor). The WORKING file is the final state, so hand edits not yet
committed blame honestly as "uncommitted (hands)". Each birth commit joins its
telemetry verdict row (the ask, verbatim) when one lands within the join window.

  blame <song> [--track T] [--from-beat A] [--to-beat B] [--pitch P] [--depth N]
  note  <song> <track> <beat> <pitch>          # one note's whole story
  --selftest                                   # deterministic proof (suite leg)

Note identity: (track, start rounded 1e-3, pitch). Read-only everywhere.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    from songname import resolve_song_name  # SONG-NAME LAW
except Exception:
    resolve_song_name = None

JOIN_WINDOW_S = 6 * 3600  # verdict rows stamp at accept time ~= commit time


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                          text=True, check=False)


def note_keys(doc):
    """{(track, start, pitch): note} for every note in a song dict."""
    out = {}
    for tr in (doc or {}).get("tracks", []) or []:
        name = tr.get("name") or "?"
        for n in tr.get("notes", []) or []:
            try:
                out[(name, round(float(n.get("start", 0)), 3), int(n.get("pitch", -1)))] = n
            except (TypeError, ValueError):
                continue
    return out


def history(repo, rel_path, depth):
    """[(sha, epoch, subject)] oldest -> newest."""
    r = _git(repo, "log", f"-{depth}", "--format=%H|%ct|%s", "--", rel_path)
    rows = []
    for line in r.stdout.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            rows.append((parts[0], int(parts[1]), parts[2]))
    rows.reverse()
    return rows


def blame_song(repo, rel_path, depth=200, telemetry_rows=None):
    """-> (births, commits). births: key -> {"sha","t","subject"} or
    {"sha": None} for uncommitted; commits: sha -> meta incl. joined ask."""
    commits = history(repo, rel_path, depth)
    prev = {}
    births = {}
    meta = {}
    for sha, t, subject in commits:
        r = _git(repo, "show", f"{sha}:{rel_path}")
        try:
            cur = note_keys(json.loads(r.stdout))
        except ValueError:
            cur = prev  # unparseable revision — attribute nothing to it
        for k in cur.keys() - prev.keys():
            births[k] = sha
        for k in prev.keys() - cur.keys():
            births.pop(k, None)  # removed: if re-added later, the re-add blames
        meta[sha] = {"t": t, "subject": subject, "ask": None, "accepted": None}
        prev = cur
    # working file = the live truth; new keys here are uncommitted hand/agent work
    try:
        live = note_keys(json.load(open(os.path.join(repo, rel_path))))
    except (OSError, ValueError):
        live = prev
    for k in live.keys() - prev.keys():
        births[k] = None
    # blame only what is ALIVE now
    births = {k: v for k, v in births.items() if k in live}
    # join the ask verbatim from telemetry (nearest row inside the window)
    song = os.path.splitext(os.path.basename(rel_path))[0]
    for row in telemetry_rows or []:
        if row.get("song") != song or not isinstance(row.get("prompt"), str):
            continue
        rt = float(row.get("t", 0))
        best = None
        # newest-first + strict compare: a verdict stamps AFTER its accept
        # commit, so among distance ties the newest commit is the one judged
        for sha, m in reversed(list(meta.items())):
            d = abs(m["t"] - rt)
            if d < JOIN_WINDOW_S and (best is None or d < best[0]):
                best = (d, sha)
        if best and (meta[best[1]]["ask"] is None or best[0] < meta[best[1]].get("_ask_d", 1e18)):
            meta[best[1]].update(ask=row["prompt"], accepted=row.get("accepted"),
                                 _ask_d=best[0])
    return births, meta, live


def load_telemetry(path):
    rows = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return rows


def _fmt_when(t):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(t))


def cmd_blame(song, track=None, from_beat=None, to_beat=None, pitch=None, depth=200):
    name = resolve_song_name(song) if resolve_song_name else song
    rel = os.path.join("songs", f"{name}.json")
    births, meta, live = blame_song(ROOT, rel, depth,
                                    load_telemetry(os.path.join(ROOT, "telemetry", "proposals.jsonl")))
    picked = {}
    for k, sha in births.items():
        tname, beat, p = k
        if track and tname != track:
            continue
        if from_beat is not None and beat < from_beat:
            continue
        if to_beat is not None and beat >= to_beat:
            continue
        if pitch is not None and p != pitch:
            continue
        picked.setdefault(sha, []).append(k)
    total = sum(len(v) for v in picked.values())
    scope = track or "all tracks"
    print(f"BLAME {name} — {total} living notes attributed ({scope})")
    order = sorted(picked.keys(), key=lambda s: -(meta[s]["t"] if s else time.time()))
    for sha in order:
        keys = picked[sha]
        per_track = {}
        for tname, _, _ in keys:
            per_track[tname] = per_track.get(tname, 0) + 1
        tr_s = ", ".join(f"{t}:{n}" for t, n in sorted(per_track.items(), key=lambda x: -x[1])[:6])
        if sha is None:
            print(f"  UNCOMMITTED (hands/live)          {len(keys):>5} notes  [{tr_s}]")
            continue
        m = meta[sha]
        ask = f'  ask: "{m["ask"][:90]}"' if m.get("ask") else ""
        print(f"  {sha[:7]} {_fmt_when(m['t'])}  {len(keys):>5} notes  [{tr_s}]  '{m['subject'][:60]}'{ask}")
    return 0


def cmd_note(song, track, beat, p):
    name = resolve_song_name(song) if resolve_song_name else song
    rel = os.path.join("songs", f"{name}.json")
    births, meta, live = blame_song(ROOT, rel, 200,
                                    load_telemetry(os.path.join(ROOT, "telemetry", "proposals.jsonl")))
    key = (track, round(float(beat), 3), int(p))
    if key not in live:
        near = [k for k in live if k[0] == track and abs(k[1] - key[1]) < 1.0]
        print(f"no living note {key}; near on {track}: {sorted(near)[:6]}")
        return 1
    sha = births.get(key)
    if sha is None:
        print(f"{track} beat {beat} pitch {p}: UNCOMMITTED — born of hands (or a take not yet kept)")
        return 0
    m = meta[sha]
    print(f"{track} beat {beat} pitch {p}: born {sha[:9]} on {_fmt_when(m['t'])}")
    print(f"  commit: {m['subject']}")
    if m.get("ask"):
        v = {True: "KEPT", False: "PASSED"}.get(m.get("accepted"), "?")
        print(f'  the ask ({v}): "{m["ask"][:200]}"')
    return 0


def selftest():
    ok = [0]
    def check(name, cond):
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        ok[0] += 1
    def note(s, p):
        return {"start": s, "len": 0.5, "pitch": p, "vel": 0.9}
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "songs"))
        _git(td, "init", "-q")
        _git(td, "config", "user.email", "t@t")
        _git(td, "config", "user.name", "t")
        rel = os.path.join("songs", "toy.json")
        path = os.path.join(td, rel)
        def commit(doc, msg):
            json.dump(doc, open(path, "w"))
            _git(td, "add", rel)
            _git(td, "commit", "-q", "-m", msg)
            return _git(td, "rev-parse", "HEAD").stdout.strip()
        c1 = commit({"tracks": [{"name": "kick", "notes": [note(0, 36), note(4, 36)]}]}, "seed")
        c2 = commit({"tracks": [{"name": "kick", "notes": [note(0, 36), note(4, 36)]},
                                {"name": "keys", "notes": [note(2, 60)]}]}, "add keys")
        c3 = commit({"tracks": [{"name": "kick", "notes": [note(0, 36)]},
                                {"name": "keys", "notes": [note(2, 60), note(6, 64)]}]}, "drop hit + extend")
        births, meta, live = blame_song(td, rel, 50)
        check("survivor blames its seed commit", births[("kick", 0.0, 36)] == c1)
        check("new-track note blames its commit", births[("keys", 2.0, 60)] == c2)
        check("later add blames later commit", births[("keys", 6.0, 64)] == c3)
        check("removed note is not blamed", ("kick", 4.0, 36) not in births)
        c4 = commit({"tracks": [{"name": "kick", "notes": [note(0, 36), note(4, 36)]},
                                {"name": "keys", "notes": [note(2, 60), note(6, 64)]}]}, "re-add hit")
        births, meta, live = blame_song(td, rel, 50)
        check("re-added note blames the RE-ADD, not its ancestor", births[("kick", 4.0, 36)] == c4)
        # uncommitted hand edit -> honest attribution
        doc = json.load(open(path))
        doc["tracks"][0]["notes"].append(note(8, 36))
        json.dump(doc, open(path, "w"))
        births, meta, live = blame_song(td, rel, 50)
        check("working-tree note blames UNCOMMITTED", births[("kick", 8.0, 36)] is None)
        # telemetry ask joins the nearest commit inside the window
        t_c4 = meta[c4]["t"]
        rows = [{"song": "toy", "t": t_c4 + 5, "prompt": "bring the hit back", "accepted": True},
                {"song": "other", "t": t_c4, "prompt": "wrong song", "accepted": True}]
        births, meta, live = blame_song(td, rel, 50, rows)
        check("ask joins its commit verbatim", meta[c4]["ask"] == "bring the hit back")
        check("foreign-song ask never joins", all(m.get("ask") != "wrong song" for m in meta.values()))
        # unparseable revision attributes nothing (poison law)
        open(path, "w").write("{torn")
        _git(td, "add", rel)
        _git(td, "commit", "-q", "-m", "torn rev")
        json.dump(doc, open(path, "w"))
        _git(td, "add", rel)
        _git(td, "commit", "-q", "-m", "healed")
        births2, meta2, _ = blame_song(td, rel, 50)
        check("torn revision poisons nothing (survivors keep their birth)",
              births2[("kick", 0.0, 36)] == c1)
    print(f"SONG BLAME SELFTEST: {ok[0]}/9 PASS")
    return 0 if ok[0] == 9 else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = sys.argv[1:]
    def fval(name, cast=str):
        if name in flags:
            i = flags.index(name)
            if i + 1 < len(flags):
                return cast(flags[i + 1])
        return None
    if args and args[0] == "note" and len(args) >= 5:
        return cmd_note(args[1], args[2], args[3], args[4])
    if args and args[0] == "blame" and len(args) >= 2:
        return cmd_blame(args[1], track=fval("--track"),
                         from_beat=fval("--from-beat", float), to_beat=fval("--to-beat", float),
                         pitch=fval("--pitch", int), depth=fval("--depth", int) or 200)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
