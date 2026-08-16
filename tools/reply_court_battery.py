#!/usr/bin/env python3
"""THE REPLY-COURT BATTERY — a message is not an edit (2026-07-17).

The disease (Chezy, live): every EDIT-run nuance fired on EVERY message. The
prop was entry-minted per ask, so ~0.7s into ANY message the ghost watcher
shipped a base-identical proposal_progress (Listen-live armed, deck chips grew,
ghost banner lit); a question answered in prose ended as a FAILED EDIT ("came
back with NO changes" error + done ok=False); a question over a standing take
re-rendered/re-walled/re-emitted that take per message; and Stop seconds into
any run KEPT a base-identical phantom take with a freshly staged wall.

The law: judge what the run actually DID.
  classify_run_end  — reply / untouched_pending / empty_edit / changed (pure)
  ask_wants_edit    — EDIT_RE|BIG_RE|EDIT_HINT_RE, verbs-only (pure)
  ghost_gate        — zero-diff snapshots never arm the UI (one-way gate)
  keep_canceled_take— phantom-keep court (entry-bytes evidence, fail-open)
  emit_action       — mutating tool_use marks the run as an EDIT ATTEMPT

Pure: SOTADAW_IPC points at scratch BEFORE import; SONGS + chronicle are
monkeypatched — the real mailbox, songs/ and .chat are never touched and no
daemon is spawned.

    python3 tools/reply_court_battery.py
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = tempfile.mkdtemp(prefix="reply_court_")

os.environ["SOTADAW_IPC"] = SCRATCH
os.environ["SOTADAW_NO_UPLINK"] = "1"
os.environ["SOTADAW_NO_PREWARM"] = "1"

_SIDECAR = os.path.join(ROOT, "agent", "sidecar.py")
_spec = importlib.util.spec_from_file_location("_sc", _SIDECAR)
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

sc.SONGS = SCRATCH
sc.chronicle = types.SimpleNamespace(append=lambda *a, **k: None)

PASS = FAIL = 0


def check(name, got, want=True):
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
    sc._EMIT_CTX.done_for = None
    open(sc.EVENTS, "w").close()


print("== THE REPLY-COURT BATTERY ==")

# ---------------------------------------------------------------- 1. the kernel
print("-- classify_run_end (pure truth table)")
C = sc.classify_run_end
check("question, nothing done -> reply",
      C(False, 0, False, False, False), "reply")
check("equal docs + receipts landed -> empty_edit (edits dissolved)",
      C(False, 2, False, False, False), "empty_edit")
check("equal docs + a mutating tool was TRIED -> empty_edit",
      C(False, 0, True, False, False), "empty_edit")
check("equal docs + edit-shaped ask -> empty_edit (W99 narrated-done class)",
      C(False, 0, False, True, False), "empty_edit")
check("standing take untouched -> untouched_pending",
      C(True, 0, False, False, True), "untouched_pending")
check("standing take + receipts this run -> changed (re-judge)",
      C(True, 1, False, False, True), "changed")
check("take moved -> changed",
      C(True, 0, False, False, False), "changed")
check("take moved on a question ask still -> changed",
      C(True, 0, False, True, False), "changed")

# ------------------------------------------------------------ 2. ask_wants_edit
print("-- ask_wants_edit (verbs yes, questions no)")
for t in ("make the hats louder", "add a pad under the chorus",
          "make me a dark techno track", "turn the bass up",
          "can you extend it to 64 bars", "change the key to F minor",
          "fix the muddy low end"):
    check(f"edit ask: {t!r}", sc.ask_wants_edit(t))
for t in ("what key is this in?", "how does the second drop sound?",
          "which track carries the melody?", "why does it feel empty at bar 12?",
          "tell me about the mix balance", "is this ready to release?"):
    check(f"question: {t!r}", sc.ask_wants_edit(t), False)

# ---------------------------------------------------------------- 3. ghost_gate
print("-- ghost_gate (zero-diff snapshots never arm the UI)")
BASE = {"bpm": 120, "lengthBars": 4,
        "tracks": [{"name": "kick", "notes": [{"start": 0, "len": 1, "pitch": 36, "vel": 0.9}]}]}
json.dump(BASE, open(os.path.join(SCRATCH, "x.json"), "w"))
gate = sc.ghost_gate("x")
check("base-identical snapshot holds fire", gate(json.loads(json.dumps(BASE))), False)
moved_doc = json.loads(json.dumps(BASE))
moved_doc["tracks"][0]["notes"].append({"start": 2, "len": 1, "pitch": 38, "vel": 0.8})
check("first real change opens the gate", gate(moved_doc))
check("gate is ONE-WAY (back-to-base keeps streaming)",
      gate(json.loads(json.dumps(BASE))))
check("unreadable base fails open (streams)", sc.ghost_gate("nosuch")({"any": 1}))

# ------------------------------------------------- 4. keep_canceled_take court
print("-- keep_canceled_take (the phantom-keep court)")
# a. fresh mint, nothing streamed: cancel clean, mint removed, NO done of its own
new_run()
json.dump(BASE, open(os.path.join(SCRATCH, "y1.json"), "w"))
entry = open(os.path.join(SCRATCH, "y1.json"), "rb").read()
open(os.path.join(SCRATCH, "_prop_y1.json"), "wb").write(entry)
kept = sc.keep_canceled_take(21, "y1", "_prop_y1", entry, False)
check("fresh mint + no stream: NOT kept", kept, False)
check("...the mint left with it",
      os.path.exists(os.path.join(SCRATCH, "_prop_y1.json")), False)
check("...and no done was stamped (the epilogue owns it)", len(events(21, "done")), 0)

# b. pending take, nothing streamed: it stays EXACTLY as it was
new_run()
json.dump(BASE, open(os.path.join(SCRATCH, "y2.json"), "w"))
PEND = json.loads(json.dumps(BASE))
PEND["tracks"][0]["gainDb"] = -3
json.dump(PEND, open(os.path.join(SCRATCH, "_prop_y2.json"), "w"))
entry = open(os.path.join(SCRATCH, "_prop_y2.json"), "rb").read()
kept = sc.keep_canceled_take(22, "y2", "_prop_y2", entry, True)
check("pending + no stream: kept (standing take survives)", kept, True)
check("...done ok=True", [e.get("ok") for e in events(22, "done")], [True])
check("...NO proposal re-emit (deck already holds it)", len(events(22, "proposal")), 0)
check("...take bytes UNTOUCHED (no wall staged into it)",
      open(os.path.join(SCRATCH, "_prop_y2.json"), "rb").read() == entry)

# c. real streamed work: kept, wall staged, deck armed (the 2026-07-11 law holds)
new_run()
json.dump(BASE, open(os.path.join(SCRATCH, "y3.json"), "w"))
entry = open(os.path.join(SCRATCH, "y3.json"), "rb").read()
WORK = json.loads(json.dumps(BASE))
WORK["tracks"].append({"name": "pad", "notes": [{"start": 0, "len": 4, "pitch": 60, "vel": 0.6}]})
json.dump(WORK, open(os.path.join(SCRATCH, "_prop_y3.json"), "w"))
kept = sc.keep_canceled_take(23, "y3", "_prop_y3", entry, False)
check("streamed work: KEPT", kept, True)
kinds = [e["kind"] for e in events(23)]
check("...proposal precedes done", "proposal" in kinds and "done" in kinds
      and kinds.index("proposal") < kinds.index("done"))
wj = json.load(open(os.path.join(SCRATCH, "_prop_y3.json")))
check("...release wall staged LAST",
      bool(wj.get("master")) and wj["master"][-1].get("id") == "fx_truepeak")

# d. streamed BACK to base-identical (doc-level): zero-diff serves nobody
new_run()
json.dump(BASE, open(os.path.join(SCRATCH, "y4.json"), "w"))
entry = open(os.path.join(SCRATCH, "y4.json"), "rb").read()
json.dump(BASE, open(os.path.join(SCRATCH, "_prop_y4.json"), "w"), indent=1)  # bytes differ
kept = sc.keep_canceled_take(24, "y4", "_prop_y4", entry, False)
check("back-to-base take: NOT kept", kept, False)
check("...and swept", os.path.exists(os.path.join(SCRATCH, "_prop_y4.json")), False)

# e. legacy caller (no entry bytes) + unreadable base: FAIL OPEN to keeping
new_run()
json.dump(WORK, open(os.path.join(SCRATCH, "_prop_y5.json"), "w"))
kept = sc.keep_canceled_take(25, "y5", "_prop_y5")
check("legacy + no base: fails open to KEEP (never delete work on doubt)", kept, True)

# ------------------------------------------------------ 5. the attempt tracker
print("-- emit_action marks edit ATTEMPTS (previews and reads never count)")
new_run()
sc._RUN_EDIT_ATTEMPTS.clear()
sc.emit_action(50, {"name": "mcp__daw__update_track",
                    "input": {"song": "_prop_x", "track": "kick", "gainDb": -3}})
check("update_track marks the run", sc._RUN_EDIT_ATTEMPTS.get(50, False))
sc.emit_action(51, {"name": "mcp__daw__surgical_edit",
                    "input": {"preview": True, "ops": [{"op": "shift"}]}})
check("surgical_edit PREVIEW does not", 51 in sc._RUN_EDIT_ATTEMPTS, False)
sc.emit_action(52, {"name": "mcp__daw__get_song", "input": {"name": "x"}})
check("get_song does not", 52 in sc._RUN_EDIT_ATTEMPTS, False)
sc.emit_action(53, {"name": "mcp__daw__locate", "input": {"query": "the drop"}})
check("locate does not", 53 in sc._RUN_EDIT_ATTEMPTS, False)

# ---------------------------------------------------------- 6. wiring source law
print("-- source law (the seams stay wired)")
src = open(_SIDECAR).read()
handle_src = src.split("def handle(req):", 1)[1]
check("handle() classifies the run end", "classify_run_end(" in handle_src)
check("handle() captures pre-state receipts", "_pre_rc_n" in handle_src)
rp_src = src.split("def real_propose(", 1)[1]
check("real_propose arms ONE ghost gate per run", "ghost_gate(song_name)" in rp_src)
check("all three cancel sites carry entry evidence",
      rp_src.count("keep_canceled_take(req_id, song_name, prop, entry_take_bytes, revise)"), 3)
check("all three watchers hold zero-diff fire", rp_src.count("_ghost_moved("), 3)

shutil.rmtree(SCRATCH, ignore_errors=True)
print(f"\nreply-court: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
