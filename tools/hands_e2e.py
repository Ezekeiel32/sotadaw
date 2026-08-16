#!/usr/bin/env python3
"""THE HANDS E2E (HB1+HB2) — THRESHOLD + BLOCK + SPINE + ROLL ARSENAL + UNDO, real app.

Boots the actual SOTA DAW binary in --snapshot mode (peerless, never touches the
screen) with SOTADAW_HANDSTEST=<fixture dir>. MainComponent::handsSelfTest then
drives the SAME code paths the mouse and the OS drag-and-drop drive and prints one
machine-checkable [hands] line per check. This script owns fixtures + cleanup.

What it proves (docs/THE_HANDS.md HB1+HB2):
  1-2  wav drop -> new audio track / lane clip, AT the bar
  3    mid drop -> notes merge, arrive SELECTED (instant BLOCK)
  4-6  THE BLOCK move +4 / clone-to-next-lane / delete
  7    every gesture files a hand receipt (origin:"hand", surgical grammar)
  8    ~/.config/sotadaw/keymap.json overlay rebinds a verb (grid.flip -> x)
  9    a lane header drags OUT as a real .mid
  10   roll: H then Q(1.0) lands every start on the grid
  11   roll: THE KNIFE splits, total span preserved
  12   roll: ctrl+B repeats the selection right
  13   roll: mirror twice = identity (involution)
  14   UNDO: a roll op reverts to the EXACT pre-op state (snapshot-before)
  15-20 AUDIO CLIP VERBS: move / trim / fade(+clamp) / gain / knife(share file) / remove
  21-24 SECTION SURGERY: duplicate ("another chorus") copies content + ripples markers;
        delete-time shrinks + ripples back; save/load round-trips the slate
  25-31 HB4+H9: parseNumeric (math/units), palette match + dropdown, inline ask open/close
  32-33 HB5 per-note chance: seeded dice — 1.0 always / 0.0 never / 0.5 ~half, deterministic
  34-36 H23 DIALECTS: cubase pack rebinds, user overlay outranks, fresh restores canonical

Usage: tools/hands_e2e.py [runs]        (default 1; engine boot is the cost)
"""
import json, os, shutil, struct, subprocess, sys, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_hands_e2e"

N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}


def write_song():
    song = {"version": 1, "bpm": 120, "key": "A minor", "lengthBars": 8,
            "masterGainDb": 0.0, "master": [],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                 "gainDb": -4, "pan": 0, "notes": [N(b, 0.22, 36, 1.0) for b in range(4)]},
                {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"},
                 "gainDb": -6, "pan": 0, "notes": [N(0, 0.5, 33, 0.9), N(2, 0.5, 33, 0.9)]},
            ]}
    with open(os.path.join(SONGS, NAME + ".json"), "w") as f:
        json.dump(song, f, indent=1)


def write_wav(path, secs=0.5, hz=440.0, sr=44100):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        n = int(secs * sr)
        frames = bytearray()
        import math
        for i in range(n):
            frames += struct.pack("<h", int(12000 * math.sin(2 * math.pi * hz * i / sr)))
        w.writeframes(bytes(frames))


def write_mid(path, tpq=480):
    """Minimal SMF format-0: three quarter notes at beats 0/1/2 (C4 E4 G4)."""
    ev = []
    for i, pitch in enumerate((60, 64, 67)):
        ev.append((i * tpq, bytes((0x90, pitch, 100))))
        ev.append((i * tpq + tpq, bytes((0x80, pitch, 0))))
    ev.sort(key=lambda e: e[0])
    body = bytearray()
    last = 0
    for t, msg in ev:
        d = t - last
        last = t
        vlq = bytearray([d & 0x7F])          # var-length delta (2 bytes covers tpq range)
        while d > 0x7F:
            d >>= 7
            vlq.insert(0, 0x80 | (d & 0x7F))
        body += vlq + msg
    body += bytes((0x00, 0xFF, 0x2F, 0x00))  # end of track
    trk = b"MTrk" + struct.pack(">I", len(body)) + bytes(body)
    hdr = b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq)
    with open(path, "wb") as f:
        f.write(hdr + trk)


def run_once(i):
    fix = tempfile.mkdtemp(prefix="hands_e2e_")
    home = os.path.join(fix, "home")
    ipc = os.path.join(fix, "ipc")
    snap = os.path.join(fix, "snap")
    os.makedirs(os.path.join(home, ".config", "sotadaw"))
    os.makedirs(ipc)
    os.makedirs(snap)
    with open(os.path.join(home, ".config", "sotadaw", "keymap.json"), "w") as f:
        json.dump({"grid.flip": "x"}, f)     # check 8: the overlay rebinds a verb
    write_song()
    write_wav(os.path.join(fix, "hands.wav"))
    write_mid(os.path.join(fix, "hands.mid"))
    # mp3 fixture for the ANY-FORMAT drop leg (Chezy: mp3 drops must work). The
    # transcode-on-drop is the SUT; skip only where ffmpeg is absent.
    import shutil as _sh
    if _sh.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i",
                        os.path.join(fix, "hands.wav"), "-codec:a", "libmp3lame",
                        "-q:a", "5", os.path.join(fix, "hands.mp3")],
                       capture_output=True)

    env = dict(os.environ)
    env.update({"SOTADAW_HANDSTEST": fix, "SOTADAW_SONG": NAME, "SOTADAW_IPC": ipc,
                "SOTADAW_NO_SIDECAR": "1", "HOME": home})
    try:
        p = subprocess.run([BIN, "--snapshot", snap], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        out = p.stdout
        lines = [l for l in out.splitlines() if l.startswith("[hands]")]
        for l in lines:
            print("  " + l)
        ok = True

        def need(cond, what):
            nonlocal ok
            if not cond:
                ok = False
                print(f"  ASSERT FAIL: {what}")

        # 40 base checks (+3 2026-07-10: palette '/fable' + FABLE MODE toggle/rider/restore)
        # (+2 2026-07-10: THE WORLD GROWS — audio/midi past the end extend the timeline)
        # (+1 2026-07-11: THE VEILED DROP — agent-mode drop mints + the stage answers)
        # (+5 2026-07-11: Codex catalog/filter/rider + retired-model + chat-bar honesty)
        # + 1 optional mp3-drop leg (present iff ffmpeg made the fixture)
        # (+7 2026-07-31 ux-campaign waves ROLL-1/2: alt+wheel vel shadow, Z dive
        #  round-trip, ctrl+L legato, CHASE locate + follow-truce triplet)
        # (+3 wave ROLL-3: P44 props strip — pitch grammar, anchored scrub, typed VEL)
        # (+1 wave ROLL-5: P38 scale fold shrinks the tower)
        # (+3 wave CHAT-1: P71 prompt history up/down/draft)
        # (+2 wave CHAT-2: P65 run dividers fold + reopen)
        import shutil as _sh
        want = 66 if _sh.which("ffmpeg") else 65
        need(any(l.endswith(f"{want}/{want} passed") for l in lines),
             f"{want}/{want} self-checks green")
        verdict = os.path.join(fix, "verdict.json")
        need(os.path.exists(verdict), "verdict.json written")
        if os.path.exists(verdict):
            v = json.load(open(verdict))
            need(v.get("fail") == 0 and v.get("pass") == want, f"verdict clean ({v})")
        rjs = os.path.join(ipc, "receipts.jsonl")
        need(os.path.exists(rjs), "receipts.jsonl exists")
        if os.path.exists(rjs):
            rows = [json.loads(l) for l in open(rjs) if l.strip()]
            hands = [r for r in rows if r.get("origin") == "hand"]
            need(len(hands) >= 6, f"filed {len(hands)} hand receipts (>=6)")
            need(all(r.get("song") == NAME and r.get("tool", "").startswith("hand.")
                     and "fields" in r for r in hands), "receipts speak the surgical grammar")
        # disk round-trip: the section checks end on a saved 1-track / 2-section slate
        # (the drop itself is proven in-app by checks 1-2; here we prove save/load).
        doc = json.load(open(os.path.join(SONGS, NAME + ".json")))
        need(len(doc["tracks"]) == 1, "final slate persisted to song.json (section checks resized)")
        need(abs(doc.get("lengthBars", 0) - 8) < 1e-6, "delete-time restored lengthBars=8 on disk")
        secs = [s.get("name") for s in doc.get("sections", [])]
        need("intro" in secs and "verse" in secs, "sections round-trip through save/load")
        print(f"[hands-e2e] run {i}: {'ALL GREEN' if ok else 'RED'}")
        if not ok and p.stderr:
            print(p.stderr[-1200:])
        return ok
    finally:
        shutil.rmtree(fix, ignore_errors=True)
        try:
            os.remove(os.path.join(SONGS, NAME + ".json"))
        except OSError:
            pass


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if not os.path.exists(BIN):
        print(f"binary missing: {BIN} (build sotadaw first)")
        return 1
    good = sum(run_once(i + 1) for i in range(runs))
    print(f"[hands-e2e] {good}/{runs} runs green")
    return 0 if good == runs else 1


if __name__ == "__main__":
    sys.exit(main())
