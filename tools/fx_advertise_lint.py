#!/usr/bin/env python3
"""fx_advertise_lint.py — every usable Faust fx must be advertised to the agent.

A compiled fx_* is in list_instruments() (so set_track_fx ACCEPTS it) — but if it
isn't NAMED in set_track_fx's description, the agent never knows it exists: usable
yet undiscoverable (fx_ms_eq / fx_multiband / fx_softclip were hidden this way).
This guardian keeps the description in sync with the compiled fx set. Exit code IS
the verdict (0 = all advertised, 1 = something hidden).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))


def main():
    import daw_mcp
    avail = sorted(i for i in daw_mcp.list_instruments() if i.startswith("fx_"))
    desc = daw_mcp.TOOLS["set_track_fx"][1]
    hidden = [f for f in avail if f not in desc]
    print(f"== FX ADVERTISE LINT == {len(avail)} usable fx, "
          f"{len(avail) - len(hidden)} advertised")
    if hidden:
        print("  HIDDEN (usable but undiscoverable — add to set_track_fx desc):", hidden)
        print("REGRESSION")
        return 1
    print("PASS — every usable Faust fx is advertised to the agent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
