#!/usr/bin/env python3
"""THE CHAT IS A DAW — E2E: transcript cards stream/curate/freeze through the REAL app.

Rides the ghost-journey rig (tools/ghost_e2e.py owns fixtures + staged events)
with one extra rail armed: SOTADAW_SNAP_AGENTMODE=1 — the in-app rig flips
AGENT MODE (chat-first) ON mid-stream (stage 2) and back OFF before the roll
shot (stage 4). The app prints flow* fields on its [ghost-e2e] dump lines;
this driver asserts the whole card lifecycle:

  s1  bass streams        -> ONE live MidiCard rides the transcript (+6 notes)
  s2  lead layer born     -> a second card; AGENT MODE ON (canvas veiled)
  s3  pads + lead grows   -> third card; the LEAD CARD GREW IN PLACE (8 -> 12)
  s4  proposal pending    -> cards stay live; the ROLL hunk-drop MIRRORS into
                             the bass card (bidirectional curation law)
  s6  ghost-roll hunk     -> the second drop mirrors too
  s5  accept              -> every card FREEZES with the verdict (owned snapshot)

Usage: tools/chat_flow_e2e.py [runs]     (default 3)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ghost_e2e as G  # fixtures / parse / cleanup / BIN are the one truth


def run_once(gap=None):
    G.write_fixtures()
    ipc = tempfile.mkdtemp(prefix="chat_flow_ipc_")
    out = tempfile.mkdtemp(prefix="chat_flow_png_")
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_GHOST="1", SOTADAW_SNAP_AGENTMODE="1",
               SOTADAW_SNAP_STAGE_MS=gap or ("600" if G._busy() else "250"),
               SOTADAW_SONG=G.NAME, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([G.BIN, "--snapshot", out], env=env, cwd=G.ROOT,
                           capture_output=True, text=True, timeout=240)
        stages = [G.parse(l) for l in p.stdout.splitlines()
                  if l.startswith("[ghost-e2e]")]
        pngs = sorted(f for f in os.listdir(out) if f.endswith(".png"))
        return check(stages, pngs, p.returncode), p.stdout
    finally:
        G.cleanup()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def check(stages, pngs, rc):
    A = []
    ok = lambda c, m: A.append((bool(c), m))
    s = {int(d["stage"]): d for d in stages}
    ok(set(s) == {1, 2, 3, 4, 5, 6}, f"all stages reported ({sorted(s)})")
    if set(s) != {1, 2, 3, 4, 5, 6}:
        return A
    d = s[1]
    ok(d.get("flowCards") == "1" and d.get("flowLive") == "1",
       f"s1 ONE live card rides the transcript ({d.get('flowCards')}/{d.get('flowLive')})")
    ok(d.get("flowAdds") == "6", f"s1 the card carries the +6 stream ({d.get('flowAdds')})")
    ok(d.get("flowNames") == "bass", f"s1 it is the bass card ({d.get('flowNames')})")
    ok(d.get("agentMode") == "0", "s1 still sidebar mode")
    d = s[2]
    ok(d.get("agentMode") == "1", "s2 AGENT MODE ON mid-stream (chat-first)")
    ok(d.get("flowCards") == "2" and d.get("flowNames") == "bass|lead",
       f"s2 the NEW LAYER lands as a second card ({d.get('flowNames')})")
    ok(d.get("flowAdds") == "14", f"s2 6+8 streamed notes across cards ({d.get('flowAdds')})")
    d = s[3]
    ok(d.get("flowCards") == "3" and d.get("flowNames") == "bass|lead|pads",
       f"s3 three cards in creation order ({d.get('flowNames')})")
    ok(d.get("flowAdds") == "22", f"s3 the lead card GREW IN PLACE 8->12 (6+12+4 = {d.get('flowAdds')})")
    ok(d.get("agentMode") == "1", "s3 agent mode holds while streaming")
    d = s[4]
    ok(d.get("agentMode") == "0", "s4 rig exits agent mode for the roll shot")
    ok(d.get("flowLive") == "3" and d.get("flowFrozen") == "0",
       f"s4 cards live at pending ({d.get('flowLive')}/{d.get('flowFrozen')})")
    ok(d.get("flowDrops") == "1",
       f"s4 the ROLL hunk-drop MIRRORS into the card ({d.get('flowDrops')})")
    d = s[6]
    ok(d.get("flowDrops") == "2", f"s6 the ghost-roll drop mirrors too ({d.get('flowDrops')})")
    d = s[5]
    ok(d.get("flowLive") == "0" and d.get("flowFrozen") == "3",
       f"s5 ACCEPT freezes every card ({d.get('flowLive')}/{d.get('flowFrozen')})")
    ok(d.get("flowAdds") == "22", f"s5 frozen cards keep their story ({d.get('flowAdds')})")
    ok(len([f for f in pngs if f.startswith("ghost_stage")]) == 6,
       f"6 stage PNGs shot ({len(pngs)})")
    ok(rc == 0, f"app exit 0 (got {rc})")
    return A


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = 0
    for i in range(1, runs + 1):
        res, raw = run_once()
        fails = [m for okk, m in res if not okk]
        if fails:
            # announced retry-once at a wide gap (ghost_e2e discipline: flakes
            # stay visible, real regressions fail identically at any gap)
            print(f"== run {i}/{runs}: red (busy={G._busy()}) — one announced retry at 1200ms")
            res, raw = run_once(gap="1200")
            fails = [m for okk, m in res if not okk]
        if fails:
            bad += 1
            print(f"== run {i}/{runs}: FAIL ({len(res) - len(fails)}/{len(res)})")
            for okk, m in res:
                print(f"   {'ok ' if okk else 'FAIL'} {m}")
            print("---- raw [ghost-e2e] lines ----")
            for l in raw.splitlines():
                if l.startswith("[ghost-e2e]"):
                    print("  " + l)
        else:
            print(f"== run {i}/{runs}: PASS ({len(res)}/{len(res)} checks)")
    print(f"\n{'ALL GREEN' if bad == 0 else str(bad) + ' RUN(S) FAILED'} over {runs} runs")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
