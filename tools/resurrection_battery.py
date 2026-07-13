#!/usr/bin/env python3
"""RESURRECTION COURT battery — a dead run's leftover prop must be judged on
byte evidence at boot: rejected-archive twins and base twins swept (with their
ghost/wav siblings + receipts), superseded twins KEPT with one honest chronicle
note, orphaned siblings finished, everything else untouched (a real pending
decision keeps full deck rights).

Drives the REAL sidecar.resurrection_sweep() in a hermetic yard: SOTADAW_IPC
sandboxes chronicle + receipts, sc.SONGS points at a tmp songs dir — no repo
pollution, no scrub debt.

Usage: python3 tools/resurrection_battery.py
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="rc_battery_ipc_")
os.environ.pop("SOTADAW_CHRONICLE", None)      # the note law is under proof here
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as sc

sc.SONGS = tempfile.mkdtemp(prefix="rc_battery_songs_")

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def P(name):
    return os.path.join(sc.SONGS, name)

def put(name, payload):
    open(P(name), "w").write(payload)

def take(song, fname, payload):
    tdir = os.path.join(sc.SONGS, ".takes", song)
    os.makedirs(tdir, exist_ok=True)
    open(os.path.join(tdir, fname), "w").write(payload)

DOC = json.dumps({"version": 2, "bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
     "notes": [{"start": 0.0, "len": 0.2, "pitch": 36, "vel": 0.9}]}]})
OTHER = DOC.replace("120", "121")

# ---- class A-r: prop == a *_rejected.json archive -> finish the reject's sweep
put("_prop_ar1.json", DOC)
put("_prop_ar1.ghost.json", DOC)
put("_prop_ar1.wav", "RIFFfake")
put("_prop_ar1.prev.wav", "RIFFfake2")
put("ar1.json", OTHER)
take("ar1", "1000_rejected.json", DOC)
sc.surgical.coarse_receipt("_prop_ar1", "write_song", fields=["*"], summary="battery seed")

# ---- A-r negative: one byte differs -> a real pending decision, keep it
put("_prop_ar2.json", DOC[:-1] + " ")
put("ar2.json", OTHER)
take("ar2", "1000_rejected.json", DOC)

# ---- class B: prop == base -> the accept's sweep died; zero-diff entry, sweep
put("_prop_b1.json", DOC)
put("b1.json", DOC)

# ---- B negative: differs from base, no takes -> pending, keep
put("_prop_b2.json", DOC)
put("b2.json", OTHER)

# ---- class S: prop == *_superseded.json -> KEEP + one honest note
put("_prop_s1.json", DOC)
put("s1.json", OTHER)
take("s1", "2000_superseded.json", DOC)

# ---- class C: orphaned siblings (no prop json, base EXISTS)
put("_prop_c1.ghost.json", DOC)
put("_prop_c1.wav", "RIFFfake")
put("_prop_c1.prev.wav", "RIFFfake2")
put("c1.json", DOC)
# C negatives: no base -> not provably ours; sung vocal shape -> never an orphan
put("_prop_c2.ghost.json", DOC)
put("_prop_c1_lead_vocal.wav", "RIFFsung")
# corpse court's evidence stays untouched
put("_prop_c3.json.corpse", "{broken")
put("c3.json", DOC)

v1 = sc.resurrection_sweep()
verd = {(s, kind) for s, kind, _ in v1}

ok(("ar1", "swept") in verd, "A-r: rejected-twin prop swept")
ok(not os.path.exists(P("_prop_ar1.json")), "A-r: prop json removed")
ok(not os.path.exists(P("_prop_ar1.ghost.json")), "A-r: ghost sibling removed")
ok(not os.path.exists(P("_prop_ar1.wav")), "A-r: wav sibling removed")
ok(not os.path.exists(P("_prop_ar1.prev.wav")), "A-r: prev.wav sibling removed")
ok(sc.surgical.read_receipts("_prop_ar1") == [], "A-r: receipts cleared with the prop")
ok(any("REJECTED" in r.get("text", "") and r.get("role") == "note"
       for r in (sc.chronicle.read("ar1") or [])), "A-r: honest chronicle note filed")
ok(os.path.exists(P("_prop_ar2.json")) and ("ar2", "swept") not in verd,
   "A-r negative: near-identical prop keeps deck rights")

ok(("b1", "swept") in verd and not os.path.exists(P("_prop_b1.json")),
   "B: base-twin prop swept")
ok(os.path.exists(P("b1.json")), "B: the base itself untouched")
ok(any("LANDED" in r.get("text", "") for r in (sc.chronicle.read("b1") or [])),
   "B: chronicle says LANDED")
ok(os.path.exists(P("_prop_b2.json")) and ("b2", "swept") not in verd,
   "B negative: differing pending prop kept")

ok(("s1", "stalled-revise") in verd, "S: stalled revise recognized")
ok(os.path.exists(P("_prop_s1.json")), "S: the pending take is KEPT")
srows = [r for r in (sc.chronicle.read("s1") or [])
         if r.get("court_key") == "2000_superseded.json"]
ok(len(srows) == 1 and "DIED mid-run" in srows[0].get("text", ""),
   "S: exactly one keyed honest note")

ok(("c1", "orphan-swept") in verd and not os.path.exists(P("_prop_c1.ghost.json"))
   and not os.path.exists(P("_prop_c1.wav")) and not os.path.exists(P("_prop_c1.prev.wav")),
   "C: orphaned ghost+wav+prev finished")
ok(os.path.exists(P("_prop_c2.ghost.json")), "C negative: no base, ghost stays")
ok(os.path.exists(P("_prop_c1_lead_vocal.wav")), "C negative: sung vocal wav is NOT an orphan")
ok(os.path.exists(P("_prop_c3.json.corpse")), "corpse evidence untouched")

# ---- idempotence: the yard is judged; a second sweep must be silent
v2 = sc.resurrection_sweep()
ok(v2 == [], f"idempotent: second sweep returns no verdicts (got {v2})")
ok(len([r for r in (sc.chronicle.read("s1") or []) if r.get("court_key")]) == 1,
   "S idempotent: still exactly one note")

# ---- a SECOND dead revise freezing the SAME bytes adds an archive but no spam
take("s1", "3000_superseded.json", DOC)
v3 = sc.resurrection_sweep()
ok(len([r for r in (sc.chronicle.read("s1") or []) if r.get("court_key")]) == 1,
   "S: identical re-freeze does not repeat the note")

for d in (sc.SONGS, os.environ["SOTADAW_IPC"]):
    shutil.rmtree(d, ignore_errors=True)

print(f"resurrection_battery: {PASS} passed, {len(FAIL)} failed")
for f in FAIL:
    print(f"  FAIL: {f}")
sys.exit(1 if FAIL else 0)
