#!/usr/bin/env python3
"""FEEDBACK LOOP battery — the UI's "reason" and "held_back" fields are CONSUMED:
reject WHY rides the next prompt VERBATIM (once), the curation law rides 30 min.

Drives the REAL sidecar handlers (import, isolated SOTADAW_IPC, git/telemetry/
provenance mocked — no repo pollution) + the pure feedback_context_block.

Usage: python3 tools/feedback_loop_battery.py
"""
import json, os, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="fb_battery_ipc_")
# This battery isolates by MOCKING run/log_telemetry itself, so the REAL
# accept/reject code paths must execute. An inherited SOTADAW_SANDBOX=1 would
# short-circuit run_git/log_telemetry INSIDE sidecar (captured at import,
# sidecar.py SANDBOX LAW) — silently skipping the exact paths proven here.
os.environ.pop("SOTADAW_SANDBOX", None)
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as sc

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

SONG = "_fb_e2e"
PROP = os.path.join(sc.SONGS, f"_prop_{SONG}.json")
BASE = os.path.join(sc.SONGS, f"{SONG}.json")

git_calls, telemetry = [], []
sc.run = lambda cmd, timeout=900: (git_calls.append(list(cmd)), (0, "", ""))[1]
sc.log_telemetry = lambda song, accepted, note: telemetry.append((song, accepted, note))
sc.stamp_provenance = lambda *a, **k: None
sc.render_and_analyze = lambda *a, **k: None

def stage_prop():
    doc = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0.0, "master": [],
           "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                       "gainDb": -3,
                       "notes": [{"start": float(i), "len": 0.2, "pitch": 36, "vel": 0.9}
                                 for i in range(4)]}]}
    json.dump(doc, open(PROP, "w"))

def scrub():
    for p in (PROP, BASE, PROP.replace(".json", ".ghost.json")):
        if os.path.exists(p):
            os.remove(p)
    tdir = os.path.join(sc.SONGS, ".takes", SONG)
    if os.path.isdir(tdir):
        import shutil
        shutil.rmtree(tdir)

def main():
    scrub()
    # 1) REJECT with a reason: verbatim everywhere
    stage_prop()
    git_calls.clear(); telemetry.clear()
    sc.handle({"id": 1, "type": "reject", "song": SONG, "reason": "too bright, lost the groove"})
    ok(telemetry and telemetry[0][2] == "too bright, lost the groove", "reject: telemetry carries the WHY")
    commits = [c for c in git_calls if "commit" in c]
    ok(any("too bright, lost the groove" in " ".join(c) for c in commits),
       "reject: the take's commit message carries the WHY")
    ok(sc.last_reject.get(SONG, {}).get("why") == "too bright, lost the groove",
       "reject: last_reject stores the WHY verbatim")
    blk = sc.feedback_context_block(SONG, revise=False)
    ok('VERBATIM: "too bright, lost the groove"' in blk, "next prompt QUOTES the reason verbatim")
    ok(sc.feedback_context_block(SONG, revise=False) == "", "reject context rides exactly ONCE (popped)")

    # 2) REJECT falls back to legacy note field
    stage_prop()
    sc.handle({"id": 2, "type": "reject", "song": SONG, "note": "nah"})
    ok(sc.last_reject.get(SONG, {}).get("why") == "nah", "reason absent -> note fallback")
    sc.last_reject.pop(SONG, None)

    # 3) REJECT with neither: block still renders, no quote line
    sc.last_reject[SONG] = {"t": time.time(), "notes": 12, "why": ""}
    blk = sc.feedback_context_block(SONG, revise=False)
    ok("REJECTED a proposal" in blk and "VERBATIM" not in blk, "no reason -> classic context, no fake quote")

    # 4) revise NEVER consumes reject context
    sc.last_reject[SONG] = {"t": time.time(), "notes": 5, "why": "x"}
    ok(sc.feedback_context_block(SONG, revise=True) == "", "revise: reject context suppressed")
    ok(SONG in sc.last_reject, "revise: ...and NOT popped")
    sc.last_reject.pop(SONG, None)

    # 5) ACCEPT with held_back: curation law rides, 30 min, NOT popped
    stage_prop()
    sc.handle({"id": 3, "type": "accept", "song": SONG,
               "held_back": ["lead: F#4 @ b2.75", "bass: A1 @ b1.00"]})
    ok(os.path.exists(BASE), "accept: prop landed on base")
    lc = sc.last_curation.get(SONG)
    ok(lc and lc["held"] == ["lead: F#4 @ b2.75", "bass: A1 @ b1.00"], "accept: held_back consumed")
    blk = sc.feedback_context_block(SONG, revise=False)
    ok("CURATION LAW" in blk and "lead: F#4 @ b2.75" in blk and "Do NOT re-add" in blk,
       "next prompt carries the do-not-readd law")
    ok("CURATION LAW" in sc.feedback_context_block(SONG, revise=False),
       "curation law RIDES repeatedly (not popped)")
    ok("CURATION LAW" in sc.feedback_context_block(SONG, revise=True),
       "curation law rides revisions too")
    sc.last_curation[SONG]["t"] = time.time() - 1900
    ok(sc.feedback_context_block(SONG, revise=False) == "", "curation law expires after 30 min")
    sc.last_curation.pop(SONG, None)

    # 6) accept WITHOUT held_back leaves no residue
    stage_prop()
    sc.handle({"id": 4, "type": "accept", "song": SONG})
    ok(SONG not in sc.last_curation, "plain accept: no curation residue")

    # 7) RESTART SURVIVAL: verdicts persist to ipc/feedback_state.json and reload
    stage_prop()
    sc.handle({"id": 5, "type": "reject", "song": SONG, "reason": "survives restarts"})
    stage_prop()
    sc.handle({"id": 6, "type": "accept", "song": SONG, "held_back": ["kick: C2 @ b1.00"]})
    saved = json.load(open(sc.FEEDBACK_STATE))
    ok(saved["last_reject"].get(SONG, {}).get("why") == "survives restarts",
       "reject WHY persisted to disk")
    ok(saved["last_curation"].get(SONG, {}).get("held") == ["kick: C2 @ b1.00"],
       "curation persisted to disk")
    sc.last_reject.clear()
    sc.last_curation.clear()      # simulate the restart's fresh process state
    sc.load_feedback_state()
    ok(sc.last_reject.get(SONG, {}).get("why") == "survives restarts"
       and SONG in sc.last_curation, "state reloads after 'restart'")
    sc.last_reject.pop(SONG, None)
    sc.last_curation.pop(SONG, None)

    # 8) DOUBLE-CLICK IDEMPOTENCE: a second accept inside the round-trip window is
    # BENIGN (status), never an error — today's live-user pain x4
    stage_prop()
    ev = os.path.join(os.environ["SOTADAW_IPC"], "events.jsonl")
    sc.handle({"id": 7, "type": "accept", "song": SONG})
    n0 = sum(1 for _ in open(ev)) if os.path.exists(ev) else 0
    sc.handle({"id": 8, "type": "accept", "song": SONG})   # prop already consumed
    tail = [json.loads(l) for l in list(open(ev))[n0:]]
    ok(not any(e.get("kind") == "error" for e in tail),
       "double accept: NO error event")
    ok(any(e.get("kind") == "status" and "already accepted" in e.get("text", "") for e in tail),
       "double accept: benign status names the double-click")
    ok(any(e.get("kind") == "done" and e.get("ok") for e in tail), "double accept: done ok")
    sc.last_verdict_t.pop(SONG, None)

    # 9) SANDBOX LAW: with SOTADAW_SANDBOX, verdicts leave NO git/telemetry trace
    stage_prop()
    git_calls.clear(); telemetry.clear()
    sc.SANDBOX = True
    try:
        sc.handle({"id": 10, "type": "reject", "song": SONG, "reason": "sandboxed"})
        ok(not any("commit" in c for c in git_calls), "sandbox: zero git commits")
        stage_prop()
        sc.handle({"id": 11, "type": "accept", "song": SONG})
        ok(not any("commit" in c for c in git_calls), "sandbox: accept commits nothing")
    finally:
        sc.SANDBOX = False
    sc.last_reject.pop(SONG, None)
    sc.last_verdict_t.pop(SONG, None)

    scrub()


def recovery_brain():
    """W8 — the pure loudness-recovery decision: lift toward lufs_lo, capped by
    the genre's PSR floor (PLR budget), stop on dirty/at-target. Zero renders."""
    A = lambda lufs, dbtp, clip=0: {"clipped_samples": clip,
                                    "lufs_integrated": lufs, "true_peak_dbtp": dbtp}
    d, why = sc.recovery_step(A(-16.0, -1.3), -12.0, None, 0.0)
    ok(d == 4.0 and why == "lift", f"R1: plain lift toward the floor ({d} {why})")
    d, why = sc.recovery_step(A(-16.0, -1.3), -12.0, 5.0, 0.0)
    ok(d == 4.0, f"R2: PLR 14.7 has budget — full lift ({d})")
    d, why = sc.recovery_step(A(-16.0, -9.0), -12.0, 5.0, 0.0)
    ok(d == 2.0 and "capped" in why, f"R3: PLR 7.0, floor 5 -> lift capped at 2.0 ({d} {why})")
    d, why = sc.recovery_step(A(-10.0, -5.2), -6.0, 5.0, 0.0)
    ok(d == 0.0 and why.startswith("PSR floor"), f"R4: PLR 4.8 at floor -> punchy over loud ({why})")
    d, why = sc.recovery_step(A(-16.0, -1.3, clip=9), -12.0, None, 0.0)
    ok(d == 0.0 and why == "not clean", "R5: clipped take never lifts")
    d, why = sc.recovery_step(A(-12.2, -1.3), -12.0, None, 0.0)
    ok(d == 0.0 and why == "at target", "R6: within 0.4 dB = at target")
    d, why = sc.recovery_step(A(-16.0, -1.3), -12.0, None, 7.8)
    ok(d == 0.0, "R7: max_push budget spent -> stop")
    d, why = sc.recovery_step(A(-16.0, "bad"), -12.0, 5.0, 0.0)
    ok(d == 4.0, "R8: unparsable dBTP fails OPEN (lift, no floor check)")
    # W41 THE BREATH GUARD: PSR guards crest, not macro-breathing — when the
    # CURRENT ears already read at/below the LRA floor, the lift stops.
    AL = lambda lufs, dbtp, lra: {"clipped_samples": 0, "lufs_integrated": lufs,
                                  "true_peak_dbtp": dbtp, "lra": lra}
    d, why = sc.recovery_step(AL(-16.0, -1.3, 2.8), -12.0, None, 0.0, lra_floor=3.2)
    ok(d == 0.0 and why.startswith("LRA squash guard"),
       f"R9: squashed take (LRA 2.8 <= 3.2) never lifts ({why})")
    d, why = sc.recovery_step(AL(-16.0, -1.3, 5.0), -12.0, None, 0.0, lra_floor=3.2)
    ok(d == 4.0 and why == "lift", f"R10: breathing take (LRA 5.0) lifts ({d})")
    d, why = sc.recovery_step(A(-16.0, -1.3), -12.0, None, 0.0, lra_floor=3.2)
    ok(d == 4.0, "R11: no lra in the analysis fails OPEN (lift)")
    d, why = sc.recovery_step(AL(-16.0, -1.3, 3.8), -12.0, None, 0.0, lra_floor=4.0)
    ok(d == 0.0 and why.startswith("LRA squash guard"),
       "R12: a GENRE floor above 3.2 protects more breath (dnb 4.0)")


if __name__ == "__main__":
    main()
    recovery_brain()
    for f in FAIL:
        print("FAIL:", f)
    # W101 THE VOICE CTX LAW: singing asks route to the vocal journey;
    # plain asks don't (start_session never sees non-genre words)
    ok(sc.voice_ctx_block("make a pop song with vocals") != ""
       and "vocal-topline" in sc.voice_ctx_block("sing this melody")
       and "hum_topline" in sc.voice_ctx_block("add a sung topline")
       and sc.voice_ctx_block("make it louder") == ""
       and sc.voice_ctx_block("") == ""
       and "Gahata Meiji" in sc.voice_ctx_block("give it lyrics"),
       "W101: voice asks route to the singing journey (plain asks silent)")
    # W129: vocal-LED genre with no sing-word = one-line NUDGE (not the full
    # journey); 'instrumental' silences it; non-vocal genres stay silent
    ok("VOICE NUDGE" in sc.voice_ctx_block("MAKE A WORLD VIRAL IT POP SONG FOR 2027!")
       and "VOICE NUDGE" in sc.voice_ctx_block("an anthemic soul record")
       and sc.voice_ctx_block("a pop instrumental for the outro") == ""
       and sc.voice_ctx_block("dark techno banger 140bpm") == ""
       and "VOICE ASK" in sc.voice_ctx_block("pop song with vocals"),
       "W129: vocal-led genres get the nudge; instrumental/others silent")

    # W116: the breath guard fires only NEAR THE WALL — a flat quiet take
    # lifts as pure gain; a flat take already at the wall stays guarded
    d_quiet, w_quiet = sc.recovery_step(
        {"clipped_samples": 0, "lufs_integrated": -38.0, "true_peak_dbtp": -20.0,
         "lra": 0.8}, -12.0, 5.0, 0.0, lra_floor=3.2)
    d_wall, w_wall = sc.recovery_step(
        {"clipped_samples": 0, "lufs_integrated": -13.5, "true_peak_dbtp": -1.4,
         "lra": 0.8}, -12.0, 5.0, 0.0, lra_floor=3.2)
    ok(d_quiet >= 4.0 and d_wall == 0.0 and "squash guard" in w_wall,
       "W116: quiet-flat (dBTP -20) lifts as pure gain; at-wall flat stays guarded")

    print(f"feedback-loop battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
