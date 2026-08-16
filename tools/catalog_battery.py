#!/usr/bin/env python3
"""THE CATALOG BRAIN battery (A4-T2, docs/SPEC_TRANSCENDENCE.md). Pure,
tempdir-isolated."""
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as cat

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def write_song(root, name, lead=None, source="acid303", key="A minor",
               bpm=120):
    tracks = [{"name": "kick", "source": {"id": "kick_808"},
               "notes": [{"start": 0.0, "pitch": 36, "vel": 0.9,
                          "len": 0.5}]}]
    if lead:
        tracks.append({"name": "lead", "source": {"id": source},
                       "notes": [{"start": float(i), "pitch": p, "vel": 0.8,
                                  "len": 0.5} for i, p in enumerate(lead)]})
    doc = {"key": key, "bpm": bpm, "lengthBars": 8, "tracks": tracks}
    p = os.path.join(root, "songs", f"{name}.json")
    json.dump(doc, open(p, "w"))
    return p


def main():
    root = tempfile.mkdtemp(prefix="cat_bat_")
    os.makedirs(os.path.join(root, "songs"))
    try:
        motif = [60, 64, 67, 65, 62, 60, 64, 67, 65, 62]
        write_song(root, "alpha", lead=motif)
        write_song(root, "beta", lead=[48, 50] + motif, source="reese_bass")
        write_song(root, "gamma", lead=[70, 69, 67, 66, 64, 61, 59, 56],
                   source="pad_warm")
        json.dump({"tracks": [{"name": "x",
                               "notes": [{"start": 0.0, "pitch": 60,
                                          "vel": 1, "len": 1}]}]},
                  open(os.path.join(root, "songs", "_prop_alpha.json"), "w"))
        json.dump({"garbage": True},
                  open(os.path.join(root, "songs", "broken.json"), "w"))

        idx = cat.build_index(root)
        ok(set(idx["songs"]) == {"alpha", "beta", "gamma"},
           f"index skips props + non-songs ({sorted(idx['songs'])})")
        ok(idx["songs"]["alpha"]["notes"] == 11, "note counts fold")

        # incremental: untouched files keep entries; touched re-index
        e0 = idx["songs"]["gamma"]
        idx2 = cat.build_index(root)
        ok(idx2["songs"]["gamma"] == e0, "incremental keeps untouched entries")
        time.sleep(0.02)
        write_song(root, "gamma", lead=[60, 62, 64], source="pad_warm")
        os.utime(os.path.join(root, "songs", "gamma.json"),
                 (time.time() + 2, time.time() + 2))
        idx3 = cat.build_index(root)
        ok(idx3["songs"]["gamma"]["notes"] != e0["notes"],
           "touched file re-indexes")

        se = cat.self_echo("alpha", root)
        ok([e["song"] for e in se["echoes"]] == ["beta"],
           "self-echo finds the shared motif in beta only")
        ok("echoes 1 of your own songs" in se["note"], "echo note honest")
        se2 = cat.self_echo("gamma", root)
        ok(se2["echoes"] == [] and "fresh material" in se2["note"],
           "no echo = fresh material note")
        ok("error" in cat.self_echo("nosuch", root),
           "unknown song = honest error")

        f = cat.find("acid", root)
        ok([h["song"] for h in f["hits"]] == ["alpha"],
           "find locates the acid303 lane")
        f2 = cat.find("kick_808", root)
        ok(f2["n"] == 3, "find sweeps all songs (kick everywhere)")

        st = cat.stats(root)
        ok(st["songs"] == 3 and st["voices"].get("kick_808") == 3,
           f"stats fold ({st['songs']} songs, kick x{st['voices'].get('kick_808')})")
        ok(st["keys"].get("A minor") == 3 and st["bpm"]["median"] == 120,
           "keys + bpm stats")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print(f"\ncatalog_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
