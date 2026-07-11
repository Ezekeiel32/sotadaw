#!/usr/bin/env python3
"""MAKE SINGS E2E (W104/W105) — the zero-token sung take, guarded.

Drives the REAL sidecar.handle() with isolated IPC: a make_track request
carrying vocals:true must land a proposal whose vocal lane points at a
real synthesized wav, with the event stream narrating the voice and the
instrumental surviving any voice failure (fail-open probed by pointing
the bank away).

Requires the Gahata Meiji voicebank (skips gracefully when absent — the
suite stays green on bankless machines; the sing preflight battery covers
the skip line itself).
"""
import glob
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BANK = os.path.join(ROOT, "library", "voices", "gahata_meiji")


def main():
    if not os.path.isdir(BANK):
        print("make-sings e2e: SKIP (voicebank not installed on this machine)")
        return 0
    ipc = tempfile.mkdtemp(prefix="w105_ipc_")
    os.environ["SOTADAW_IPC"] = ipc
    os.environ["SOTADAW_CHRONICLE"] = "0"
    # THE SANDBOX LAW (2026-07-07 lesson, re-learned 2026-07-11): IPC
    # isolation does NOT contain git/telemetry — the accept leg minted a
    # junk commit on its first run. Verdicts flow, files move, nothing
    # reaches history or the taste data.
    os.environ["SOTADAW_SANDBOX"] = "1"
    sys.path.insert(0, os.path.join(ROOT, "agent"))
    import sidecar as sc

    fails = []

    def check(tag, ok):
        print(f"  {'ok' if ok else 'XX'} {tag}")
        if not ok:
            fails.append(tag)

    SONG = "_mse2e"
    scraps = lambda: glob.glob(os.path.join(SONGS, f"*{SONG}*"))

    def scrub(paths):
        # the sing rail mints vocal DIRECTORIES (_prop_<song>_vocals/) beside the
        # wavs — os.remove on one crashed the NEXT run's opening sweep (suite red
        # 2026-07-11) while the final sweep's except swallowed it: rmtree dirs.
        for p in paths:
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError:
                pass
    scrub(scraps())

    def fresh_base():
        json.dump({"bpm": 120, "lengthBars": 8, "key": "A minor", "tracks": [
            {"name": "pad", "source": {"kind": "faust", "id": "pad_motion"},
             "gainDb": -12,
             "notes": [{"start": 0.0, "len": 4.0, "pitch": 57, "vel": 0.5}]}]},
            open(os.path.join(SONGS, SONG + ".json"), "w"))
    fresh_base()
    try:
        # 1) the sung take lands end to end
        sc.handle({"id": 9105, "type": "make_track", "song": SONG,
                   "genre": "pop", "seed": 27, "vocals": True})
        prop = os.path.join(SONGS, f"_prop_{SONG}.json")
        check("proposal landed", os.path.exists(prop))
        vk = False
        if os.path.exists(prop):
            pj = json.load(open(prop))
            vt = next((t for t in pj["tracks"]
                       if str(t.get("name", "")).startswith("vocal")), None)
            clips = (vt or {}).get("audioClips") or []
            vk = bool(clips) and os.path.getsize(
                os.path.join(ROOT, clips[0]["file"])) > 100000
        check("sung lane carries a real wav", vk)
        ev = open(os.path.join(ipc, "events.jsonl")).read()
        check("events narrate the voice",
              "singing" in ev and '"proposal"' in ev)
        check("attribution in the sing rail",
              "Gahata Meiji" in open(os.path.join(ROOT, "tools", "sing.py")).read())

        # 2) THE ASSET ADOPTION (W106): accept must move the sung wav to a
        # stable name — the next take's sing would overwrite _prop_*_vocal
        pj1 = json.load(open(prop))
        sc.handle({"id": 9107, "type": "accept", "song": SONG})
        base = json.load(open(os.path.join(SONGS, SONG + ".json")))
        vt_b = next((t for t in base["tracks"]
                     if str(t.get("name", "")).startswith("vocal")), None)
        clips_b = (vt_b or {}).get("audioClips") or []
        adopted = (bool(clips_b)
                   and "_prop_" not in os.path.basename(clips_b[0]["file"])
                   and os.path.exists(os.path.join(ROOT, clips_b[0]["file"])))
        check("accept adopts the sung wav to a stable name", adopted)
        check("the _prop_ wav is gone (nothing to overwrite)",
              not os.path.exists(os.path.join(
                  SONGS, f"_prop_{SONG}_vocal.wav")))

        # 3) FAIL-OPEN: voice trouble lands the instrumental unchanged.
        # PRISTINE BASE: phase 2's accept adopted a SUNG lane into the base song,
        # and the sing rail deliberately never clobbers an existing vocal (the
        # imported-record law) — without a reset, phase 2's vocal rides phase 3's
        # prop and fakes a fail-open red (surfaced 2026-07-11 once the dir-crash
        # stopped masking this phase).
        scrub(p for p in scraps() if "_prop_" in p or "_vocal" in p)
        fresh_base()
        os.environ["SOTADAW_SING_MINGB"] = "99999"   # preflight refuses -> rc!=0
        sc.handle({"id": 9106, "type": "make_track", "song": SONG,
                   "genre": "pop", "seed": 27, "vocals": True})
        os.environ.pop("SOTADAW_SING_MINGB", None)
        ok2 = os.path.exists(prop)
        pj2 = json.load(open(prop)) if ok2 else {"tracks": []}
        no_voice = not any(str(t.get("name", "")).startswith("vocal")
                           and (t.get("audioClips") or [])
                           for t in pj2["tracks"])
        ev2 = open(os.path.join(ipc, "events.jsonl")).read()
        check("fail-open: instrumental still lands", ok2 and no_voice)
        check("fail-open: skip is narrated", "voice skipped" in ev2)
    finally:
        scrub(scraps())
        shutil.rmtree(ipc, ignore_errors=True)
    print(f"make-sings e2e: {'clean' if not fails else 'RED ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
