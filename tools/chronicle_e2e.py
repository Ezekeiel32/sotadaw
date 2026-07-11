#!/usr/bin/env python3
"""CHRONICLE E2E — per-project conversation memory through the REAL protocol
seam (the ears-on-write law: kernels lie politely, seams tell the truth).

Boots the actual sidecar in --mock mode (zero tokens) on an isolated
SOTADAW_IPC, then drives the exact UI protocol (request.json -> events.jsonl)
through a whole conversation lifecycle and asserts the chronicle at every
stage:

  s1  first ask         -> user + agent rows land; NO conversation block yet
                           (honest miss: the project had no prior chat)
  s2  accept            -> verdict row (accept) rides the file
  s3  second ask        -> the prompt's ctx (ipc/context.json) now carries
                           CONVERSATION MEMORY quoting ask #1 -> ACCEPTED
  s4  reject with WHY   -> verdict row (reject) carries the reason verbatim
  s5  DAEMON RESTART    -> third ask: the block still tells the whole story
                           (accept AND the reject WHY) — disk is the memory
  s6  isolation         -> a second song's chronicle has none of song A's rows

Scratch songs wear the _tmp_* gitignored name so the accept lane's real git
commit machinery no-ops (nothing enters history). Telemetry rows for the
scratch songs are scrubbed at cleanup (the isolation recipe).

Usage: tools/chronicle_e2e.py [runs]   (default 1)
"""
import json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_tmp_chron_e2e"
SONG_B = "_tmp_chron_iso"
FAILS = []


def ok(cond, label):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        FAILS.append(label)


def write_song(name):
    doc = {"version": 1, "bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
           "tracks": [
               {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                "gainDb": -4, "pan": 0,
                "notes": [{"start": float(b), "len": 0.2, "pitch": 36, "vel": 1.0}
                          for b in range(8)]},
               {"name": "hats", "source": {"kind": "faust", "id": "hat_closed"},
                "gainDb": -8, "pan": 0,
                "notes": [{"start": b * 0.5, "len": 0.1, "pitch": 42, "vel": 0.7}
                          for b in range(16)]}]}
    with open(os.path.join(SONGS, f"{name}.json"), "w") as f:
        json.dump(doc, f, indent=1)


class Daemon:
    def __init__(self, ipc):
        self.ipc = ipc
        self.p = None

    def start(self):
        env = dict(os.environ, SOTADAW_IPC=self.ipc, SOTADAW_NO_UPLINK="1",
                   SOTADAW_NO_PREWARM="1")
        self.p = subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
        deadline = time.time() + 20
        ev = os.path.join(self.ipc, "events.jsonl")
        while time.time() < deadline:
            if os.path.exists(ev) and "agent online" in open(ev).read():
                return True
            time.sleep(0.1)
        return False

    def stop(self):
        if self.p is not None:
            self.p.kill()           # exact-pid kill law: never pkill by name
            self.p.wait(timeout=10)
            self.p = None
        try:                        # the lockfile must not orphan across restarts
            os.remove(os.path.join(self.ipc, "sidecar.pid"))
        except OSError:
            pass


_rid = [0]


def ask(ipc, body):
    _rid[0] += 1
    body = dict(body, id=_rid[0])
    tmp = os.path.join(ipc, "request.json.tmp")
    with open(tmp, "w") as f:
        json.dump(body, f)
    os.replace(tmp, os.path.join(ipc, "request.json"))
    deadline = time.time() + 120
    ev = os.path.join(ipc, "events.jsonl")
    while time.time() < deadline:
        for line in open(ev):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("id") == _rid[0] and e.get("kind") == "done":
                return e
        time.sleep(0.15)
    return None


def rows(ipc, song):
    p = os.path.join(ipc, "chat", f"{song}.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p):
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def rendered_ctx(ipc):
    try:
        return json.load(open(os.path.join(ipc, "context.json"))).get("rendered", "")
    except Exception:
        return ""


def scrub_telemetry():
    for name in ("proposals.jsonl", "asks.jsonl"):
        p = os.path.join(ROOT, "telemetry", name)
        if not os.path.exists(p):
            continue
        keep = [l for l in open(p) if SONG not in l and SONG_B not in l]
        with open(p, "w") as f:
            f.writelines(keep)


def cleanup(ipc, d):
    d.stop()
    for n in (SONG, SONG_B):
        for suf in (".json", ".wav"):
            for pre in ("", "_prop_", "_seed_"):
                try:
                    os.remove(os.path.join(SONGS, f"{pre}{n}{suf}"))
                except OSError:
                    pass
        try:
            os.remove(os.path.join(SONGS, f"_prop_{n}.ghost.json"))
        except OSError:
            pass
        shutil.rmtree(os.path.join(SONGS, ".takes", n), ignore_errors=True)
    scrub_telemetry()
    shutil.rmtree(ipc, ignore_errors=True)


def run_once(i):
    print(f"-- run {i} --")
    ipc = tempfile.mkdtemp(prefix="chron_e2e_")
    write_song(SONG)
    write_song(SONG_B)
    d = Daemon(ipc)
    try:
        ok(d.start(), "s0 mock sidecar up on isolated IPC")
        hb = os.path.join(ipc, "alive")
        time.sleep(1.2)   # >= one beat period
        ok(os.path.exists(hb) and time.time() - os.path.getmtime(hb) < 5.0,
           "s0 heartbeat: ipc/alive beats (the OFFLINE-chip ground truth)")

        # s1: first contact — rows land, block honestly missing
        e = ask(ipc, {"type": "prompt", "text": "make the hats quieter", "song": SONG})
        ok(e and e.get("ok"), "s1 first ask completes")
        r = rows(ipc, SONG)
        ok(any(x["role"] == "user" and "hats quieter" in x["text"] for x in r),
           "s1 user ask chronicled")
        ok(any(x["role"] == "agent" for x in r), "s1 agent result chronicled")
        ok("CONVERSATION MEMORY" not in rendered_ctx(ipc),
           "s1 no conversation block on a fresh project (honest miss)")

        # s2: accept -> verdict row
        e = ask(ipc, {"type": "accept", "song": SONG})
        ok(e and e.get("ok"), "s2 accept completes")
        ok(any(x["role"] == "verdict" and x.get("verdict") == "accept"
               for x in rows(ipc, SONG)), "s2 accept verdict chronicled")

        # s3: second ask -> the block rides the prompt context
        e = ask(ipc, {"type": "prompt", "text": "now make it darker", "song": SONG})
        ok(e and e.get("ok"), "s3 second ask completes")
        ctx = rendered_ctx(ipc)
        ok("CONVERSATION MEMORY" in ctx, "s3 conversation block rides the prompt")
        ok("hats quieter" in ctx, "s3 block quotes the first ask")
        ok("-> ACCEPTED" in ctx, "s3 block carries the accept verdict")

        # s4: reject with WHY
        e = ask(ipc, {"type": "reject", "song": SONG, "reason": "too dark, lost the top end"})
        ok(e and e.get("ok"), "s4 reject completes")
        vr = [x for x in rows(ipc, SONG) if x["role"] == "verdict"]
        ok(any(x.get("verdict") == "reject" and "lost the top end" in x.get("text", "")
               for x in vr), "s4 reject WHY chronicled verbatim")

        # s5: DAEMON RESTART — disk is the memory
        d.stop()
        ok(d.start(), "s5 daemon restarted")
        e = ask(ipc, {"type": "prompt", "text": "try a warmer take", "song": SONG})
        ok(e and e.get("ok"), "s5 third ask completes")
        ctx = rendered_ctx(ipc)
        ok("CONVERSATION MEMORY" in ctx and "hats quieter" in ctx,
           "s5 the block survives the restart (disk memory)")
        ok('REJECTED: "too dark, lost the top end"' in ctx,
           "s5 the reject WHY still rides after restart")

        # s6: isolation — song B never saw song A's chat
        e = ask(ipc, {"type": "prompt", "text": "give the kick more punch", "song": SONG_B})
        ok(e and e.get("ok"), "s6 song-B ask completes")
        rb = rows(ipc, SONG_B)
        ok(rb and all("hats quieter" not in x.get("text", "") for x in rb),
           "s6 song B chronicle isolated from song A")
        ok("hats quieter" not in rendered_ctx(ipc),
           "s6 song B prompt context free of song A history")
    finally:
        cleanup(ipc, d)


def run_ui():
    """--ui: the replay path through the REAL binary (SOTADAW_SNAP_CHRONICLE
    rig): boot on a chat-less song, switch to one wearing a prewritten
    songs/.chat history, assert the transcript census card-for-card."""
    BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
    if not os.path.exists(BIN):
        ok(False, "ui: binary missing (build app first)")
        return
    boot, hist = "_tmp_chron_boot", "_tmp_chron_ui"
    write_song(boot)
    write_song(hist)
    chat_dir = os.path.join(SONGS, ".chat")
    os.makedirs(chat_dir, exist_ok=True)
    rows_fixture = [
        {"t": 1000, "role": "user", "text": "make a dark acid drop"},
        {"t": 1010, "role": "note", "text": "the bass is a static A1 pedal"},
        {"t": 1020, "role": "agent", "text": "Built the drop: 303 lead + pedal bass."},
        {"t": 1030, "role": "verdict", "text": "", "verdict": "accept", "held": 0},
        {"t": 1100, "role": "user", "text": "now brighter hats"},
        {"t": 1110, "role": "agent", "text": "Opened the hat filter to 9k."},
        {"t": 1120, "role": "verdict", "text": "too bright", "verdict": "reject"},
        {"t": 1130, "role": "event", "text": "MAKE: a house track landed as a take"},
    ]
    with open(os.path.join(chat_dir, hist + ".jsonl"), "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows_fixture)
    ipc = tempfile.mkdtemp(prefix="chron_ui_ipc_")
    out = tempfile.mkdtemp(prefix="chron_ui_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_CHRONICLE=hist, SOTADAW_SONG=boot, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        st = {}
        for l in p.stdout.splitlines():
            if l.startswith("[chronicle] "):
                d = dict(kv.split("=", 1) for kv in l[12:].split())
                st[d.pop("stage", "?")] = d
        ok(st.get("boot", {}).get("user") == "0",
           f"ui boot: no user cards before the switch ({st.get('boot')})")
        sw = st.get("switch") or {}
        ok(sw.get("song") == hist, f"ui switch landed on {hist} ({sw})")
        ok(sw.get("user") == "2", f"ui replay: 2 user cards ({sw})")
        ok(sw.get("agent") == "3", f"ui replay: 3 agent cards = 2 finals + 1 note ({sw})")
        ok(sw.get("status") == "4", f"ui replay: divider + 2 verdicts + 1 event ({sw})")
        if p.returncode != 0:
            ok(False, f"ui app exit {p.returncode}: {p.stdout[-300:]} {p.stderr[-300:]}")
        png = os.path.join(out, "chronicle_replay.png")
        if os.path.exists(png):   # human evidence: the replayed chat page, in pixels
            shutil.copy(png, os.path.join(ROOT, "eval", "chronicle_replay.png"))
            print("  [....] eval/chronicle_replay.png = the replayed conversation, visible")
    finally:
        for n in (boot, hist):
            for pth in (os.path.join(SONGS, n + ".json"),
                        os.path.join(chat_dir, n + ".jsonl")):
                try:
                    os.remove(pth)
                except OSError:
                    pass
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    if "--ui" in sys.argv:
        run_ui()
    else:
        runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        for i in range(1, runs + 1):
            run_once(i)
    n = len(FAILS)
    print(f"\n== CHRONICLE E2E: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} ==")
    for f in FAILS:
        print("  - " + f)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
