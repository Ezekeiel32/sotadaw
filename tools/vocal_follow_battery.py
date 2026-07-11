#!/usr/bin/env python3
"""THE FOLLOWING VOICE battery — pure proof that vocal MIDI is the source.

Chezy 2026-07-11: "IT NEEDS TO BE EDITABLE MIDI!" — these checks pin the
law: edits drift the melody sha; follow re-renders ONLY the edited spans
(REGION SURGERY — the whole-take E2E moved unedited notes 114-337 cents,
so the map is law); the first follow rebases onto the pristine stem; the
wav is replaced IN PLACE (song.json never written); a backend failure is
honest. No GPU, no engine — the backend is a stub.
"""
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vocal_follow as vf  # noqa: E402

N = 0
FAILS = []


def check(name, ok, detail=""):
    global N
    N += 1
    print(f"[follow-battery] {N:2}. {name:58} "
          f"{'OK' if ok else 'FAIL ' + str(detail)}")
    if not ok:
        FAILS.append(name)


def main():
    tmp = tempfile.mkdtemp(prefix="vfollow_")
    vf.SONGS = tmp                      # the kernel lives in a sandbox

    notes = [{"start": 0.0, "len": 1.0, "pitch": 60, "vel": 0.8},
             {"start": 4.0, "len": 0.5, "pitch": 64, "vel": 0.7},
             {"start": 8.0, "len": 0.5, "pitch": 67, "vel": 0.9}]

    s0 = vf.melody_sha(notes)
    check("sha: order-invariant",
          vf.melody_sha(list(reversed(notes))) == s0)
    velved = [dict(n, vel=0.1) for n in notes]
    check("sha: velocity edits do NOT drift (not a pitch target)",
          vf.melody_sha(velved) == s0)
    pitched = [dict(notes[0], pitch=61)] + notes[1:]
    check("sha: a pitch edit drifts", vf.melody_sha(pitched) != s0)
    moved = [dict(notes[0], start=0.5)] + notes[1:]
    check("sha: a timing edit drifts", vf.melody_sha(moved) != s0)

    c0 = vf._canon(notes)
    sp1 = vf.edited_spans(c0, vf._canon(pitched))
    check("spans: one pitch edit = one span hugging that note",
          len(sp1) == 1 and abs(sp1[0][0] - 0.0) < 0.16
          and abs(sp1[0][1] - 1.15) < 0.02, sp1)
    two = [dict(notes[0], pitch=61)] + [notes[1]] + [dict(notes[2], pitch=69)]
    sp2 = vf.edited_spans(c0, vf._canon(two))
    check("spans: two distant edits = two spans (middle note untouched)",
          len(sp2) == 2 and sp2[0][1] < 4.0 < sp2[1][0], sp2)
    movedfar = [dict(notes[0], start=6.0)] + notes[1:]
    spm = vf.edited_spans(c0, vf._canon(movedfar))
    check("spans: a moved note covers BOTH its old and new home",
          any(a <= 0.5 <= b for a, b in spm)
          and any(a <= 6.2 <= b for a, b in spm), spm)

    name = "vf_test"
    song = {"bpm": 120, "tracks": [
        {"name": "vocals_true", "source": {"kind": "audio", "id": "vocals_true"},
         "audioClips": [{"file": "x.wav", "startBeat": 0}], "notes": []},
        {"name": "vocals_sketch", "source": {"kind": "sample", "kit": "choir"},
         "muted": True, "notes": [dict(n) for n in notes]}]}
    sp = vf.song_path(name)
    json.dump(song, open(sp, "w"), indent=1)
    out_wav = os.path.join(tmp, "vf_test_vocals_true.wav")
    src_wav = os.path.join(tmp, "stem.wav")
    open(out_wav, "wb").write(b"OLDTAKE")
    open(src_wav, "wb").write(b"STEM")

    b = vf.bind(name, "vocals_sketch", out_wav, src_wav)
    check("bind: stamps the current melody sha", b["melody_sha"] == s0)
    check("bind: stores the melody itself (the surgery map's baseline)",
          b["melody"] == c0)
    check("bind: round-trips through follow.json",
          vf.load_bindings(name)[0]["out_wav"] == out_wav)

    rep = vf.check(name)
    check("check: unedited = clean",
          rep and not rep[0]["stale"] and rep[0]["reason"] == "clean", rep)

    song["tracks"][1]["notes"][0]["pitch"] = 62      # THE USER'S EDIT
    json.dump(song, open(sp, "w"), indent=1)
    rep = vf.check(name)
    check("check: pitch edit = stale (sha drift)",
          rep and rep[0]["stale"] and "drift" in rep[0]["reason"], rep)

    song2 = dict(song, tracks=[song["tracks"][0]])
    orphan = "vf_orphan"
    json.dump(song2, open(vf.song_path(orphan), "w"))
    vf.save_bindings(orphan, [dict(b)])
    rep = vf.check(orphan)
    check("check: missing source track is an honest miss",
          rep and not rep[0]["stale"] and "missing" in rep[0]["reason"], rep)

    calls = []

    def fake_backend(nm, bb, in_wav, tmp_out, region=None, song_json=None):
        guide = None
        if song_json:
            gs = json.load(open(song_json))
            gt = next(t for t in gs["tracks"] if t["name"] == bb["src_track"])
            guide = [(n["start"], n["pitch"]) for n in gt["notes"]]
        calls.append({"in": open(in_wav, "rb").read(), "region": region,
                      "guide": guide})
        open(tmp_out, "wb").write(b"NEWSING")
        return None

    vf.BACKENDS["retune"] = fake_backend
    json_mtime = os.path.getmtime(sp)
    json_bytes = open(sp, "rb").read()
    time.sleep(0.02)
    reps = vf.follow(name)
    check("follow: stale binding re-renders through the backend",
          len(calls) == 1 and reps[0]["result"] == "followed", reps)
    check("follow: REGION SURGERY - only the edited span is rendered",
          calls and calls[0]["region"] is not None
          and calls[0]["region"][0] <= 0.0 and 1.0 < calls[0]["region"][1] < 1.5,
          calls and calls[0]["region"])
    check("follow: THE EDIT IS AUTHORITATIVE - guide holds only changed notes",
          calls and calls[0]["guide"] == [(0.0, 62)], calls and calls[0]["guide"])
    check("follow: first follow REBASES onto the pristine stem",
          calls and calls[0]["in"] == b"STEM")
    check("follow: out wav replaced IN PLACE with the new take",
          open(out_wav, "rb").read() == b"NEWSING")
    check("follow: sha re-stamped to the edited melody",
          vf.load_bindings(name)[0]["melody_sha"]
          == vf.melody_sha(song["tracks"][1]["notes"]))
    check("follow: song.json NEVER written (stomp-proof law)",
          os.path.getmtime(sp) == json_mtime
          and open(sp, "rb").read() == json_bytes)

    calls.clear()
    reps = vf.follow(name)
    check("follow: clean binding is a no-op (backend not called)",
          calls == [] and reps[0]["result"] == "clean", reps)

    song["tracks"][1]["notes"][2]["pitch"] = 69      # a SECOND edit session
    json.dump(song, open(sp, "w"), indent=1)
    reps = vf.follow(name)
    check("follow: later follows chain on the CURRENT take (edits survive)",
          calls and calls[0]["in"] == b"NEWSING"
          and reps[0]["result"] == "followed", calls)

    calls.clear()
    for n in song["tracks"][1]["notes"]:             # MASS EDIT: re-drawn line
        n["pitch"] += 1
    json.dump(song, open(sp, "w"), indent=1)
    reps = vf.follow(name)
    check("follow: a mass edit falls back to a whole-take render",
          calls and calls[0]["region"] is None, calls)

    def dead_backend(nm, bb, in_wav, tmp_out, region=None, song_json=None):
        raise RuntimeError("vocoder exploded")

    vf.BACKENDS["retune"] = dead_backend
    song["tracks"][1]["notes"][0]["pitch"] = 55
    json.dump(song, open(sp, "w"), indent=1)
    reps = vf.follow(name)
    check("follow: backend failure is honest, wav untouched",
          "failed" in str(reps[0]["result"])
          and open(out_wav, "rb").read() == b"NEWSING", reps)
    check("follow: failed binding stays stale (retry next edit-tick)",
          vf.check(name)[0]["stale"])
    check("follow: no work/tmp litter after a failure",
          not [f for f in os.listdir(tmp) if "follow_" in f])

    name2 = "vf_land"
    json.dump({"bpm": 100, "tracks": [
        {"name": "vocals", "source": {"kind": "audio", "id": "vocals"},
         "audioClips": [{"file": "v.wav", "startBeat": 0}], "notes": []}]},
        open(vf.song_path(name2), "w"), indent=1)
    landed = vf.land_sketch(name2, notes)
    s2 = json.load(open(vf.song_path(name2)))
    lane = next((t for t in s2["tracks"] if t["name"] == "vocals_sketch"), None)
    check("land_sketch: lands the muted edit surface after the vocal lane",
          landed and lane is not None and lane["muted"]
          and s2["tracks"][1]["name"] == "vocals_sketch")
    check("land_sketch: melody cached for the watcher's stomp-heal",
          vf.cached_melody(name2) == notes)
    check("land_sketch: idempotent (never clobbers an existing lane)",
          vf.land_sketch(name2, notes) is False
          and sum(1 for t in json.load(open(vf.song_path(name2)))["tracks"]
                  if t["name"] == "vocals_sketch") == 1)

    want = 29
    ok = not FAILS and N == want
    print(f"[follow-battery] {N}/{want} checks, "
          + ("ALL PASS — the MIDI is the source, the voice follows surgically"
             if ok else f"RED: {FAILS}"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
