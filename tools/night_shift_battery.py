#!/usr/bin/env python3
"""THE NIGHT SHIFT battery (A6-T1, docs/SPEC_TRANSCENDENCE.md).

Pure + isolated: fixture root in a tempdir, subprocess jobs injected as
no-ops, the stand-down gate forced off. Proves: the pulse window, the
drafter's trip rules + dedupe + covered-vs-primitive framing, honest empty
reports, the <=2K cap, state accrual across shifts, atomic outputs.
"""
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import night_shift as ns

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def build_root(now):
    root = tempfile.mkdtemp(prefix="night_bat_")
    os.makedirs(os.path.join(root, "telemetry"))
    os.makedirs(os.path.join(root, "agent", "ipc"))
    rows = []
    # in-window: 2 accepts + 4 bright rejects (storm) + 1 groove reject
    for i in range(2):
        rows.append({"t": now - 3600 * (i + 1), "song": f"a{i}",
                     "accepted": True, "note": "", "genre": "goa"})
    for i in range(4):
        rows.append({"t": now - 7200 * (i + 1), "song": f"r{i}",
                     "accepted": False, "note": f"too bright take {i}",
                     "genre": "goa"})
    rows.append({"t": now - 9999, "song": "rg", "accepted": False,
                 "note": "not in the pocket", "genre": "pop"})
    # out-of-window rows must not count
    rows.append({"t": now - 30 * 86400, "song": "old", "accepted": False,
                 "note": "too bright ancient", "genre": "goa"})
    with open(os.path.join(root, "telemetry", "proposals.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return root


def main():
    now = time.time()
    root = build_root(now)
    try:
        p = ns.pulse(root, now)
        ok(p["accepts"] == 2 and p["rejects"] == 5,
           f"pulse windows 7d ({p['accepts']}a/{p['rejects']}r; ancient row "
           "excluded)")
        ok(len(p["buckets"].get("bright", [])) == 4, "WHYs bucket (bright x4)")
        ok(p["genres"]["goa"] == (2, 4), "per-genre rates fold")

        drafts = ns.draft_findings(p, root, now)
        kinds = {(d["kind"], d["subject"]) for d in drafts}
        ok(("bucket_storm", "bright") in kinds,
           "storm trips at >=3 bucket hits")
        ok(("bucket_storm", "groove") not in kinds,
           "1 hit never trips (honest threshold)")
        ok(("accept_collapse", "goa") in kinds,
           "accept-rate collapse trips (2/6 < 0.4)")
        storm = next(d for d in drafts if d["kind"] == "bucket_storm")
        ok("CALIBRATION" in storm["suggestion"],
           "covered bucket framed as calibration, not missing primitive")
        ok("too bright take 0" in storm["evidence"][0],
           "drafts carry the user's words verbatim")
        drafts2 = ns.draft_findings(ns.pulse(root, now), root, now + 60)
        ok(drafts2 == [], "dedupe: same window never re-drafts")
        rows = [json.loads(l) for l in
                open(os.path.join(root, ns.FINDINGS_REL))]
        ok(len(rows) == len(drafts), "findings.jsonl append-only, no dupes")

        # full shift with injected no-op jobs (gate forced off)
        out = ns.run_shift(root, now=now, jobs=[
            ("verdict_ingest", ["true"], 5), ("gold_growth", ["true"], 5)],
            force=True)
        rep = out["report"]
        ok(len(rep) <= 2000, f"report <=2K ({len(rep)})")
        ok("MORNING REPORT" in rep and "bright x4" in rep,
           "report leads with the deltas + complaint spread")
        ok("constitution" in rep, "constitution job reported")
        ok(os.path.exists(os.path.join(root, ns.REPORT_REL)),
           "report written atomically to ipc")
        ok(os.path.exists(os.path.join(root, ns.STATE_REL)), "state persisted")

        # second shift: delta vs prev state + drafts quiet
        out2 = ns.run_shift(root, now=now + 120, jobs=[], force=True)
        ok("since last shift" in out2["report"],
           "second shift reports the delta vs state")
        ok(out2["drafts"] == 0 and "quiet is honest" in out2["report"],
           "no new trips -> honest quiet line")

        # empty root: honest empties, nothing invented
        empty = tempfile.mkdtemp(prefix="night_empty_")
        try:
            os.makedirs(os.path.join(empty, "agent", "ipc"))
            oute = ns.run_shift(empty, now=now, jobs=[], force=True)
            ok("none typed" in oute["report"] and oute["drafts"] == 0,
               "empty tree -> honest empty report")
        finally:
            shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print(f"\nnight_shift_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
