#!/usr/bin/env python3
"""WALL LINT — the no-unwalled-proposals law, machine-enforced forever.

Every `render_and_analyze(rid*, <prop>, "proposal")` call in agent/sidecar.py
must be followed by a `clip_wall(` call within the next 6 lines
(loudness_recovery may sit between — the chain still ends at the wall). Exceptions:
  - the call INSIDE clip_wall itself (the wall's own re-render)
  - calls inside loudness_recovery (W116: its lifts re-render mid-chain and
    the caller ALWAYS walls after; its own last lift re-walls when pushed)
  - the call INSIDE _worldclass_floor (the wall's FLOOR leg, 2026-07-11:
    deterministic heal + one re-render; only ever called from clip_wall)
  - the "merged" label (post-ACCEPT cherry re-render: user-approved material,
    already committed — the wall never mutates an accepted base)

Any session adding a new proposal flow without the wall turns the guardian RED.

Usage: python3 tools/wall_lint.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "agent", "sidecar.py")

def main():
    lines = open(SRC).read().splitlines()
    bad = []
    inside_wall = False
    for i, l in enumerate(lines):
        if re.match(r"^def (clip_wall|_worldclass_floor|loudness_recovery)\b", l):
            inside_wall = True
        elif re.match(r"^def \w+", l):
            inside_wall = False
        if 'render_and_analyze(' not in l or '"proposal"' not in l:
            continue
        if inside_wall:
            continue
        window = "\n".join(lines[i:i + 8])
        if "clip_wall(" not in window:
            bad.append((i + 1, l.strip()))
    for n, l in bad:
        print(f"UNWALLED PROPOSAL RENDER at sidecar.py:{n}: {l}")
    n_ok = len([l for l in lines if 'render_and_analyze(' in l and '"proposal"' in l]) - len(bad)
    print(f"wall lint: {n_ok} walled proposal renders, {len(bad)} unwalled "
          f"{'— LAW HOLDS' if not bad else '— LAW BROKEN'}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
