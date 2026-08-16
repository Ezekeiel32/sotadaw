#!/usr/bin/env python3
"""THE ARTIST MODEL battery (A2, docs/SPEC_TRANSCENDENCE.md).

Pure, isolated (tempdir fixture root — never touches the live tree).
Proves: evidence thresholds (honest miss), verbatim WHY laws, fact laws,
user-line sacredness across re-distills, id hard-overwrite, block budget +
genre scoping + empty-omission, court word-boundary law, md round-trip.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import artist_model as am

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def build_root():
    root = tempfile.mkdtemp(prefix="artist_bat_")
    os.makedirs(os.path.join(root, "telemetry"))
    os.makedirs(os.path.join(root, "songs", ".memory"))
    os.makedirs(os.path.join(root, "songs", ".chat"))
    rows = []
    # 4 accepted 3step takes w/ tight LUFS + key habit (law lands)
    for i, (lufs, key) in enumerate([(-9.4, "A minor"), (-9.1, "A minor"),
                                     (-9.8, "A minor"), (-9.3, "C major")]):
        rows.append({"t": 1000 + i, "song": f"s{i}", "accepted": True,
                     "note": "", "genre": "3step",
                     "metrics": str({"lufs_integrated": lufs,
                                     "key_estimate": key,
                                     "peak_dbfs": -2.0})})
    # only 2 accepted pop takes (below n>=3 -> honest miss)
    for i, lufs in enumerate([-11.0, -10.5]):
        rows.append({"t": 2000 + i, "song": f"p{i}", "accepted": True,
                     "note": "", "genre": "pop",
                     "metrics": str({"lufs_integrated": lufs})})
    # repeated bright rejects (law) + one groove reject (recent only)
    rows.append({"t": 3000, "song": "s9", "accepted": False,
                 "note": "way too bright", "genre": "3step", "metrics": "{}"})
    rows.append({"t": 3001, "song": "s9", "accepted": False,
                 "note": "harsh highs again", "genre": "3step",
                 "metrics": "{}"})
    rows.append({"t": 3002, "song": "s8", "accepted": False,
                 "note": "not on beat", "genre": "pop", "metrics": "{}"})
    with open(os.path.join(root, "telemetry", "proposals.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    # chronicle WHY that telemetry lacks (dedupe path exercised by same-t row)
    with open(os.path.join(root, "songs", ".chat", "s7.jsonl"), "w") as f:
        f.write(json.dumps({"t": 4000, "role": "verdict", "verdict": "reject",
                            "text": "too bright violin", "held": 0}) + "\n")
        f.write(json.dumps({"t": 4001, "role": "verdict", "verdict": "accept",
                            "text": "", "held": 0}) + "\n")
    # facts: explicit avoid + vocab (+ a retracted one that must NOT land)
    with open(os.path.join(root, "songs", ".memory", "s0.jsonl"), "w") as f:
        f.write(json.dumps({"t": 1, "entity": "crash cymbals", "rel": "avoid",
                            "value": "", "prov": "user"}) + "\n")
        f.write(json.dumps({"t": 2, "entity": "squelchy", "rel": "refers_to",
                            "value": "the reese track", "prov": "accept"})
                + "\n")
        f.write(json.dumps({"t": 3, "entity": "cowbell", "rel": "avoid",
                            "value": "", "prov": "user"}) + "\n")
        f.write(json.dumps({"t": 4, "entity": "cowbell", "rel": "avoid",
                            "gone": True}) + "\n")
    return root


def main():
    root = build_root()
    try:
        ev = am.mine(root)
        ok(len(ev["verdicts"]) == 10,
           f"mine folds telemetry+chronicle ({len(ev['verdicts'])}=10)")
        ok(len(ev["facts"]) == 2,
           f"facts fold w/ gone-retraction ({len(ev['facts'])}=2)")

        laws, recent = am.distill(ev, now=5000)
        ids = {l["id"]: l for l in laws}
        ok("lufs:3step" in ids, "lufs habit lands at n>=3")
        ok("-9." in ids.get("lufs:3step", {}).get("text", ""),
           "lufs habit carries the measured median")
        ok("lufs:pop" not in ids, "HONEST MISS: n=2 pop mints no lufs law")
        ok("key:3step" in ids and "a minor" in ids["key:3step"]["text"],
           "key habit lands (3/4 a minor)")
        ok("avoid:bright" in ids, "repeated WHY bucket -> avoid law")
        ok("too bright" in ids.get("avoid:bright", {}).get("text", ""),
           "avoid law keeps the user's words verbatim")
        ok("avoid:groove" not in ids, "single WHY mints no law")
        ok(any("not on beat" in r for r in recent),
           "single WHY surfaces as RECENT FEEDBACK")
        ok("never:crash cymbals" in ids, "explicit avoid fact -> law")
        ok("never:cowbell" not in ids, "retracted (gone) fact never lands")
        ok("vocab:squelchy" in ids
           and "reese" in ids["vocab:squelchy"]["text"], "vocab law lands")

        r1 = am.distill_and_write(root, now=5000)
        ok(r1["laws"] >= 5 and os.path.exists(r1["path"]),
           f"constitution written ({r1['laws']} laws)")

        # user lines survive re-distill; user bullet in LAWS promoted
        txt = open(r1["path"]).read()
        txt = txt.replace(
            "## YOUR WORDS (yours, never machine-touched)",
            "## YOUR WORDS (yours, never machine-touched)\n"
            "- hooks must arrive inside 20 seconds")
        txt += "- my own extra law typed at the file tail is ignored\n"
        open(r1["path"], "w").write(txt)
        r2 = am.distill_and_write(root, now=6000)
        body = open(r2["path"]).read()
        ok("hooks must arrive inside 20 seconds" in body,
           "USER LINE SACRED across re-distill")
        machine, user_laws, user_words = am.parse_md(body)
        ok("lufs:3step" in machine and len(machine) == len(
            {l["id"] for l in laws}),
           "machine ids hard-overwrite (no dupes)")
        ok("hooks must arrive inside 20 seconds" in user_words,
           "round-trip parse: user words section")

        # block: user lines first, genre scoping, budget, honest omission
        blk = am.artist_block("3step", root=root)
        ok(blk.startswith("ARTIST CONSTITUTION"), "block header")
        ok("hooks must arrive" in blk, "user words ride the block FIRST")
        ok(blk.index("hooks must arrive") < blk.index("never:")
           if "never:" in blk else True, "user before machine")
        ok("lufs" in blk.lower() and "3step" in blk,
           "genre habit rides for 3step")
        blk_pop = am.artist_block("pop", root=root)
        ok("~-9." not in blk_pop, "3step habit does NOT ride a pop ask")
        tiny = am.artist_block("3step", root=root, budget=200)
        ok(len(tiny) <= 200, f"budget respected ({len(tiny)}<=200)")
        empty_root = tempfile.mkdtemp(prefix="artist_empty_")
        try:
            ok(am.artist_block("3step", root=empty_root) == "",
               "empty constitution -> empty block (omitted, never filler)")
        finally:
            shutil.rmtree(empty_root, ignore_errors=True)

        # court: word-boundary avoid scan, advisory only
        song = {"tracks": [{"name": "crash cymbals", "source": {"id": "x"}},
                           {"name": "loudness_bus", "source": {"id": "y"}}]}
        v = am.court_constitution(song, root=root)
        ok(v.get("ok") is False and "crash cymbals" in v.get("hits", []),
           "court flags an explicit avoid on the take")
        song2 = {"tracks": [{"name": "loudness_bus", "source": {"id": "oudplayer_no"}}]}
        # plant an 'oud' avoid via YOUR WORDS to prove the boundary law
        body2 = open(r2["path"]).read().replace(
            "## YOUR WORDS (yours, never machine-touched)",
            "## YOUR WORDS (yours, never machine-touched)\n- never: oud")
        open(r2["path"], "w").write(body2)
        v2 = am.court_constitution(song2, root=root)
        ok(v2.get("ok") is True,
           "word-boundary law: 'oud' never matches 'loudness'")
        song3 = {"tracks": [{"name": "oud lead", "source": {"id": "z"}}]}
        v3 = am.court_constitution(song3, root=root)
        ok(v3.get("ok") is False and "oud" in v3.get("hits", []),
           "…but a real oud lane is flagged")
        noroot = tempfile.mkdtemp(prefix="artist_nc_")
        try:
            ok(am.court_constitution(song, root=noroot).get("skipped") is True,
               "no laws -> court skips (fail-open)")
        finally:
            shutil.rmtree(noroot, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print(f"\nartist_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
