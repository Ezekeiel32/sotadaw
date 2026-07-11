#!/usr/bin/env python3
"""THE PROP FENCE proof (2026-07-11).

Run 9 live: the agent passed the BASE song name and clear_bars x10 +
automate x5 mutated untitled_36.json MID-RUN — the proposal law ("agent
edits _prop_ copies; base changes only on accept") was prompt convention
with no structural wall, and receipts keyed the base so the scope check
flagged 15 phantom changes.

Proves through the REAL daw_mcp tool layer:
  1. fence active + BASE name -> the write lands on the _prop_ twin,
     the base is byte-unchanged, the receipt keys the prop
  2. fence active + prop name passed explicitly -> no double-prefix
  3. fence absent -> base-name writes hit the base (CLI behavior kept)

Run: python3 tools/prop_fence_e2e.py
"""
import glob
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")


def main():
    ipc = tempfile.mkdtemp(prefix="fence_ipc_")
    os.environ["SOTADAW_IPC"] = ipc
    sys.path.insert(0, os.path.join(ROOT, "agent"))
    import daw_mcp as M
    import surgical as S

    fails = []

    def check(tag, ok, detail=""):
        print(f"  {'ok' if ok else 'XX'} {tag}" + (f"  [{detail}]" if detail and not ok else ""))
        if not ok:
            fails.append(tag)

    SONG = "_fence2e"
    for p in glob.glob(os.path.join(SONGS, f"*{SONG}*")):
        os.remove(p)
    doc = {"bpm": 120, "lengthBars": 4, "key": "A minor", "tracks": [
        {"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -4,
         "notes": [{"start": float(b), "len": 0.2, "pitch": 36, "vel": 0.9}
                   for b in range(16)]}]}
    base = os.path.join(SONGS, SONG + ".json")
    json.dump(doc, open(base, "w"))
    base_bytes = open(base, "rb").read()
    try:
        # 1) fence up: BASE name redirects to the prop twin
        json.dump({"song": SONG, "rid": 1}, open(os.path.join(ipc, "active_prop.json"), "w"))
        out = M.TOOLS["clear_bars"][0]({"song": SONG, "fromBar": 0, "toBar": 1})
        prop = os.path.join(SONGS, f"_prop_{SONG}.json")
        check("prop twin born from the base", os.path.exists(prop))
        check("base byte-unchanged through a fenced mutator",
              open(base, "rb").read() == base_bytes)
        if os.path.exists(prop):
            pj = json.load(open(prop))
            n = len(pj["tracks"][0]["notes"])
            check("the edit landed on the prop (12 notes left)", n == 12, f"n={n}")
        rcs = S.read_receipts(f"_prop_{SONG}")
        check("receipt keys the PROP name", len(rcs) >= 1
              and all(r.get("song") == f"_prop_{SONG}" for r in rcs))

        # 2) explicit prop name: no double-prefix
        nm = M.resolve_song_name(f"_prop_{SONG}")
        check("explicit prop name resolves flat (no _prop__prop_)",
              nm == f"_prop_{SONG}")

        # 3) fence down: base name means base again
        os.remove(os.path.join(ipc, "active_prop.json"))
        nm2 = M.resolve_song_name(SONG)
        check("fence down: base name resolves to base", nm2 == SONG)
        print(("PASS" if not fails else "FAIL") + f" prop-fence e2e ({6 - len(fails)}/6)")
        return 1 if fails else 0
    finally:
        for p in glob.glob(os.path.join(SONGS, f"*{SONG}*")):
            try:
                os.remove(p)
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
