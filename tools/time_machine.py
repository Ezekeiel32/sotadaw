#!/usr/bin/env python3
"""THE TIME MACHINE (THE_UTMOST §3 road: hear-any-version — history you can
audition, not just read).

Accept = git commit has always been the law, so every version of every song is
already in the vault. This gives it hands: any past version re-enters the room
as a NORMAL PROPOSAL — it ghosts onto the lanes, the deck arms, audition is
CANVAS FOLLOWS EARS, and KEEP/PASS work exactly like any take (a keep is just a
new commit; history is never rewritten). Zero new UI: the proposal rails ARE
the time machine's face.

  list <song> [--depth N]      # the vault: sha / date / what / the ask
  hear <song> <sha> [--force]  # propose that version for audition (deck arms)
  --selftest                   # isolated proof (suite leg; SOTADAW_IPC honored)

The mint obeys every proposal law: serving-shape check (corpse court's bar),
receipt filed via the surgical kernel (the empty-accept tripwire sees a real
agent edit), mint-sha stamped (hands-keep protects manual edits made after the
mint), pending-take and active-run fences refuse instead of clobbering.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import hands_keep                     # mint stamp + the accept tripwire's own eyes
import surgical                       # THE receipt kernel (never a schema copy)
try:
    from songname import resolve_song_name
except Exception:
    resolve_song_name = None

FENCE_FRESH_S = 2 * 3600


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True, check=False)


def history(repo, song, depth=30):
    rel = os.path.join("songs", f"{song}.json")
    r = _git(repo, "log", f"-{depth}", "--format=%H|%ct|%s", "--", rel)
    out = []
    for line in r.stdout.splitlines():
        p = line.split("|", 2)
        if len(p) == 3:
            out.append({"sha": p[0], "t": int(p[1]), "subject": p[2]})
    return out


def _ask_for(repo, song, t):
    """Nearest telemetry ask within 6h of a commit (newest-first tie-break)."""
    best = None
    try:
        for line in open(os.path.join(repo, "telemetry", "proposals.jsonl"),
                         errors="replace"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("song") != song or not isinstance(r.get("prompt"), str):
                continue
            d = abs(float(r.get("t", 0)) - t)
            if d < 6 * 3600 and (best is None or d < best[0]):
                best = (d, r["prompt"])
    except OSError:
        pass
    return best[1] if best else None


def cmd_list(song, depth=30, repo=ROOT):
    name = resolve_song_name(song) if resolve_song_name else song
    rows = history(repo, name, depth)
    if not rows:
        print(f"no history for {name} (a song enters the vault on its first KEEP)")
        return 1
    print(f"THE VAULT — {name}, {len(rows)} versions (newest first). "
          f"hear one: tools/time_machine.py hear {name} <sha>")
    for r in rows:
        ask = _ask_for(repo, name, r["t"])
        line = f"  {r['sha'][:7]}  {time.strftime('%Y-%m-%d %H:%M', time.localtime(r['t']))}  {r['subject'][:56]}"
        if ask:
            line += f'  ask: "{ask[:64]}"'
        print(line)
    return 0


def _emit(ipc, kind, **kw):
    ev = {"id": 0, "kind": kind, "t": round(time.time(), 1)}
    ev.update(kw)
    with open(os.path.join(ipc, "events.jsonl"), "a") as f:
        f.write(json.dumps(ev) + "\n")


def propose_version(repo, ipc, song, sha, force=False, now=None):
    """The mint. Returns (ok, message)."""
    base = os.path.join(repo, "songs", f"{song}.json")
    prop_name = f"_prop_{song}"
    prop = os.path.join(repo, "songs", f"{prop_name}.json")
    if not os.path.exists(base):
        return False, f"no such song: {base}"
    # active-run fence: never pull the floor from under a composing run
    try:
        fence = json.load(open(os.path.join(ipc, "active_prop.json")))
        if fence.get("song") == song and (now or time.time()) - float(fence.get("t", 0)) < FENCE_FRESH_S:
            return False, ("a run is composing on this song right now — "
                           "let it land (or stop it) first")
    except (OSError, ValueError):
        pass
    if os.path.exists(prop) and not force:
        return False, ("a take is already pending on this song — KEEP or PASS it "
                       "first (--force replaces it)")
    r = _git(repo, "show", f"{sha}:songs/{song}.json")
    if r.returncode != 0:
        return False, f"no version {sha[:9]} of {song} in the vault"
    try:
        doc = json.loads(r.stdout)
    except ValueError:
        return False, f"version {sha[:9]} does not parse — it cannot serve"
    if not (isinstance(doc.get("tracks"), list) and doc.get("bpm")):
        return False, (f"version {sha[:9]} is not serving-shaped (tracks/bpm) — "
                       "the corpse court would quarantine it; refusing to mint")
    meta = _git(repo, "log", "-1", "--format=%ct|%s", sha).stdout.strip()
    when, _, subject = meta.partition("|")
    stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(when or 0)))
    tmp = prop + ".tmp"
    with open(tmp, "w") as f:
        f.write(r.stdout)
    os.replace(tmp, prop)
    # the receipt (through THE kernel) + the mint sha — the accept-side laws
    # (empty-accept tripwire, hands-keep) see a first-class proposal
    old_ipc = os.environ.get("SOTADAW_IPC")
    os.environ["SOTADAW_IPC"] = ipc
    try:
        surgical.clear_receipts(prop_name)   # fresh-prop birth: per-song clear
        surgical.coarse_receipt(prop_name, "time_machine", fields=["*"],
                                summary=f"version {sha[:7]} ({stamp}) proposed for audition")
    finally:
        if old_ipc is None:
            os.environ.pop("SOTADAW_IPC", None)
        else:
            os.environ["SOTADAW_IPC"] = old_ipc
    hands_keep.stamp_mint(ipc, song, base)
    _emit(ipc, "activity", song=song,
          text=f"TIME MACHINE: proposing {sha[:7]} ({stamp}) '{subject[:60]}' — "
               "audition it, then KEEP or PASS like any take")
    _emit(ipc, "proposal", song=song, proposal=prop_name,
          surgical={"clean": True, "full_write": True, "note_changes": None,
                    "touched_tracks": [t.get("name") for t in doc.get("tracks", [])][:24]})
    return True, (f"{song} <- version {sha[:7]} ({stamp}) proposed. If the song is "
                  "open, the deck is arming now; a KEEP commits it as a NEW version "
                  "(history is never rewritten).")


def cmd_hear(song, sha, force=False):
    name = resolve_song_name(song) if resolve_song_name else song
    ipc = os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
    ok, msg = propose_version(ROOT, ipc, name, sha, force=force)
    print(("TIME MACHINE: " if ok else "refused: ") + msg)
    return 0 if ok else 1


def selftest():
    ok = [0]
    def check(name, cond):
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        ok[0] += 1
    def song_doc(pitches):
        return {"bpm": 120, "tracks": [{"name": "kick",
                "notes": [{"start": float(i), "len": 0.5, "pitch": p, "vel": 1.0}
                          for i, p in enumerate(pitches)]}]}
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "songs"))
        ipc = os.path.join(td, "ipc")
        os.makedirs(ipc)
        _git(td, "init", "-q")
        _git(td, "config", "user.email", "t@t")
        _git(td, "config", "user.name", "t")
        base = os.path.join(td, "songs", "toy.json")
        def commit(doc, msg):
            json.dump(doc, open(base, "w"))
            _git(td, "add", "songs/toy.json")
            _git(td, "commit", "-q", "-m", msg)
            return _git(td, "rev-parse", "HEAD").stdout.strip()
        c1 = commit(song_doc([36, 38]), "v1")
        c2 = commit(song_doc([36, 38, 40]), "v2")
        check("vault lists both versions newest-first",
              [h["sha"] for h in history(td, "toy")] == [c2, c1])
        okd, msg = propose_version(td, ipc, "toy", c1)
        check("hear mints the prop", okd)
        prop = json.load(open(os.path.join(td, "songs", "_prop_toy.json")))
        check("prop bytes ARE the historical version",
              len(prop["tracks"][0]["notes"]) == 2)
        check("the accept tripwire sees an agent edit",
              hands_keep.agent_receipts(ipc, "_prop_toy") == 1)
        mint = json.load(open(os.path.join(ipc, "prop_mint.json")))
        check("mint sha stamps the CURRENT base (hands-keep armed)",
              mint["toy"]["sha"] == hands_keep.sha_file(base))
        evs = [json.loads(l) for l in open(os.path.join(ipc, "events.jsonl"))]
        check("proposal event appended (deck door)",
              evs[-1]["kind"] == "proposal" and evs[-1]["proposal"] == "_prop_toy"
              and evs[-1]["song"] == "toy")
        okd, msg = propose_version(td, ipc, "toy", c2)
        check("pending take refuses a second mint", not okd and "pending" in msg)
        okd, msg = propose_version(td, ipc, "toy", c2, force=True)
        prop = json.load(open(os.path.join(td, "songs", "_prop_toy.json")))
        check("--force replaces and re-receipts (ledger = exactly 1 row)",
              okd and len(prop["tracks"][0]["notes"]) == 3
              and hands_keep.agent_receipts(ipc, "_prop_toy") == 1)
        os.remove(os.path.join(td, "songs", "_prop_toy.json"))
        json.dump({"song": "toy", "rid": 9, "t": time.time()},
                  open(os.path.join(ipc, "active_prop.json"), "w"))
        okd, msg = propose_version(td, ipc, "toy", c1)
        check("active-run fence refuses", not okd and "composing" in msg)
        json.dump({"song": "toy", "rid": 9, "t": time.time() - 3 * 3600},
                  open(os.path.join(ipc, "active_prop.json"), "w"))
        okd, _ = propose_version(td, ipc, "toy", c1)
        check("stale fence does not block", okd)
        os.remove(os.path.join(td, "songs", "_prop_toy.json"))
        c3 = commit({"bpm": 0, "tracks": None}, "husk rev")
        okd, msg = propose_version(td, ipc, "toy", c3)
        check("non-serving version refused (corpse bar), nothing minted",
              not okd and not os.path.exists(os.path.join(td, "songs", "_prop_toy.json")))
    print(f"TIME MACHINE SELFTEST: {ok[0]}/11 PASS")
    return 0 if ok[0] == 11 else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    if args and args[0] == "list" and len(args) >= 2:
        depth = 30
        if "--depth" in argv:
            depth = int(argv[argv.index("--depth") + 1])
        return cmd_list(args[1], depth)
    if args and args[0] == "hear" and len(args) >= 3:
        return cmd_hear(args[1], args[2], force="--force" in argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
