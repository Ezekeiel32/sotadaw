#!/usr/bin/env python3
"""HISTORY SUITE — T2-S4: the 10 history-ask cases (roadmap §5.4, bar >=90%).

The ask class that was ~0 BY CONSTRUCTION this morning (finding B: routing
fragments resident memory), graded against the REAL sidecar. Zero tokens
(mock cloud), zero git: "accept" is simulated exactly as the accept branch
behaves minus commit/telemetry — copy _prop_ onto base, confirm_verdict with
the proposal EVENT's surgical rep + resolutions, delete the prop files.

Cases 1-7 must LAND (correct edit / correct report); 8-10 must REFUSE
(precision polarity: a wrong retarget is worse than a cloud round-trip).
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_histw"
IPC = tempfile.mkdtemp(prefix="histw_ipc_")
os.environ["SOTADAW_IPC"] = IPC
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import session_memory as sm                # noqa: E402
from scalpel_suite import base_song, T, in_win  # noqa: E402

ASKS = os.path.join(ROOT, "telemetry", "asks.jsonl")


class Bus:
    def __init__(self, ipc):
        self.ipc, self.rid = ipc, 970

    def events(self):
        try:
            return [json.loads(l) for l in open(os.path.join(self.ipc, "events.jsonl"))
                    if l.strip()]
        except FileNotFoundError:
            return []

    def prompt(self, text, timeout=180):
        self.rid += 1
        tmp = os.path.join(self.ipc, "request.json.tmp")
        with open(tmp, "w") as f:
            f.write(json.dumps({"type": "prompt", "text": text, "song": SONG,
                                "id": self.rid}))
        os.replace(tmp, os.path.join(self.ipc, "request.json"))
        t0 = time.time()
        while time.time() - t0 < timeout:
            evs = [e for e in self.events() if e.get("id") == self.rid]
            if any(e.get("kind") == "done" for e in evs):
                return evs
            time.sleep(0.25)
        return [e for e in self.events() if e.get("id") == self.rid]


def wipe(fresh_store=True):
    """Fresh fixture song + (optionally) a fresh fact store."""
    for f in os.listdir(SONGS):
        if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
            os.remove(os.path.join(SONGS, f))
    json.dump(base_song(), open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)
    if fresh_store:
        p = os.path.join(sm.memory_dir(), f"{SONG}.jsonl")
        os.path.exists(p) and os.remove(p)


def sim_accept(prop_ev):
    """The accept branch minus git/telemetry: base <- prop, verdict facts, scrub."""
    pp = os.path.join(SONGS, f"_prop_{SONG}.json")
    shutil.copy(pp, os.path.join(SONGS, f"{SONG}.json"))
    sm.confirm_verdict(SONG, prop_ev.get("surgical"), prop_ev.get("resolutions"),
                       prop_ev.get("verb", "") or "accepted")
    for f in (f"_prop_{SONG}.json", f"_prop_{SONG}.wav", f"_prop_{SONG}.ghost.json"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)


def prop_of(evs):
    return next((e for e in evs if e.get("kind") == "proposal"), None)


def load_prop():
    return json.load(open(os.path.join(SONGS, f"_prop_{SONG}.json")))


def main():
    fails = []

    def check(cond, label):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            fails.append(label)

    def hit_and_accept(bus, text):
        evs = bus.prompt(text)
        ev = prop_of(evs)
        # surgical hits carry parsed:true; verb hits self-identify via verb=
        assert ev is not None and (ev.get("parsed") or ev.get("verb")), \
            f"setup ask did not parse: {text!r}"
        sim_accept(ev)
        return ev

    py = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    wipe()
    side = subprocess.Popen([py, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                            env=dict(os.environ, SOTADAW_IPC=IPC, SOTADAW_NO_UPLINK="1"),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    bus = Bus(IPC)
    try:
        # 1 — "do that to the snare too" after a scoped hats edit
        wipe()
        hit_and_accept(bus, "make the hats quieter in the verse only")
        evs = bus.prompt("do that to the snare too")
        ev = prop_of(evs)
        ok = ev is not None and ev.get("parsed")
        if ok:
            b, p = base_song(), load_prop()
            sv = [n["vel"] for n in T(p, "snare")["notes"] if in_win(n, 16, 32)]
            ok = (sv and all(v < 0.85 - 1e-6 for v in sv)
                  and all(abs(n["vel"] - 0.85) < 1e-6
                          for n in T(p, "snare")["notes"] if not in_win(n, 16, 32))
                  and (ev.get("surgical") or {}).get("clean"))
        check(ok, "1  'do that to the snare too' retargets the scoped vel edit")

        # 2 — gain retarget
        wipe()
        hit_and_accept(bus, "make the kick 3db louder")
        evs = bus.prompt("do that to the bass too")
        ev = prop_of(evs)
        ok = ev is not None and ev.get("parsed") \
            and abs(T(load_prop(), "bass")["gainDb"] + 3.0) < 0.01
        check(ok, "2  'do that to the bass too' retargets the gain move (-6 -> -3)")

        # 3 — "same but wider" after a color verb
        wipe()
        hit_and_accept(bus, "make the pad warmer")
        evs = bus.prompt("same but wider")
        ev = prop_of(evs)
        ok = ev is not None and ev.get("verb") == "color" \
            and any(f.get("id") == "fx_widen" for f in T(load_prop(), "pad").get("fx", []))
        check(ok, "3  'same but wider' re-runs color on the SAME target (pad)")

        # 4 — fx retarget
        wipe()
        hit_and_accept(bus, "add some reverb to the pad")
        evs = bus.prompt("do that to the lead too")
        ev = prop_of(evs)
        ok = ev is not None and ev.get("parsed") \
            and any(f.get("id") == "fx_reverb" for f in T(load_prop(), "lead").get("fx", []))
        check(ok, "4  'do that to the lead too' retargets the fx add")

        # 5 — established alias powers a NEW ask class
        wipe()
        sm.write_fact(SONG, "squelchy one", "refers_to", "bass",
                      prov="accepted: prior session")
        evs = bus.prompt("mute the squelchy one")
        ev = prop_of(evs)
        ok = ev is not None and ev.get("parsed") \
            and T(load_prop(), "bass").get("muted") is True
        check(ok, "5  established alias mutes the right track")

        # 6 — "what did we change?" answers from the store
        wipe()
        hit_and_accept(bus, "make the hats quieter in the verse only")
        evs = bus.prompt("what did we change?")
        rep = next((e for e in evs if e.get("kind") == "verb_report"), None)
        check(rep is not None and "hats" in str(rep.get("text", "")),
              "6  'what did we change?' reports the hats edit (memory verb)")

        # 7 — track-scoped history question
        evs = bus.prompt("what did we change on the hats?")
        rep = next((e for e in evs if e.get("kind") == "verb_report"), None)
        check(rep is not None and "hats" in str(rep.get("text", ""))
              and "recent edits" in str(rep.get("text", "")),
              "7  'what did we change on the hats?' filters to the track")

        # 8 — unknown retarget target must REFUSE
        evs = bus.prompt("do that to the guitar too")
        ev = prop_of(evs)
        check(ev is None or not ev.get("parsed"),
              "8  'do that to the guitar too' refuses (no such track) -> cloud rail")

        # 9 — law guard survives the retarget ("same but wider" on a kick edit)
        wipe()
        hit_and_accept(bus, "make the kick 3db louder")
        evs = bus.prompt("same but wider")
        ev = prop_of(evs)
        acts = " | ".join(str(e.get("text")) for e in evs if e.get("kind") == "activity")
        check((ev is None or not ev.get("parsed")) and "verb bus takes it" not in acts,
              "9  'same but wider' after a KICK edit refuses (mono-below-120 law)")

        # 10 — no history at all must REFUSE
        wipe()
        evs = bus.prompt("do that to the snare too")
        ev = prop_of(evs)
        check(ev is None or not ev.get("parsed"),
              "10 'do that…' with an empty store refuses (no hallucinated retarget)")
    finally:
        try:
            side.send_signal(signal.SIGTERM)
            side.wait(timeout=5)
        except Exception:
            side.kill()
        shutil.rmtree(IPC, ignore_errors=True)
        for f in os.listdir(SONGS):
            if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
                os.remove(os.path.join(SONGS, f))
        if os.path.exists(ASKS):
            keep = []
            for l in open(ASKS):
                try:
                    if json.loads(l).get("song") != SONG:
                        keep.append(l)
                except json.JSONDecodeError:
                    keep.append(l)
            if keep:
                with open(ASKS, "w") as f:
                    f.writelines(keep)
            else:
                os.remove(ASKS)
    n = len(fails)
    score = 10 - n
    print(f"\n== HISTORY SUITE: {score}/10 (bar >=9) "
          f"{'ALL GREEN' if n == 0 else 'FAILURES: ' + '; '.join(fails)} ==")
    return 0 if score >= 9 else 1


if __name__ == "__main__":
    sys.exit(main())
