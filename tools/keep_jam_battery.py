#!/usr/bin/env python3
"""CAPTURE LAW battery — keep_jam: a kept jam becomes MATERIAL of the song.

Pure checks through daw_mcp.TOOLS (the server's own dispatch) on scratch songs:
  - default: take lands AFTER the song's end as 'jam:<role>' lanes + a section,
    notes/automation beat-offset, lengthBars extended
  - at_bar override overlays where asked; collisions suffix; sends filtered to
    buses the song actually has; receipts filed (RECEIPT LAW); bpm-delta called
    out; invalid takes blocked; empty takes refused; determinism

Usage: python3 tools/keep_jam_battery.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ISOLATION LAW: receipts go to a scratch ipc — a live session's receipts.jsonl
# (and its scope law) must never see this battery. Set BEFORE the imports read env.
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="keep_jam_ipc_")
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import daw_mcp as D
import surgical

SONGS = os.path.join(ROOT, "songs")
PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def N(start, pitch, ln=0.5, vel=0.8):
    return {"start": start, "len": ln, "pitch": pitch, "vel": vel}


def write(name, doc):
    json.dump(doc, open(os.path.join(SONGS, name + ".json"), "w"))


def load(name):
    return json.load(open(os.path.join(SONGS, name + ".json")))


def cleanup(*names):
    for n in names:
        p = os.path.join(SONGS, n + ".json")
        if os.path.exists(p):
            os.remove(p)


def main():
    tgt = {"version": 2, "bpm": 124, "lengthBars": 4, "masterGainDb": 0.0, "master": [],
           "buses": [{"id": "verb", "gainDb": 0, "fx": [{"id": "fx_reverb"}]}],
           "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                       "gainDb": -4, "pan": 0, "notes": [N(b, 36, 0.2, 1) for b in range(4)]}]}
    take = {"version": 2, "bpm": 126, "lengthBars": 2, "masterGainDb": 0.0, "master": [],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "hardkick"}, "gainDb": -5,
                 "notes": [N(0, 36, 0.2, 1), N(2, 36, 0.2, 1)],
                 "automation": [{"target": "gainDb",
                                 "points": [{"beat": 0, "v": -12}, {"beat": 8, "v": 0}]}]},
                {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -6,
                 "notes": [N(0.5, 40), N(1.5, 43)],
                 "sends": [{"bus": "verb", "gainDb": -12}, {"bus": "ghostbus", "gainDb": -9}]},
                {"name": "empty", "source": {"kind": "faust", "id": "hat"}, "notes": []}]}
    write("_kj_tgt", tgt)
    write("_kj_take", take)
    try:
        surgical.clear_receipts()
        out = D.TOOLS["keep_jam"][0]({"song": "_kj_tgt", "take": "_kj_take"})
        s = load("_kj_tgt")
        names = [t["name"] for t in s["tracks"]]
        ok(out.startswith("OK:"), f"keep_jam ran ({out[:80]})")
        ok(names == ["kick", "jam:kick", "jam:bass"],
           f"take lands as jam:<role> lanes, empty tracks skipped (got {names})")
        jk = s["tracks"][1]
        ok(jk["notes"][0]["start"] == 16.0 and jk["notes"][1]["start"] == 18.0,
           f"notes beat-offset to bar 4 (got {[n['start'] for n in jk['notes']]})")
        ok(jk["automation"][0]["points"][0]["beat"] == 16.0
           and jk["automation"][0]["points"][1]["beat"] == 24.0,
           f"automation rides the same offset (got {jk['automation'][0]['points']})")
        jb = s["tracks"][2]
        ok(jb.get("sends") == [{"bus": "verb", "gainDb": -12}],
           f"sends filtered to buses the song HAS (got {jb.get('sends')})")
        ok(s["lengthBars"] == 6.0, f"length 4 -> 6 bars (got {s['lengthBars']})")
        ok({"name": "jam", "startBar": 4.0} in s["sections"]
           or {"name": "jam", "startBar": 4} in s["sections"],
           f"section marks the jam (got {s['sections']})")
        ok("124" in out and "126" in out and "NOTE" in out,
           "bpm delta called out in the reply")
        rcs = [r for r in surgical.read_receipts("_kj_tgt") if r["tool"] == "keep_jam"]
        ok(len(rcs) == 1 and sorted(rcs[0]["track_wild"]) == ["jam:bass", "jam:kick"],
           f"RECEIPT LAW: keep_jam filed its receipt ({rcs})")

        # collisions suffix + at_bar override
        out2 = D.TOOLS["keep_jam"][0]({"song": "_kj_tgt", "take": "_kj_take", "at_bar": 0})
        s2 = load("_kj_tgt")
        names2 = [t["name"] for t in s2["tracks"]]
        ok("jam:kick_2" in names2 and "jam:bass_2" in names2,
           f"collision law suffixes (got {names2})")
        ov = next(t for t in s2["tracks"] if t["name"] == "jam:kick_2")
        ok(ov["notes"][0]["start"] == 0.0, "at_bar=0 overlays at the top")
        ok(s2["lengthBars"] == 6.0, "overlay never shrinks the song")

        # refusals
        write("_kj_empty", dict(take, tracks=[]))
        ok("no notes to keep" in D.TOOLS["keep_jam"][0]({"song": "_kj_tgt", "take": "_kj_empty"}),
           "empty take refused")
        ok("no such take" in D.TOOLS["keep_jam"][0]({"song": "_kj_tgt", "take": "_kj_missing"}),
           "missing take refused")
        ok("no such song" in D.TOOLS["keep_jam"][0]({"song": "_kj_missing", "take": "_kj_take"}),
           "missing song refused")

        # determinism on fresh copies
        write("_kj_tgt2", tgt)
        write("_kj_tgt3", tgt)
        D.TOOLS["keep_jam"][0]({"song": "_kj_tgt2", "take": "_kj_take"})
        D.TOOLS["keep_jam"][0]({"song": "_kj_tgt3", "take": "_kj_take"})
        ok(json.dumps(load("_kj_tgt2"), sort_keys=True)
           == json.dumps(load("_kj_tgt3"), sort_keys=True), "deterministic")
    finally:
        cleanup("_kj_tgt", "_kj_take", "_kj_empty", "_kj_tgt2", "_kj_tgt3")
        surgical.clear_receipts()


if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"keep-jam battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
