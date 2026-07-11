#!/usr/bin/env python3
"""CAPTURE LAW's verb-bus door — keep_jam as a CLI for the zero-token lane.

The kernel lives in agent/daw_mcp.py (t_keep_jam: a kept jam take merges INTO a
song as 'jam:<role>' lanes, beat-offset, receipted — keep_jam_battery 16/16).
This wrapper lets the sidecar's verb bus drive it against a _prop_ copy, so the
merge lands as a normal PROPOSAL: ghosts on the lanes, deck verdict, accept =
the one door. Receipts ride SOTADAW_IPC exactly as the tool files them.

  keep_jam.py <song> <take> [--at-bar N]
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song", help="target song (the verb lane passes the _prop_ copy)")
    ap.add_argument("take", help="the kept jam (songs/jam_<genre>_<n> or any song)")
    ap.add_argument("--at-bar", type=int, default=None,
                    help="landing bar (default: appended after the end, own section)")
    a = ap.parse_args()
    import daw_mcp as D
    args = {"song": a.song, "take": a.take}
    if a.at_bar is not None:
        args["at_bar"] = a.at_bar
    out = D.TOOLS["keep_jam"][0](args)
    print(out)
    return 0 if str(out).startswith("OK:") else 1


if __name__ == "__main__":
    sys.exit(main())
