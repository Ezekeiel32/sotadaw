#!/usr/bin/env python3
"""THE DONE-COURT BATTERY — one done per run, machine-enforced (2026-07-13).

The disease (live on Chezy's bus, 3 of the last 12 dones): every Stop that KEPT
a streamed take emitted TWO contradicting dones. keep_canceled_take() emitted
done ok=True (the take is on the deck), the lane returned None, and the prompt
epilogue stamped done ok=False on top — so the run's LAST word was FAILURE on a
take the user was told was KEPT. Telemetry/rigs keying on the final done read
failure; and if the proposal event were ever dropped, the UI's mirage-teardown
branch would tear down the kept take itself.

The law: emit() is the one funnel every event passes through, so the court sits
there — the FIRST done for a request wins; any second stamp (epilogues,
exception handlers, future lanes) is dropped. handle() re-arms the court per
request, because ids are small per-session ints that recycle across UI restarts.

Pure: SOTADAW_IPC points at scratch BEFORE import, SONGS + chronicle are
monkeypatched — the real mailbox, songs/, and .chat are never touched and no
daemon is spawned.

    python3 tools/done_court_battery.py
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = tempfile.mkdtemp(prefix="done_court_")

# isolate BEFORE import: IPC must never point at the real mailbox
os.environ["SOTADAW_IPC"] = SCRATCH
os.environ["SOTADAW_NO_UPLINK"] = "1"
os.environ["SOTADAW_NO_PREWARM"] = "1"

_SIDECAR = os.path.join(ROOT, "agent", "sidecar.py")
_spec = importlib.util.spec_from_file_location("_sc", _SIDECAR)
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)            # module level only — main() never runs

sc.SONGS = SCRATCH                                                   # no real songs/
sc.chronicle = types.SimpleNamespace(append=lambda *a, **k: None)    # no real .chat

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    ok = got == want
    PASS, FAIL = PASS + ok, FAIL + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got {got!r}, want {want!r}")


def events(rid=None, kind=None):
    out = []
    if not os.path.exists(sc.EVENTS):
        return out
    for ln in open(sc.EVENTS):
        e = json.loads(ln)
        if rid is not None and e.get("id") != rid:
            continue
        if kind is not None and e.get("kind") != kind:
            continue
        out.append(e)
    return out


def new_run():
    """what handle() does at entry: the court re-arms for a fresh request."""
    sc._EMIT_CTX.done_for = None
    open(sc.EVENTS, "w").close()


print("== THE DONE-COURT BATTERY ==")

# 1. the raw double-stamp: second done for the SAME request is dropped,
#    and the FIRST word survives (ok=True, not the contradicting ok=False)
new_run()
sc.emit(3, "done", ok=True)
sc.emit(3, "done", ok=False)
check("second done for one request is DROPPED", len(events(3, "done")), 1)
check("...and the surviving word is the FIRST", events(3, "done")[0].get("ok"), True)

# 2. distinct requests are distinct runs — both dones land
new_run()
sc.emit(4, "done", ok=True)
sc._EMIT_CTX.done_for = None            # next pickup re-arms mid-bus
sc.emit(5, "done", ok=False)
check("distinct requests each keep their done", len(events(kind="done")), 2)

# 3. RECYCLED id (ids restart per UI session): after the court re-arms for the
#    new request, the same integer is a FRESH run and its done must land
new_run()
sc.emit(1, "done", ok=True)
sc._EMIT_CTX.done_for = None            # a new session's request 1 is picked up
sc.emit(1, "done", ok=True)
check("recycled id after re-arm still gets its done", len(events(1, "done")), 2)

# 4. THE DISEASE END-TO-END: stop-keep emits done ok=True inside
#    keep_canceled_take; the lane returns None; the epilogue stamps ok=False.
#    Exactly ONE done reaches the bus, it says ok=True, and the proposal
#    event precedes it (the UI arms the deck before the run ends).
new_run()
prop = "_prop_x"
json.dump({"bpm": 120, "tracks": [{"name": "kick", "instrument": "kick",
                                   "notes": [{"start": 0, "len": 1, "pitch": 36, "vel": 0.9}]}]},
          open(os.path.join(SCRATCH, f"{prop}.json"), "w"))
kept = sc.keep_canceled_take(8, "x", prop)
sc.emit(8, "done", ok=False)            # the epilogue's stamp on result=None
check("stop with a streamed take KEEPS it", kept, True)
check("stop-keep run has EXACTLY ONE done", len(events(8, "done")), 1)
check("...and it says ok=True", events(8, "done")[0].get("ok"), True)
kinds = [e["kind"] for e in events(8)]
check("proposal event precedes the done", kinds.index("proposal") < kinds.index("done"), True)

# 5. cancel with NOTHING streamed stays an honest failure: keep_canceled_take
#    declines (no done of its own) and the epilogue's ok=False is the one word
new_run()
kept = sc.keep_canceled_take(9, "y", "_prop_y")   # no prop file exists
sc.emit(9, "done", ok=False)
check("nothing streamed: not kept", kept, False)
check("...and the ONLY done is the honest ok=False",
      [e.get("ok") for e in events(9, "done")], [False])

# 6. SOURCE LAW: handle() must re-arm the court at entry — without it, a
#    recycled per-session id would false-drop a fresh session's first done
head = open(_SIDECAR).read().split("def handle(req):", 1)[1][:600]
check("handle() re-arms the court at entry", "done_for" in head, True)

shutil.rmtree(SCRATCH, ignore_errors=True)
print(f"\ndone-court: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
