#!/usr/bin/env python3
"""THE STAND-DOWN CHECK (W118) — is Chezy's session producing RIGHT NOW?

The live-session law: his compute outranks any campaign work. Every heavy
sweep (guardian suite, render corpora, builds) calls this FIRST:

    tools/user_live.py && echo "LIVE - stand down" || echo "idle - proceed"

Exit 0 = LIVE (recent agent events or an unconsumed request) -> stand down.
Exit 1 = idle -> heavy work may proceed.

Born from the untitled_34 meter death (2026-07-11): a campaign suite +
a 19-render sweep ran while his agent produced at max effort, and the
contention blew analyze2's timeout on HIS take.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = os.environ.get("SOTADAW_IPC", os.path.join(ROOT, "agent", "ipc"))
WINDOW_S = float(os.environ.get("SOTADAW_LIVE_WINDOW_S", "180"))


def user_is_live():
    req = os.path.join(IPC, "request.json")
    if os.path.exists(req) and time.time() - os.path.getmtime(req) < WINDOW_S:
        return True, "unconsumed/recent request.json"
    # A RUN IN FLIGHT IS LIVE (2026-07-11): max-effort streams gap >3 min
    # between events — the event window alone read an ACTIVE run as idle.
    # request.json.working exists exactly while handle() runs; that file is
    # the ground truth (1h staleness cap guards crashed leftovers).
    work = req + ".working"
    if os.path.exists(work) and time.time() - os.path.getmtime(work) < 3600:
        age = time.time() - os.path.getmtime(work)
        return True, f"request in flight ({age / 60:.0f} min)"
    ev = os.path.join(IPC, "events.jsonl")
    if os.path.exists(ev):
        try:
            # 32KB tail: a thinking-stream storm filled 4KB with noise-skipped
            # lines and the gate read LIVE sessions as idle (2026-07-11)
            with open(ev, "rb") as f:
                f.seek(max(0, os.path.getsize(ev) - 32768))
                tail = f.read().decode(errors="replace").strip().splitlines()
            for line in reversed(tail):
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                # daemon lifecycle noise is NOT user activity (the daemon
                # self-refreshes at idle — those very events read as LIVE
                # and locked the gate closed, 2026-07-11)
                txt = str(e.get("text", ""))
                if e.get("kind") == "status" and (
                        "self-refresh" in txt or "agent online" in txt
                        or "agent offline" in txt):
                    continue
                # injected/synthetic events (sibling camera rigs write t-less
                # or t=1 lines into the LIVE stream, 2026-07-11) have no real
                # clock — skipping keeps scanning; breaking on one would read
                # an ACTIVE session as idle
                if float(e.get("t", 0) or 0) < 1e9:
                    continue
                age = time.time() - float(e.get("t", 0))
                if age < WINDOW_S:
                    return True, f"agent event {age:.0f}s ago ({e.get('kind')})"
                break
        except OSError:
            pass
    return False, "no recent session activity"


if __name__ == "__main__":
    live, why = user_is_live()
    print(("LIVE: " if live else "idle: ") + why)
    sys.exit(0 if live else 1)
