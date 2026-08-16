#!/usr/bin/env python3
"""THE HANDS-KEEP LAW battery (the two-hands race, 2026-08-02). Pure,
tempdir-isolated. Proves: mint stamp round-trip, base-moved detection,
fail-open on missing stamps, hand-vs-agent receipt discrimination, the
verdict truth table (the disaster case = refuse_empty + base_moved), and
garbage tolerance."""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hands_keep as hk

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def main():
    root = tempfile.mkdtemp(prefix="hands_bat_")
    ipc = os.path.join(root, "ipc")
    os.makedirs(ipc)
    base = os.path.join(root, "song.json")
    open(base, "w").write('{"tracks": [1]}')
    try:
        # mint stamp round-trip + unchanged base
        hk.stamp_mint(ipc, "s", base, now=100.0)
        ok(hk.base_moved(ipc, "s", base) is False,
           "unchanged base after mint -> moved=False")
        # THE RACE: user hand-edits the base mid-run
        open(base, "w").write('{"tracks": [1, 2]}')
        ok(hk.base_moved(ipc, "s", base) is True,
           "hand-edited base -> moved=True")
        # no stamp = unknown (fail open, old runs unaffected)
        ok(hk.base_moved(ipc, "nostamp", base) is None,
           "no mint stamp -> None (fail-open)")
        # missing base file = unknown, never a crash
        ok(hk.base_moved(ipc, "s", os.path.join(root, "gone.json")) is None,
           "missing base -> None, no raise")

        # receipts: hand.* NEVER counts as agent work
        with open(os.path.join(ipc, "receipts.jsonl"), "w") as f:
            f.write(json.dumps({"ts": 1, "song": "_prop_s",
                                "tool": "hand.clip_remove"}) + "\n")
            f.write(json.dumps({"ts": 2, "song": "_prop_other",
                                "tool": "update_track"}) + "\n")
            f.write("garbage line\n")
        ok(hk.agent_receipts(ipc, "_prop_s") == 0,
           "hand receipts + other-prop rows count ZERO agent work")
        with open(os.path.join(ipc, "receipts.jsonl"), "a") as f:
            f.write(json.dumps({"ts": 3, "song": "_prop_s",
                                "tool": "update_track",
                                "fields": ["track:bass:gainDb"]}) + "\n")
        ok(hk.agent_receipts(ipc, "_prop_s") == 1,
           "a real agent receipt counts")
        ok(hk.agent_receipts(ipc, "_prop_s", since_t=10) == 0,
           "since_t windows the ledger")

        # THE DISASTER TRUTH TABLE
        # tonight's exact case: base moved + zero agent receipts
        with open(os.path.join(ipc, "receipts.jsonl"), "w") as f:
            f.write(json.dumps({"ts": 1, "song": "s",
                                "tool": "hand.clip_remove"}) + "\n")
        g = hk.verdict_guard(ipc, "s", base, "_prop_s")
        ok(g["refuse_empty"] and g["base_moved"] is True,
           "DISASTER CASE: refuse the empty accept AND flag hands-keep")
        # healthy accept: agent worked, base untouched since mint
        hk.stamp_mint(ipc, "s", base)
        with open(os.path.join(ipc, "receipts.jsonl"), "a") as f:
            f.write(json.dumps({"ts": 5, "song": "_prop_s",
                                "tool": "write_song"}) + "\n")
        g2 = hk.verdict_guard(ipc, "s", base, "_prop_s")
        ok(not g2["refuse_empty"] and g2["base_moved"] is False,
           "healthy accept: no refusal, no hands-keep needed")
        # agent worked AND user edited: accept proceeds but hands-keep fires
        open(base, "w").write('{"tracks": [1, 2, 3]}')
        g3 = hk.verdict_guard(ipc, "s", base, "_prop_s")
        ok(not g3["refuse_empty"] and g3["base_moved"] is True,
           "both hands worked: accept allowed, hands committed first")

        # clear + garbage mint file tolerated
        hk.clear_mint(ipc, "s")
        ok(hk.base_moved(ipc, "s", base) is None, "clear_mint forgets")
        open(os.path.join(ipc, hk.MINT_FILE), "w").write("not json")
        hk.stamp_mint(ipc, "s", base)
        ok(hk.base_moved(ipc, "s", base) is False,
           "garbage mint file self-heals on next stamp")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print(f"\nhands_keep_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
