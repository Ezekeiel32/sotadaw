#!/usr/bin/env python3
"""GHOST STREAM E2E — the user journey, headless, through the REAL app.

Boots the actual SOTA DAW binary in --snapshot mode (peerless: never touches the
screen) with SOTADAW_SNAP_GHOST=1. The rig inside MainComponent then replays a
staged multi-layer proposal through the REAL events.jsonl -> pollEvents pipeline —
the exact bytes the sidecar feeds — and prints one machine-checkable
[ghost-e2e] line per stage. This script owns fixtures, assertions, cleanup.

The journey it proves (the "streaming only works for one layer, then only appears
after accept" indictment, dead):
  s1  agent adds notes to an EXISTING track      -> ghosts on that lane, bus lane clean
  s2  agent births a NEW layer (lead)            -> a GHOST LANE materializes, streaming
  s3  another layer (pads) + lead grows + longer -> two ghost lanes, ruler opens the bars
  s4  final proposal event                       -> pending; added layers STILL visible
  s5  accept                                     -> ghosts dissolve into real lanes

Usage: tools/ghost_e2e.py [runs]        (default 3 — "test three times e2e")
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_ghost_e2e"

N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}
TRK = lambda nm, vid, notes, g=-4: {"name": nm, "source": {"kind": "faust", "id": vid},
                                    "gainDb": g, "pan": 0, "notes": notes}

def fixtures():
    kick = TRK("kick", "hardkick", [N(b, 0.22, 36, 1) for b in range(4)])
    # a real chain on the kick: the wings' DEVICE tiles (knobs) face the camera
    kick["fx"] = [{"id": "fx_filter", "params": {"cutoff": 800.0, "res": 2.0}},
                  {"id": "fx_reverb", "params": {"mix": 0.25}}]
    base_pair = [N(0, 0.5, 33, 0.9), N(2, 0.5, 33, 0.9)]
    bass2 = TRK("bass", "bass_warm", list(base_pair), -6)
    # s1 = the base pair KEPT byte-identical + 6 new notes -> a pure +6/-0 stream
    bass8 = TRK("bass", "bass_warm", list(base_pair)
                + [N(s, 0.4, 33 + (3 if i % 3 == 2 else 0), 0.85)
                   for i, s in enumerate((0.5, 1.0, 1.5, 2.5, 3.0, 3.5))], -6)
    lead8 = TRK("lead", "flute_lead", [N(b, 0.7, 60 + [0, 3, 7, 10][b % 4], 0.8) for b in range(8)], -8)
    lead12 = TRK("lead", "flute_lead", [N(b * 0.75, 0.6, 60 + [0, 3, 7, 10, 12, 7][b % 6], 0.8)
                                        for b in range(12)], -8)
    pads4 = TRK("pads", "harp", [N(b * 4, 3.5, 48 + [0, 5, 3, 7][b], 0.6) for b in range(4)], -10)
    base = {"version": 1, "bpm": 120, "lengthBars": 4, "masterGainDb": 0.0, "master": [],
            "tracks": [kick, bass2],
            "buses": [{"id": "verb", "gainDb": 0, "fx": [{"id": "fx_reverb"}]}]}
    s1 = json.loads(json.dumps(base)); s1["tracks"] = [kick, bass8]
    s2 = json.loads(json.dumps(s1));   s2["tracks"].append(lead8)
    s3 = json.loads(json.dumps(base)); s3["tracks"] = [kick, bass8, lead12, pads4]; s3["lengthBars"] = 8
    return base, s1, s2, s3

def write_fixtures():
    base, s1, s2, s3 = fixtures()
    for tag, doc in [("", base), (".s1", s1), (".s2", s2), (".s3", s3)]:
        with open(os.path.join(SONGS, f"{NAME}{tag}.json"), "w") as f:
            json.dump(doc, f, indent=1)

def cleanup():
    pats = [f"{NAME}.json", f"{NAME}.s1.json", f"{NAME}.s2.json", f"{NAME}.s3.json",
            f"_prop_{NAME}.json", f"_prop_{NAME}.ghost.json", f"_prop_{NAME}.wav"]
    for p in pats:
        fp = os.path.join(SONGS, p)
        if os.path.exists(fp):
            os.remove(fp)

def parse(line):
    d = dict(re.findall(r"(\w+)=(\S+)", line))
    lanes = {}
    for k, v in list(d.items()):
        m = re.match(r"lane(\d+)", k)
        if m:
            nm, diff, h = v.rsplit(":", 2)   # names may hold ':' (bus:verb)
            lanes[int(m.group(1))] = (nm, diff, int(h.lstrip("h")))
            del d[k]
    d["lanes_detail"] = lanes
    return d

def check(run_idx, stages, pngs):
    A = []
    def ok(cond, msg):
        A.append((bool(cond), msg))
    s = {int(d["stage"]): d for d in stages}
    ok(set(s) == {1, 2, 3, 4, 5, 6}, f"all 6 stages reported ({sorted(s)})")
    if set(s) != {1, 2, 3, 4, 5, 6}:
        return A
    # GHOST ROLL (stage 6): the NEW layer opens read-only; hunks reach it
    d6 = s[6]
    ok(d6.get("rollVis") == "1" and d6.get("rollRO") == "1" and d6.get("rollTrack") == "0",
       f"s6 ghost roll open read-only on the copied layer ({d6.get('rollVis')}/{d6.get('rollRO')})")
    ok(d6.get("rollAdd") == "12" and d6.get("rollDel") == "0",
       f"s6 the lead layer's 12 ghosts ride the ghost roll ({d6.get('rollAdd')})")
    ok(d6.get("hunkDrops") == "2", f"s6 hunks now span BOTH tracks (bass 1 + lead 1 = {d6.get('hunkDrops')})")
    # s1: notes on an existing track stream; NO ghost lane yet; bus lane diff-free
    d = s[1]
    ok(d["ghostLanes"] == "0" and d["lanes"] == "3", f"s1 lanes=3 ghost=0 (got {d['lanes']}/{d['ghostLanes']})")
    ok(d["lanes_detail"][1][1] == "+6/-0", f"s1 bass ghosts +6/-0 (got {d['lanes_detail'][1][1]})")
    ok(d["lanes_detail"][2][1] == "-", f"s1 bus lane diff-free (got {d['lanes_detail'][2][1]})")
    ok(d["streaming"] == "1", "s1 streaming")
    # s2: THE MOMENT THAT WAS BROKEN — a new layer streams as a ghost lane
    d = s[2]
    ok(d["ghostLanes"] == "1" and d["lanes"] == "4", f"s2 GHOST LANE born (lanes {d['lanes']} ghost {d['ghostLanes']})")
    ok(d["lanes_detail"][2][0] == "lead" and d["lanes_detail"][2][1] == "+8/-0",
       f"s2 lead streams +8 on its ghost lane (got {d['lanes_detail'][2]})")
    ok(d["lanes_detail"][3][1] == "-", "s2 bus lane still diff-free (no bleed)")
    # s3: second layer + growth; the ruler opens the new bars
    d = s[3]
    ok(d["ghostLanes"] == "2" and d["lanes"] == "5", f"s3 two ghost lanes (got {d['ghostLanes']}/{d['lanes']})")
    ok(d["lanes_detail"][2][1] == "+12/-0", f"s3 lead grew to +12 (got {d['lanes_detail'][2][1]})")
    ok(d["lanes_detail"][3][0] == "pads" and d["lanes_detail"][3][1] == "+4/-0",
       f"s3 pads ghost lane +4 (got {d['lanes_detail'][3]})")
    ok(d["rulerBeats"] == "32", f"s3 ruler opened to 32 beats (got {d['rulerBeats']})")
    # THE DECK'S EARS: an early render's verdict lands fresh (s2), goes STALE when
    # a newer take streams past it (s3), refreshes with the final render (s4),
    # leaves with the take (s5)
    ok(s[2].get("earsHas") == "1" and s[2].get("earsStale") == "0"
       and s[2].get("earsLufs") == "-12.4",
       f"s2 ears land fresh on the deck ({s[2].get('earsHas')}/{s[2].get('earsStale')}/{s[2].get('earsLufs')})")
    ok(s[3].get("earsStale") == "1", f"s3 ears go stale when the take outruns the render ({s[3].get('earsStale')})")
    ok(s[4].get("earsHas") == "1" and s[4].get("earsStale") == "0"
       and s[4].get("earsLufs") == "-11.9" and s[4].get("earsClip") == "0",
       f"s4 final render verdict fresh at decision time ({s[4].get('earsLufs')} clip {s[4].get('earsClip')})")
    ok(s[5].get("earsHas") == "0", "s5 ears leave with the take")

    # THE ACTION RAILS (agent-first law): every receipt streams in immediately —
    # fx routed LEFT, master routed RIGHT, the user's hand receipts skipped,
    # repeat actions collapse, the verdict freezes the wings. Rails RENDER in
    # agent mode only (railsVis=0 on this sidebar journey; ingestion never stops).
    ok(s[1].get("railFx") == "1" and s[1].get("railMaster") == "1",
       f"s1 receipts routed: fx LEFT=1 master RIGHT=1, hand receipt skipped "
       f"(got {s[1].get('railFx')}/{s[1].get('railMaster')})")

    # THE ACTION STREAM (transcript law): the structured action event paints as a
    # chat card the moment it streams; the bare "agent: tool" pill retires behind it
    ok(int(s[1].get("actionCards", "0")) >= 1,
       f"s1 action event -> transcript action card ({s[1].get('actionCards')})")
    ok(s[1].get("toolPills") == "0",
       f"s1 bare tool pill suppressed by the action card (got {s[1].get('toolPills')})")
    ok(int(s[5].get("actionCards", "0")) >= 1,
       "s5 the action history survives the accept (the thread is the session's story)")
    ok(s[1].get("railsVis") == "0", "s1 rails render in agent mode only (hidden in sidebar)")
    ok(s[2].get("railMaster") == "2",
       f"s2 ears verdict lands on the MASTER rail (got {s[2].get('railMaster')})")
    ok(s[4].get("railMaster") == "2",
       f"s4 repeat ears COLLAPSES into the live card, no spam (got {s[4].get('railMaster')})")
    ok(s[5].get("railFxLive") == "0" and s[5].get("railMasterLive") == "0",
       f"s5 rails frozen by the verdict (live {s[5].get('railFxLive')}/{s[5].get('railMasterLive')})")

    # THE DECK (proposal cards OUT of the chat): alive + composing while streaming,
    # decision hardware materializes at pending, gone after accept
    d = s[1]
    ok(d.get("deck") == "1" and d.get("deckMode") == "1", f"s1 DECK alive in composing mode (got {d.get('deck')}/{d.get('deckMode')})")
    ok(d.get("acceptVis") == "0", "s1 no accept while composing")
    ok(d.get("audVis") == "1", "s1 Listen-live on the deck while composing")
    ok(int(d.get("deckH", "0")) >= 40, f"s1 deck claims its strip (h {d.get('deckH')})")
    # s4: pending — the added layers are VISIBLE BEFORE ACCEPT
    d = s[4]
    ok(d["pending"] == "1", "s4 proposal pending")
    ok(d["ghostLanes"] == "2" and d["lanes"] == "5", f"s4 layers visible while pending (got {d['ghostLanes']}/{d['lanes']})")
    ok(d.get("deckMode") == "2", f"s4 deck in pending mode (got {d.get('deckMode')})")
    ok(d.get("acceptVis") == "1" and d.get("acceptInDeck") == "1",
       f"s4 Accept lives INSIDE the deck (vis {d.get('acceptVis')} in {d.get('acceptInDeck')})")
    ok(d.get("cherryVis") == "1" and int(d.get("deckH", "0")) >= 60,
       f"s4 cherry-pick row rides the deck (vis {d.get('cherryVis')} h {d.get('deckH')})")
    # THE ROLL rides the take (stage 4 opens the roll on the pending bass):
    # ghosts visible in the editor BEFORE accept; gone with the decision
    ok(d.get("rollVis") == "1" and d.get("rollTrack") == "1",
       f"s4 roll open on the take's track (vis {d.get('rollVis')} trk {d.get('rollTrack')})")
    ok(d.get("rollAdd") == "6" and d.get("rollDel") == "0",
       f"s4 roll shows the take's ghosts (+{d.get('rollAdd')}/-{d.get('rollDel')})")
    # COPILOT HUNK LAW: one ghost note dropped on the roll at s4 never lands
    ok(d.get("hunkDrops") == "1" and d.get("rollAdd") == "6",
       f"s4 one hunk held back, six ghosts still shown ({d.get('hunkDrops')}/{d.get('rollAdd')})")
    # s5: accept — ghosts dissolve into real lanes
    d = s[5]
    ok(d["pending"] == "0" and d["streaming"] == "0", "s5 modes cleared")
    ok(d.get("deck") == "0", "s5 deck leaves the stage after accept")
    ok(d.get("rollVis") == "0" and d.get("rollAdd") == "-1",
       "s5 roll closed and ghost-free after the decision")
    ok(d.get("bassNotes") == "7" and d.get("hunkDrops") == "0",
       f"s5 accepted bass = base 2 + take 6 - dropped 1 = 7 (got {d.get('bassNotes')}, drops {d.get('hunkDrops')})")
    ok(d.get("leadNotes") == "11",
       f"s5 accepted NEW layer = take 12 - dropped 1 = 11 (got {d.get('leadNotes')})")
    ok(d.get("reqType") == "accept" and d.get("reqHeldBack") == "2",
       f"s5 the accept request tells the agent WHAT was held back ({d.get('reqHeldBack')} notes)")
    ok(s[4].get("reqId") is not None and d.get("reqId") is not None
       and int(d["reqId"]) == int(s[4].get("reqId", 0)) + 1,
       f"s5 DOUBLE-CLICK eaten: exactly ONE accept request left the app "
       f"(reqId {s[4].get('reqId')} -> {d.get('reqId')})")
    ok(d["baseTracks"] == "4" and d["ghostLanes"] == "0" and d["lanes"] == "5",
       f"s5 accepted: 4 real tracks + bus, no ghosts (got {d['baseTracks']}/{d['ghostLanes']}/{d['lanes']})")
    ok(all(v[1] == "-" for v in d["lanes_detail"].values()), "s5 all lanes diff-free")
    ok(all(v[2] > 0 for st in (1, 2, 3, 4, 5) if s[st].get("rollVis") != "1"
           for v in s[st]["lanes_detail"].values()),
       "every lane laid out with height > 0 whenever the lanes view is up")
    ok(len(pngs) == 6, f"6 stage PNGs shot (got {len(pngs)})")
    return A

def check_reject(stages):
    A = []
    def ok(cond, msg):
        A.append((bool(cond), msg))
    s = {int(d["stage"]): d for d in stages}
    ok(set(s) == {1, 7, 8, 9, 10, 11}, f"reject journey stages reported ({sorted(s)})")
    if set(s) != {1, 7, 8, 9, 10, 11}:
        return A
    d11 = s[11]
    ok(d11.get("deckArmed") == "1" and d11.get("pending") == "1"
       and d11.get("reqId") == s[9].get("reqId"),
       f"r11 the CHAT door ARMS the WHY strip too — no bypass, nothing sent "
       f"(armed={d11.get('deckArmed')}, reqId {s[9].get('reqId')}->{d11.get('reqId')})")
    d10 = s[10]
    ok(d10.get("reqType") == "reject" and d10.get("reqReason") == "1"
       and d10.get("pending") == "0",
       f"r10 ONE preset click says WHY and sends ({d10.get('reqType')}/{d10.get('reqReason')})")
    ok(s[7].get("pending") == "1" and s[7].get("deck") == "1", "r7 take pending on the deck")
    ok(s[8].get("deckArmed") == "1" and s[8].get("pending") == "1",
       f"r8 first Reject ARMS the WHY strip ({s[8].get('deckArmed')})")
    d = s[9]
    ok(d.get("pending") == "0" and d.get("deck") == "0", "r9 second press sends: take gone")
    ok(d.get("deckArmed") == "0", "r9 strip disarmed with the decision")
    ok(d.get("reqType") == "reject" and d.get("reqReason") == "1",
       f"r9 request carries the WHY ({d.get('reqType')}/{d.get('reqReason')})")
    ok(d.get("railFx") == "1" and d.get("railFxLive") == "0",
       f"r9 rails frozen by the reject (cards {d.get('railFx')} live {d.get('railFxLive')})")
    return A

def _busy():
    """Load on the box widens the rig's stage gaps. Watch BOTH pressure sources:
    compilers AND sibling sessions' m1 renders (the 2026-07-07 flake: 3 concurrent
    renders starved the async stage effects while cc1plus was zero)."""
    try:
        import subprocess as _sp
        cc = int(_sp.run(["pgrep", "-c", "cc1plus"], capture_output=True,
                         text=True).stdout.strip() or 0)
        m1 = int(_sp.run(["pgrep", "-fc", "m1 render"], capture_output=True,
                         text=True).stdout.strip() or 0)
        return cc > 0 or m1 > 0
    except Exception:
        return False

def run_once(idx, mode="1", stage_ms=None):
    write_fixtures()
    ipc = tempfile.mkdtemp(prefix="ghost_e2e_ipc_")
    out = tempfile.mkdtemp(prefix="ghost_e2e_png_")
    # load-aware stage gap: cc1plus on the box = async effects need room
    # (face-f5's flake evidence, collab 3m-11b); override via arg
    gap = stage_ms or ("600" if _busy() else "200")
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1", SOTADAW_SNAP_GHOST=mode,
               SOTADAW_SNAP_STAGE_MS=gap,
               SOTADAW_SONG=NAME, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        stages = [parse(l) for l in p.stdout.splitlines() if l.startswith("[ghost-e2e]")]
        pngs = [f for f in os.listdir(out) if f.startswith("ghost_stage")]
        results = check(idx, stages, pngs) if mode != "reject" else check_reject(stages)
        if p.returncode != 0:
            results.append((False, f"app exit code {p.returncode}; tail: {p.stdout[-400:]} {p.stderr[-400:]}"))
        return results, p.stdout
    finally:
        cleanup()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)

def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    total_fail = 0
    for i in range(1, runs + 1):
        for mode, tag in (("1", "accept"), ("reject", "reject")):
            results, raw = run_once(i, mode)
            fails = [m for okk, m in results if not okk]
            if fails:
                # ANNOUNCED retry-once, unconditional: the rig is DETERMINISTIC —
                # a real regression fails identically at any gap; only timing
                # flakes pass on retry (load can vanish while the box still
                # pages, so gating on _busy() missed real flakes).
                print(f"== run {i}/{runs} [{tag}]: red (busy={_busy()}) — "
                      f"one announced retry at 1200ms stage gap")
                results, raw = run_once(i, mode, stage_ms="1200")
                fails = [m for okk, m in results if not okk]
            if fails:
                total_fail += 1
                print(f"== run {i}/{runs} [{tag}]: FAIL ({len(results) - len(fails)}/{len(results)})")
                for okk, m in results:
                    print(f"   {'ok ' if okk else 'FAIL'} {m}")
                print("---- raw [ghost-e2e] lines ----")
                for l in raw.splitlines():
                    if l.startswith("[ghost-e2e]"):
                        print("  " + l)
            else:
                print(f"== run {i}/{runs} [{tag}]: PASS ({len(results)}/{len(results)} checks)")
    print(f"\n{'ALL GREEN' if total_fail == 0 else str(total_fail) + ' RUN(S) FAILED'} over {runs}x2 runs")
    sys.exit(1 if total_fail else 0)

if __name__ == "__main__":
    main()
