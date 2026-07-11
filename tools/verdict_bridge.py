#!/usr/bin/env python3
"""VERDICT BRIDGE — the serial lane between the VERDICT BOX and the sidecar's IPC.

    box BTN,make          -> request.json {"type":"make_track", song}   (zero-token take)
    box BTN,accept/reject -> request.json {"type":"accept"|"reject", song}  (verdict law:
                             never clobber an unconsumed request.json — queue + retry)
    events.jsonl          -> M,compose / M,pending / V,accept / V,reject   (ghost states)
    ears.jsonl            -> M,hear + E,<phase>,<4 bands>  (~20Hz)         (the light show)

Run:      .venv/bin/python tools/verdict_bridge.py [--port /dev/ttyUSB0] [--genre house]
Prove:    .venv/bin/python tools/verdict_bridge.py --selftest     (no hardware needed)
"""
import argparse, glob, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REJECT_HOLD_REASON = "not feeling this direction - try something different"


def find_port():
    for pat in ("/dev/serial/by-id/*CH340*", "/dev/serial/by-id/*1a86*",
                "/dev/serial/by-id/*", "/dev/ttyUSB*", "/dev/ttyACM*"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    return None


class Tail:
    """Follow an append-mostly jsonl file; survives the ears ring-truncation."""

    def __init__(self, path):
        self.path, self.pos = path, None

    def lines(self):
        try:
            size = os.path.getsize(self.path)
        except OSError:
            return []
        if self.pos is None or self.pos > size:      # first sight / ring-truncated
            self.pos = size if self.pos is None else 0
        if size == self.pos:
            return []
        with open(self.path, "r", errors="replace") as f:
            f.seek(self.pos)
            chunk = f.read()
            self.pos = f.tell()
        out = []
        for ln in chunk.splitlines():
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
        return out


class Bridge:
    def __init__(self, ser, ipc, songs_dir, genre=None, log=print):
        self.ser, self.ipc, self.songs, self.genre = ser, ipc, songs_dir, genre
        self.log = log
        self.events = Tail(os.path.join(ipc, "events.jsonl"))
        self.ears = Tail(os.path.join(ipc, "ears.jsonl"))
        self.req_path = os.path.join(ipc, "request.json")
        self.pending_song = None       # a take awaiting the verdict
        self.last_song = None          # last song any event mentioned
        self.playing = False
        self.queued = None             # verdict held for the single-lane law
        self.last_e = 0.0
        self.buf = b""

    # ---- serial helpers -------------------------------------------------
    def send(self, line):
        self.ser.write((line + "\n").encode())

    def _read_lines(self):
        try:
            n = self.ser.in_waiting
        except Exception:
            n = 0
        if n:
            self.buf += self.ser.read(n)
        out = []
        while b"\n" in self.buf:
            ln, self.buf = self.buf.split(b"\n", 1)
            ln = ln.strip().decode(errors="replace")
            if ln:
                out.append(ln)
        return out

    # ---- IPC writes ------------------------------------------------------
    def _write_request(self, body):
        tmp = self.req_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(body, f)
        os.replace(tmp, self.req_path)
        self.log(f"[bridge] -> request.json {body.get('type')} ({body.get('song')})")

    def _try_verdict(self, body):
        if os.path.exists(self.req_path):            # single lane is busy: queue, retry
            self.queued = body
            self.log("[bridge] request lane busy - verdict queued")
        else:
            self._write_request(body)
            self.queued = None

    def _resolve_song(self):
        if self.pending_song or self.last_song:
            return self.pending_song or self.last_song
        cands = [p for p in glob.glob(os.path.join(self.songs, "*.json"))
                 if not os.path.basename(p).startswith("_")]
        if cands:
            return os.path.splitext(os.path.basename(
                max(cands, key=os.path.getmtime)))[0]
        return None

    def _rid(self):
        return int(time.time() * 1000) % 2_000_000_000

    # ---- input handling ---------------------------------------------------
    def _on_button(self, name):
        if name == "make":
            song = self._resolve_song()
            if not song:
                return self.log("[bridge] MAKE: no song to land on")
            if os.path.exists(self.req_path):
                return self.log("[bridge] MAKE: request lane busy, try again")
            body = {"id": self._rid(), "type": "make_track", "song": song}
            if self.genre:
                body["genre"] = self.genre
            self._write_request(body)
        elif name in ("accept", "reject", "reject_hold"):
            song = self.pending_song
            if not song:
                return self.log(f"[bridge] {name}: no pending take")
            body = {"id": self._rid(),
                    "type": "accept" if name == "accept" else "reject",
                    "song": song}
            if name == "reject_hold":
                body["reason"] = REJECT_HOLD_REASON
            self._try_verdict(body)

    def _on_event(self, e):
        kind, song = e.get("kind"), e.get("song")
        if song:
            self.last_song = song
        if kind == "proposal_progress":
            self.send("M,compose")
        elif kind == "proposal":
            self.pending_song = song
            bpm = (e.get("proposal") or {}).get("bpm")
            if bpm:
                self.send(f"T,{float(bpm):.1f}")
            self.send("M,pending")
        elif kind in ("accepted", "rejected"):
            self.send("V,accept" if kind == "accepted" else "V,reject")
            self.pending_song = None
            self.send("M,hear" if self.playing else "M,idle")
        elif kind == "done" and not self.pending_song:
            self.send("M,hear" if self.playing else "M,idle")

    def _on_ears(self, frames):
        if not frames:
            return
        f = frames[-1]                                  # newest frame wins
        playing = bool(f.get("playing"))
        if playing != self.playing:
            self.playing = playing
            if playing:
                self.send("M,hear")
            else:
                self.send("M,pending" if self.pending_song else "M,idle")
        if not playing or time.time() - self.last_e < 0.05:
            return
        self.last_e = time.time()
        phase = (float(f.get("beat", 0.0)) % 4.0) / 4.0
        bands = f.get("bands_db") or [-60] * 4
        norm = [min(1.0, max(0.0, (float(b) + 45.0) / 40.0)) for b in bands[:4]]
        self.send("E,%.3f,%.2f,%.2f,%.2f,%.2f" % (phase, *norm))

    # ---- one scheduler beat -----------------------------------------------
    def step(self):
        for ln in self._read_lines():
            tok = ln.split(",")
            if tok[0] == "HELLO":
                self.log(f"[bridge] box online: {ln}")
                self.send("M,idle")
            elif tok[0] == "BTN" and len(tok) > 1:
                self.log(f"[bridge] button: {tok[1]}")
                self._on_button(tok[1])
            elif tok[0] == "POT" and len(tok) > 1:
                pass                                    # reserved: the DJ knob lane
        for e in self.events.lines():
            self._on_event(e)
        self._on_ears(self.ears.lines())
        if self.queued and not os.path.exists(self.req_path):
            self._write_request(self.queued)
            self.queued = None


# ---------------------------- selftest rig ---------------------------------
class FakeSerial:
    def __init__(self):
        self.inbox, self.out = b"", []

    def feed(self, line):
        self.inbox += (line + "\n").encode()

    @property
    def in_waiting(self):
        return len(self.inbox)

    def read(self, n):
        data, self.inbox = self.inbox[:n], self.inbox[n:]
        return data

    def write(self, data):
        self.out.append(data.decode().strip())


def selftest():
    import tempfile
    ok = [0, 0]

    def check(cond, msg):
        ok[0 if cond else 1] += 1
        print(("  OK  " if cond else "  FAIL") + " " + msg)

    with tempfile.TemporaryDirectory() as td:
        ipc = os.path.join(td, "ipc"); os.makedirs(ipc)
        songs = os.path.join(td, "songs"); os.makedirs(songs)
        json.dump({"bpm": 120}, open(os.path.join(songs, "demo.json"), "w"))
        ser = FakeSerial()
        br = Bridge(ser, ipc, songs, genre="house", log=lambda *a: None)
        ev = open(os.path.join(ipc, "events.jsonl"), "a")
        ears = open(os.path.join(ipc, "ears.jsonl"), "a")   # exists BEFORE first sight

        ser.feed("HELLO,verdictbox,1"); br.step()
        check("M,idle\n" in [o + "\n" for o in ser.out], "HELLO answered with M,idle")

        ser.feed("BTN,make"); br.step()
        req = json.load(open(os.path.join(ipc, "request.json")))
        check(req["type"] == "make_track" and req["song"] == "demo",
              "MAKE lands make_track on newest song")
        os.remove(os.path.join(ipc, "request.json"))

        ev.write(json.dumps({"id": 1, "kind": "proposal_progress", "song": "demo",
                             "proposal": {}}) + "\n"); ev.flush(); br.step()
        check(ser.out[-1] == "M,compose", "proposal_progress -> M,compose")

        ev.write(json.dumps({"id": 1, "kind": "proposal", "song": "demo",
                             "proposal": {"bpm": 142}}) + "\n"); ev.flush(); br.step()
        check(ser.out[-1] == "M,pending" and "T,142.0" in ser.out,
              "proposal -> T,bpm + M,pending")

        json.dump({"hold": 1}, open(os.path.join(ipc, "request.json"), "w"))
        ser.feed("BTN,accept"); br.step()
        check(br.queued and br.queued["type"] == "accept",
              "busy lane: verdict queued, not clobbered")
        os.remove(os.path.join(ipc, "request.json")); br.step()
        req = json.load(open(os.path.join(ipc, "request.json")))
        check(req["type"] == "accept" and req["song"] == "demo",
              "queued verdict lands once the lane frees")
        os.remove(os.path.join(ipc, "request.json"))

        ev.write(json.dumps({"id": 1, "kind": "accepted", "song": "demo"}) + "\n")
        ev.flush(); br.step()
        check("V,accept" in ser.out[-2:], "accepted -> V,accept flash")

        ears.write(json.dumps({"t": 1, "beat": 2.0, "playing": True,
                               "bands_db": [-15, -25, -35, -45]}) + "\n")
        ears.flush(); br.step()
        check("M,hear" in ser.out[-3:], "playing -> M,hear")
        check(any(o.startswith("E,0.500") for o in ser.out), "ears frame -> E,phase,bands")

        ev.write(json.dumps({"id": 2, "kind": "proposal", "song": "demo",
                             "proposal": {}}) + "\n"); ev.flush()
        br.step()                                     # take pends first...
        ser.feed("BTN,reject_hold"); br.step()        # ...then the verdict

        req = json.load(open(os.path.join(ipc, "request.json")))
        check(req["type"] == "reject" and req.get("reason") == REJECT_HOLD_REASON,
              "reject_hold carries the WHY preset")

    print(f"selftest: {ok[0]} ok, {ok[1]} failed")
    return ok[1] == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port"), ap.add_argument("--genre", default="house")
    ap.add_argument("--songs", default=os.path.join(ROOT, "songs"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest() else 1)

    import serial
    port = args.port or find_port()
    if not port:
        sys.exit("no serial port found - is the box plugged in? (try --port)")
    ipc = os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")
    ser = serial.Serial(port, 115200, timeout=0)
    print(f"[bridge] {port} <-> {ipc}")
    br = Bridge(ser, ipc, args.songs, genre=args.genre)
    try:
        while True:
            br.step()
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\n[bridge] bye")


if __name__ == "__main__":
    main()
