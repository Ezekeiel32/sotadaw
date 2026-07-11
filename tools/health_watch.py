#!/usr/bin/env python3
"""THE PASSIVE HEALTH WATCH (W120) — live QA on the user's running session.

Scans the tail of the event stream and classifies what a stand-down tick
needs to know: fresh errors/exceptions, scope-law flags, and the quality
passes doing their job. Zero CPU beyond a file tail; never touches the
session.

    tools/health_watch.py [--window 900] [--lines 120]

Exit 1 when a FRESH error (inside the window) is present — the campaign
tick should investigate; exit 0 otherwise. Found W117 (meter timeout) and
W119 (the 2180 false-flag flood) within minutes of them happening live.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = os.environ.get("SOTADAW_IPC", os.path.join(ROOT, "agent", "ipc"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=float, default=900.0,
                    help="freshness window in seconds (default 15 min)")
    ap.add_argument("--lines", type=int, default=120)
    a = ap.parse_args()
    ev = os.path.join(IPC, "events.jsonl")
    if not os.path.exists(ev):
        print("no event stream (idle box)")
        return 0
    with open(ev, "rb") as f:
        f.seek(max(0, os.path.getsize(ev) - 64 * 1024))
        tail = f.read().decode(errors="replace").splitlines()[-a.lines:]
    now = time.time()
    errs, scope, qual = [], [], []
    for line in tail:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        age = now - float(e.get("t", 0))
        fresh = age < a.window
        k, txt = e.get("kind", ""), str(e.get("text", ""))[:150]
        if (k == "error" or "exception" in txt.lower()
                or "Traceback" in txt) and fresh:
            errs.append(f"[{age:.0f}s] {txt or k}")
        if "OUT OF SCOPE" in txt and fresh:
            scope.append(f"[{age:.0f}s] {txt}")
        if fresh and ("loudness recovery" in txt or "WORLD-CLASS" in txt
                      or "measured ceiling" in txt or k == "quality"):
            if k == "quality":
                hard = e.get("hard") or []
                qual.append(f"[{age:.0f}s] world-class: "
                            + ("PASS" if e.get("world_class") or not hard
                               else "FIX " + "; ".join(map(str, hard))[:90]))
            else:
                qual.append(f"[{age:.0f}s] {txt}")
    print("fresh errors:", "NONE" if not errs else "")
    for x in errs[-4:]:
        print("  !!", x)
    print("scope flags:", "NONE" if not scope else "")
    for x in scope[-2:]:
        print("  --", x)
    print(f"quality passes: {len(qual)}")
    for x in qual[-3:]:
        print("  ok", x)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
