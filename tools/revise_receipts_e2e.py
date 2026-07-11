#!/usr/bin/env python3
"""THE PROPOSAL-LIFETIME seam proof (2026-07-11, commit 8025520).

Drives the REAL sidecar.handle() with isolated IPC and proves the
revise-wipe class is dead at the protocol seam (the class behind Chezy's
live "OUT OF SCOPE: 3 — rhodes_aurora/sunrise/vocals_peak fx changed"):

  run 1 (fresh ask, mock)  -> prop born; run-1 files a set_track_fx-style
                              receipt for its fx/automation edits
  run 2 (revise, mock)     -> prop PENDING at entry: the ledger SURVIVES
                              (pre-fix, clear_receipts() wiped it here) and
                              the run-2 scope verdict does NOT flag run-1's
                              receipted fields
  run 3 (fresh ask, song B)-> B's entry-clear touches only B's lines; the
                              still-pending song-A ledger is untouched

Zero tokens (mock lane). Run: python3 tools/revise_receipts_e2e.py
"""
import glob
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")


def main():
    ipc = tempfile.mkdtemp(prefix="rre2e_ipc_")
    os.environ["SOTADAW_IPC"] = ipc
    os.environ["SOTADAW_CHRONICLE"] = "0"
    # THE SANDBOX LAW: IPC isolation does NOT contain git/telemetry.
    os.environ["SOTADAW_SANDBOX"] = "1"
    os.environ["SOTADAW_PARSE"] = "0"   # revises/asks stay on the mock rail
    sys.argv.append("--mock")           # sidecar reads MOCK from argv at import
    sys.path.insert(0, os.path.join(ROOT, "agent"))
    import sidecar as sc
    import surgical as S

    fails = []

    def check(tag, ok, detail=""):
        print(f"  {'ok' if ok else 'XX'} {tag}" + (f"  [{detail}]" if detail and not ok else ""))
        if not ok:
            fails.append(tag)

    def events():
        out = []
        try:
            for line in open(os.path.join(ipc, "events.jsonl")):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
        except FileNotFoundError:
            pass
        return out

    def last_verdict():
        props = [e for e in events() if e.get("kind") == "proposal"
                 and isinstance(e.get("surgical"), dict)]
        return (props[-1]["surgical"] if props else {})

    A, B = "_rre2e_a", "_rre2e_b"
    for s in (A, B):
        for p in glob.glob(os.path.join(SONGS, f"*{s}*")):
            os.remove(p)
    fixture = {"bpm": 120, "lengthBars": 2, "key": "A minor", "tracks": [
        {"name": "pad", "source": {"kind": "faust", "id": "warmpad"},
         "gainDb": -14,
         "notes": [{"start": 0.0, "len": 2.0, "pitch": 57, "vel": 0.4}]}]}
    json.dump(fixture, open(os.path.join(SONGS, A + ".json"), "w"))
    json.dump(fixture, open(os.path.join(SONGS, B + ".json"), "w"))
    try:
        # run 1: fresh ask — the mock's sweep words stage fx/automation on pad
        sc.handle({"id": 9301, "type": "prompt", "song": A,
                   "text": "add a slow filter sweep for motion"})
        prop_a = f"_prop_{A}"
        pj = os.path.join(SONGS, prop_a + ".json")
        check("run 1: proposal born", os.path.exists(pj))
        pdoc = json.load(open(pj))
        pt = next((t for t in pdoc.get("tracks", []) if t.get("name") == "pad"), {})
        changed_fx = bool(pt.get("fx")) or bool(pdoc.get("automation"))
        check("run 1: mock staged fx/automation", changed_fx)
        # run-1's tools would have receipted DURING the run — file the same
        S.coarse_receipt(prop_a, "set_track_fx",
                         fields=["track:pad:fx", "track:pad:automation",
                                 "meta:automation"],
                         summary="run-1 sweep (seam-proof twin of the live class)")
        n_before = len(S.read_receipts(prop_a))
        check("run 1: ledger holds the receipt", n_before >= 1)

        # run 2: REVISE on the pending prop — the ledger must survive entry
        sc.handle({"id": 9302, "type": "prompt", "song": A, "revise": True,
                   "text": "make the pad quieter"})
        survived = [r for r in S.read_receipts(prop_a)
                    if r.get("tool") == "set_track_fx"]
        check("run 2: run-1 receipt SURVIVED the revise entry (the fix)",
              len(survived) == 1)
        v = last_verdict()
        oos = "; ".join(v.get("out_of_scope", []))
        check("run 2: receipted fx/automation NOT flagged",
              "fx changed" not in oos and "automation" not in oos, oos)

        # run 3: fresh ask on song B — its entry-clear is per-song
        sc.handle({"id": 9303, "type": "prompt", "song": B,
                   "text": "make it quieter"})
        check("run 3: song-A ledger untouched by song-B's fresh clear",
              len([r for r in S.read_receipts(prop_a)
                   if r.get("tool") == "set_track_fx"]) == 1)

        # run 4: THE CORPSE COURT — a half-context pending prop (the mid-run-
        # accept collision class) is quarantined at entry, the run proceeds
        with open(pj, "w") as f:
            f.write('{"comment": "half-context corpse, no tracks, no bpm"}')
        sc.handle({"id": 9304, "type": "prompt", "song": A, "revise": True,
                   "text": "make the pad quieter"})
        check("run 4: corpse quarantined to .corpse", os.path.exists(pj + ".corpse"))
        fresh = os.path.exists(pj) and bool(json.load(open(pj)).get("tracks"))
        check("run 4: the run rebirthed a SERVING prop from base", fresh)
        print(("PASS" if not fails else "FAIL") + " revise-receipts e2e "
              + f"({9 - len(fails)}/9)")
        return 1 if fails else 0
    finally:
        for s in (A, B):
            for p in glob.glob(os.path.join(SONGS, f"*{s}*")):
                try:
                    os.remove(p)
                except OSError:
                    import shutil as _sh
                    _sh.rmtree(p, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
