#!/usr/bin/env python3
"""THE LIVING CARD E2E — in-chat MidiCards show the TRACK, not just the take.

The indictment (Chezy, 2026-07-10 screenshot): an fx-only take on an imported
song raised six track cards in the chat with EMPTY bodies — compactC hid the
mini roll whenever the take added no notes, even on lanes carrying a full MIDI
sketch. The law after the fix: a card collapses to a chip strip ONLY when there
is nothing to draw at all (take empty AND track empty); any lane with notes
shows them, framed.

Boots the REAL binary in --snapshot mode with the staged ghost journey
(SOTADAW_SNAP_GHOST=1) + SOTADAW_SNAP_CARDS=1: the rig prints one
machine-checkable [cards] census line per stage:
  [cards] stage=N n=<count> card0=<name>:<compact>:<added>:<trackNotes> ...
(cards sorted by name — std::map order — so indices are deterministic).

Fixtures (this battery's own; ghost_e2e's are untouched — never loosen a battery):
  base   kick(4 notes, -4dB)  bass(2 notes)  atmos(0 notes, -10dB)  + a bus
  s1     kick GAIN-ONLY -> -2 (fx-only on a MIDI lane: THE FIX CASE)
         bass +6 notes        (the streaming case)
         atmos GAIN-ONLY -> -6 (fx-only on an EMPTY lane: compact is CORRECT)
  s2     + lead (8 notes)     (proposal-added layer card)
  s3     lead grows to 12, + pads(4), 8 bars
  s4     pending   s5 accept -> flowCards freeze + clear (census n=0)

Usage: tools/cards_e2e.py [runs]   (default 3)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_cards_e2e"

N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}
TRK = lambda nm, vid, notes, g=-4: {"name": nm, "source": {"kind": "faust", "id": vid},
                                    "gainDb": g, "pan": 0, "notes": notes}


def fixtures():
    kick4 = TRK("kick", "hardkick", [N(b, 0.22, 36, 1) for b in range(4)], -4)
    bass2 = TRK("bass", "bass_warm", [N(0, 0.5, 33, 0.9), N(2, 0.5, 33, 0.9)], -6)
    atmos0 = TRK("atmos", "warmpad", [], -10)
    base = {"version": 1, "bpm": 120, "lengthBars": 4, "masterGainDb": 0.0, "master": [],
            "tracks": [kick4, bass2, atmos0],
            "buses": [{"id": "verb", "gainDb": 0, "fx": [{"id": "fx_reverb"}]}]}

    kick_g = json.loads(json.dumps(kick4)); kick_g["gainDb"] = -2      # fx-only + notes
    atmos_g = json.loads(json.dumps(atmos0)); atmos_g["gainDb"] = -6   # fx-only, EMPTY
    bass8 = json.loads(json.dumps(bass2))
    bass8["notes"] += [N(s, 0.4, 33 + (3 if i % 3 == 2 else 0), 0.85)
                       for i, s in enumerate((0.5, 1.0, 1.5, 2.5, 3.0, 3.5))]
    lead8 = TRK("lead", "flute_lead", [N(b, 0.7, 60 + [0, 3, 7, 10][b % 4], 0.8)
                                       for b in range(8)], -8)
    lead12 = TRK("lead", "flute_lead", [N(b * 0.75, 0.6, 60 + [0, 3, 7, 10, 12, 7][b % 6], 0.8)
                                        for b in range(12)], -8)
    pads4 = TRK("pads", "harp", [N(b * 4, 3.5, 48 + [0, 5, 3, 7][b], 0.6) for b in range(4)], -10)

    s1 = json.loads(json.dumps(base)); s1["tracks"] = [kick_g, bass8, atmos_g]
    s2 = json.loads(json.dumps(s1));   s2["tracks"] = s1["tracks"] + [lead8]
    s3 = json.loads(json.dumps(s1))
    s3["tracks"] = s1["tracks"] + [lead12, pads4]
    s3["lengthBars"] = 8
    return base, s1, s2, s3


def write_fixtures():
    base, s1, s2, s3 = fixtures()
    for tag, doc in [("", base), (".s1", s1), (".s2", s2), (".s3", s3)]:
        with open(os.path.join(SONGS, f"{NAME}{tag}.json"), "w") as f:
            json.dump(doc, f, indent=1)


def cleanup():
    for p in [f"{NAME}.json", f"{NAME}.s1.json", f"{NAME}.s2.json", f"{NAME}.s3.json",
              f"_prop_{NAME}.json", f"_prop_{NAME}.ghost.json", f"_prop_{NAME}.wav"]:
        fp = os.path.join(SONGS, p)
        if os.path.exists(fp):
            os.remove(fp)


def parse(line):
    d = dict(re.findall(r"(\w+)=(\S+)", line))
    cards = {}
    for k, v in list(d.items()):
        if re.match(r"card\d+$", k):
            nm, compact, added, tn = v.rsplit(":", 3)
            cards[nm] = {"compact": int(compact), "added": int(added), "tn": int(tn)}
            del d[k]
    d["cards"] = cards
    return d


def check(stages):
    A = []

    def ok(cond, msg):
        A.append((bool(cond), msg))

    s = {int(d["stage"]): d for d in stages}
    ok({1, 2, 3, 4, 5}.issubset(set(s)), f"census stages reported ({sorted(s)})")
    if not {1, 2, 3, 4, 5}.issubset(set(s)):
        return A
    c1 = s[1]["cards"]
    # THE FIX LAW: fx-only take on a MIDI lane SHOWS the roll (the empty-body kill)
    ok(c1.get("kick", {}).get("compact") == 0 and c1["kick"]["added"] == 0
       and c1["kick"]["tn"] == 4,
       f"s1 kick fx-only card SHOWS its 4 track notes (got {c1.get('kick')})")
    # the counter-law: nothing to draw at all -> compact chip strip stays correct
    ok(c1.get("atmos", {}).get("compact") == 1 and c1["atmos"]["tn"] == 0,
       f"s1 atmos fx-only-on-EMPTY stays compact (got {c1.get('atmos')})")
    # the streaming case rides unchanged
    ok(c1.get("bass", {}).get("compact") == 0 and c1["bass"]["added"] == 6
       and c1["bass"]["tn"] == 8,
       f"s1 bass +6 streams on the roll (got {c1.get('bass')})")
    ok(int(s[1]["n"]) == 3, f"s1 exactly 3 cards (got {s[1]['n']})")
    # added layers get cards too, rolls on
    c3 = s[3]["cards"]
    ok(c3.get("lead", {}).get("compact") == 0 and c3["lead"]["added"] == 12,
       f"s3 lead layer card rolls +12 (got {c3.get('lead')})")
    ok(c3.get("pads", {}).get("compact") == 0 and c3["pads"]["added"] == 4,
       f"s3 pads layer card rolls +4 (got {c3.get('pads')})")
    # pending keeps every card alive with the same truth
    c4 = s[4]["cards"]
    ok(c4.get("kick", {}).get("compact") == 0 and int(s[4]["n"]) == 5,
       f"s4 pending: 5 cards, kick roll still up (got n={s[4]['n']} {c4.get('kick')})")
    # the verdict freezes the flow: live census empties (frozen cards persist in transcript)
    ok(int(s[5]["n"]) == 0, f"s5 accept freezes+clears the live flow (got n={s[5]['n']})")
    return A


def _busy():
    try:
        cc = int(subprocess.run(["pgrep", "-c", "cc1plus"], capture_output=True,
                                text=True).stdout.strip() or 0)
        m1 = int(subprocess.run(["pgrep", "-fc", "m1 render"], capture_output=True,
                                text=True).stdout.strip() or 0)
        return cc > 0 or m1 > 0
    except Exception:
        return False


def run_once(stage_ms=None):
    write_fixtures()
    ipc = tempfile.mkdtemp(prefix="cards_e2e_ipc_")
    out = tempfile.mkdtemp(prefix="cards_e2e_png_")
    gap = stage_ms or ("600" if _busy() else "200")
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1", SOTADAW_SNAP_GHOST="1",
               SOTADAW_SNAP_CARDS="1", SOTADAW_SNAP_STAGE_MS=gap,
               SOTADAW_SONG=NAME, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        stages = [parse(l) for l in p.stdout.splitlines() if l.startswith("[cards]")]
        results = check(stages)
        if p.returncode != 0:
            results.append((False, f"app exit {p.returncode}: {p.stdout[-300:]} {p.stderr[-300:]}"))
        return results, p.stdout
    finally:
        cleanup()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    total_fail = 0
    for i in range(1, runs + 1):
        results, raw = run_once()
        fails = [m for okk, m in results if not okk]
        if fails:   # announced retry at a wide gap — deterministic rig, timing flakes only
            print(f"== run {i}/{runs}: red (busy={_busy()}) — one announced retry at 1200ms")
            results, raw = run_once(stage_ms="1200")
            fails = [m for okk, m in results if not okk]
        if fails:
            total_fail += 1
            print(f"== run {i}/{runs}: FAIL ({len(results) - len(fails)}/{len(results)})")
            for okk, m in results:
                print(f"   {'ok ' if okk else 'FAIL'} {m}")
            for l in raw.splitlines():
                if l.startswith("[cards]"):
                    print("  " + l)
        else:
            print(f"== run {i}/{runs}: PASS ({len(results)}/{len(results)} checks)")
    print(f"\n{'ALL GREEN' if total_fail == 0 else str(total_fail) + ' RUN(S) FAILED'} over {runs} runs")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
