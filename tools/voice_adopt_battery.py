#!/usr/bin/env python3
"""VOICE-ADOPT battery — THE VOICE SURVIVES THE VERDICT (2026-07-11).

Born from untitled_38: "NOW MAKE IT 2.20 LONG AND WIRTH REAL VOCALS AND
LYRICS" — the revise removed the stale hum lane, the stop landed 3s before
the re-sing, and the accept committed a voiceless take carrying 20 lyric
words. Nothing said so, and the FOLLOWING VOICE binding dir stayed
prop-scoped (dead rail + immortal orphans).

Proves the two helpers on isolated temp trees (no daemon, no repo writes):
  vocal_gap(doc)                 lyrics staged + no sounding vocal lane -> flag
  adopt_voice_bindings(...)      live bindings migrate to <song>_vocals/
                                 (paths + recorded argv re-homed, melody cache
                                 moved, dest merge dedupes by out_wav); dead
                                 bindings swept with their unreferenced wavs;
                                 referenced prop-named wavs NEVER swept.

Usage: python3 tools/voice_adopt_battery.py
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="va_battery_ipc_")
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as sc

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


LY = [{"beat": float(i), "text": "la"} for i in range(4)]


def gap_checks():
    g = sc.vocal_gap
    ok(g({"lyrics": LY, "tracks": [{"name": "kick", "notes": [{}]}]}),
       "lyrics + no vocal lane -> flags")
    ok(g({"lyrics": LY, "tracks": [
        {"name": "vocals", "audioClips": [{"file": "songs/x_vocal.wav"}]}]}) is None,
       "vocal-named clip on an unmuted lane -> whole")
    ok(g({"tracks": [{"name": "kick"}]}) is None, "no lyrics -> None")
    ok(g({"lyrics": [], "tracks": []}) is None, "empty lyrics list -> None")
    ok(g({"lyrics": LY, "tracks": [
        {"name": "vocals_sketch", "muted": True, "notes": [{}]}]}),
       "ONLY a muted sketch lane -> still flags (muted is not sounding)")
    ok(g({"lyrics": LY, "tracks": [{"name": "vocals", "notes": [{}]}]}) is None,
       "unmuted vocals MIDI lane (proxy voice) -> whole")
    ok(g({"lyrics": LY, "tracks": [
        {"name": "lead", "audioClips": [{"file": "songs/x_vocal.wav"}]}]}) is None,
       "vocal wav riding a non-vocal-named track still counts")
    flag = g({"lyrics": LY, "tracks": []})
    ok(flag and "4 lyric word" in flag, "flag names the word count")


def fresh_tree():
    tmp = tempfile.mkdtemp(prefix="va_battery_root_")
    os.makedirs(os.path.join(tmp, "songs"))
    sc.ROOT, sc.SONGS = tmp, os.path.join(tmp, "songs")
    return tmp


def adopt_checks():
    song, prop_tok = "mysong", "_prop_mysong"

    # -- live binding: wav adopted by the clip walk, binding must follow
    tmp = fresh_tree()
    try:
        pv = os.path.join(sc.SONGS, f"{prop_tok}_vocals")
        os.makedirs(pv)
        new_wav = f"songs/{song}_vocal.wav"
        open(os.path.join(tmp, new_wav), "wb").write(b"RIFFwav")
        json.dump({"bindings": [{
            "out_wav": f"songs/{prop_tok}_vocal.wav",
            "src_audio": f"songs/{prop_tok}_vocal.wav",
            "src_track": "lead", "backend": "sing", "melody": [[0.0, 60, 1.0]],
            "argv": ["py", "sing.py", "hum", prop_tok, "lead", "laa"]}]},
            open(os.path.join(pv, "follow.json"), "w"))
        json.dump({"notes": [[0.0, 60, 1.0]]},
                  open(os.path.join(pv, "melody.json"), "w"))
        bj = {"tracks": [{"name": "vocals", "audioClips": [{"file": new_wav}]}]}
        amap = {f"songs/{prop_tok}_vocal.wav": new_wav}
        mig, swept = sc.adopt_voice_bindings(song, bj, amap)
        ok(mig == 1 and swept == 0, f"live binding migrates (got {mig},{swept})")
        sv = os.path.join(sc.SONGS, f"{song}_vocals")
        try:
            b = json.load(open(os.path.join(sv, "follow.json")))["bindings"][0]
        except Exception:
            b = {}
        ok(b.get("out_wav") == new_wav, "out_wav re-homed to the adopted name")
        ok(b.get("src_audio") == new_wav, "src_audio re-homed")
        ok(prop_tok not in " ".join(b.get("argv", ["x"])),
           "recorded argv re-homed (re-sing hits the ACCEPTED song)")
        ok(os.path.exists(os.path.join(sv, "melody.json")),
           "melody cache migrated")
        ok(not os.path.isdir(pv), "prop-scoped _vocals dir gone")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -- dest merge: same out_wav replaced (new wins), other binding kept
    tmp = fresh_tree()
    try:
        pv = os.path.join(sc.SONGS, f"{prop_tok}_vocals")
        sv = os.path.join(sc.SONGS, f"{song}_vocals")
        os.makedirs(pv)
        os.makedirs(sv)
        new_wav = f"songs/{song}_vocal.wav"
        open(os.path.join(tmp, new_wav), "wb").write(b"RIFFwav")
        json.dump({"bindings": [
            {"out_wav": new_wav, "src_track": "STALE", "backend": "sing"},
            {"out_wav": "songs/other.wav", "src_track": "adlib", "backend": "sing"}]},
            open(os.path.join(sv, "follow.json"), "w"))
        json.dump({"bindings": [{
            "out_wav": f"songs/{prop_tok}_vocal.wav", "src_track": "lead",
            "backend": "sing"}]}, open(os.path.join(pv, "follow.json"), "w"))
        bj = {"tracks": [{"name": "vocals", "audioClips": [{"file": new_wav}]}]}
        mig, _ = sc.adopt_voice_bindings(
            song, bj, {f"songs/{prop_tok}_vocal.wav": new_wav})
        bl = json.load(open(os.path.join(sv, "follow.json")))["bindings"]
        by_out = {b.get("out_wav"): b for b in bl}
        ok(mig == 1 and len(bl) == 2, f"merge keeps 2 bindings (got {len(bl)})")
        ok(by_out.get(new_wav, {}).get("src_track") == "lead",
           "same-out_wav binding: the NEW one wins")
        ok("songs/other.wav" in by_out, "unrelated dest binding survives")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -- dead binding (untitled_38's exact shape): lane removed mid-swap
    tmp = fresh_tree()
    try:
        pv = os.path.join(sc.SONGS, f"{prop_tok}_vocals")
        os.makedirs(pv)
        dead = os.path.join(sc.SONGS, f"{prop_tok}_vocal.wav")
        open(dead, "wb").write(b"RIFFwav")
        json.dump({"bindings": [{
            "out_wav": f"songs/{prop_tok}_vocal.wav", "src_track": "lead",
            "backend": "sing", "argv": ["py", "sing.py", "hum", prop_tok, "lead", "laa"]}]},
            open(os.path.join(pv, "follow.json"), "w"))
        bj = {"tracks": [{"name": "kick", "notes": [{}]}]}   # no vocal refs
        mig, swept = sc.adopt_voice_bindings(song, bj, {})
        ok(mig == 0 and swept == 1,
           f"dead binding: nothing migrates, wav swept (got {mig},{swept})")
        ok(not os.path.isdir(pv), "dead binding dir gone")
        ok(not os.path.exists(dead), "orphan prop wav deleted")
        ok(not os.path.isdir(os.path.join(sc.SONGS, f"{song}_vocals")),
           "no empty stable _vocals dir minted for a dead binding")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -- a REFERENCED prop-named wav (failed clip adopt) is never swept
    tmp = fresh_tree()
    try:
        w = os.path.join(sc.SONGS, f"{prop_tok}_vocal.wav")
        open(w, "wb").write(b"RIFFwav")
        bj = {"tracks": [{"name": "vocals",
                          "audioClips": [{"file": f"songs/{prop_tok}_vocal.wav"}]}]}
        mig, swept = sc.adopt_voice_bindings(song, bj, {})
        ok(swept == 0 and os.path.exists(w),
           "referenced prop-named wav survives the sweep")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -- nothing on disk = clean no-op
    tmp = fresh_tree()
    try:
        ok(sc.adopt_voice_bindings(song, {"tracks": []}, {}) == (0, 0),
           "no dir + no wavs -> (0, 0)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    gap_checks()
    adopt_checks()
    total = PASS + len(FAIL)
    print(f"\nVOICE-ADOPT BATTERY: {PASS}/{total} " +
          ("ALL GREEN" if not FAIL else "RED"))
    for m in FAIL:
        print(f"  FAIL {m}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
