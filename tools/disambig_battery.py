#!/usr/bin/env python3
"""DISAMBIGUATION GATE battery (BEST_DAW_30 #13b) — locate asks, never guesses.

Two plucks and a vague ask -> the AMBIGUITY GATE fires: the tool result carries
the do-not-guess law verbatim and agent/ipc/candidates.json lands atomically for
the UI chips. A uniquely-named target stays gate-free. Pure + local (direct
t_locate calls on a scratch song). Run: python3 tools/disambig_battery.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import daw_mcp

SONGS = os.path.join(ROOT, "songs")
CAND = os.path.join(ROOT, "agent", "ipc", "candidates.json")
NAME = "_disambig_bat"
fails = []


def check(tag, ok, detail=""):
    print(f"  {'ok' if ok else 'XX'} {tag} {detail}")
    if not ok:
        fails.append(tag)


def main():
    song = {"bpm": 120, "lengthBars": 4, "tracks": [
        {"name": "pluck_soft", "source": {"kind": "faust", "id": "pluck"},
         "notes": [{"start": 0.0, "len": 0.4, "pitch": 60, "vel": 0.6}]},
        {"name": "pluck_hard", "source": {"kind": "faust", "id": "pluck2"},
         "notes": [{"start": 1.0, "len": 0.4, "pitch": 64, "vel": 0.9}]},
        {"name": "kick", "source": {"kind": "faust", "id": "kick_punch"},
         "notes": [{"start": 0.0, "len": 0.2, "pitch": 36, "vel": 0.9}]}]}
    json.dump(song, open(os.path.join(SONGS, f"{NAME}.json"), "w"))
    before = os.path.getmtime(CAND) if os.path.exists(CAND) else 0
    try:
        out = daw_mcp.t_locate({"song": NAME, "query": "pluck"})
        check("ambiguous ask flags AMBIGUOUS", "AMBIGUOUS CANDIDATES" in out)
        check("the gate speaks the law", "do NOT guess" in out and "AMBIGUITY GATE" in out)
        check("dry-run guidance rides", "select_notes on EACH candidate" in out)
        check("candidates.json landed",
              os.path.exists(CAND) and os.path.getmtime(CAND) >= before)
        if os.path.exists(CAND):
            c = json.load(open(CAND))
            names = [o["track"] for o in c.get("options", [])]
            check("chip options carry both plucks",
                  c.get("song") == NAME and "pluck_soft" in names
                  and "pluck_hard" in names, str(names))
            check("options carry score+why",
                  all("score" in o and "why" in o for o in c["options"]))
        out2 = daw_mcp.t_locate({"song": NAME, "query": "kick"})
        check("unique target stays gate-free",
              "AMBIGUITY GATE" not in out2 and "kick" in out2)
    finally:
        for p in (os.path.join(SONGS, f"{NAME}.json"),):
            os.path.exists(p) and os.remove(p)
        # the scratch candidates drop must not linger as UI state
        if os.path.exists(CAND):
            try:
                if json.load(open(CAND)).get("song") == NAME:
                    os.remove(CAND)
            except Exception:
                pass
    print(f"disambig battery: {'clean' if not fails else 'RED ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
