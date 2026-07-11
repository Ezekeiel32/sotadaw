#!/usr/bin/env python3
"""PROMPT LINT (I9, docs/IMPROVEMENTS_2026_07_07.md) — the tiered rulebook's proof.

The EDIT lane's slim prompt exists to cut latency, NEVER laws: every
damage-preventer law must appear in BOTH tiers, verbatim enough to bind.
A law string missing from either tier turns this red — the slim book can
never quietly drop a guardrail in a future edit.

Also proves: slim is actually slim (<=55% of full), slim never fires with
arranged/ghost blocks (they are compose-class by construction), and the
full book still carries the compose domains slim drops.

Zero tokens. Exit 0 = green.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
os.environ.setdefault("SOTADAW_IPC", os.path.join(ROOT, "agent", "ipc"))
import sidecar  # noqa: E402

# the damage-preventer canon: each entry is (name, marker string that must bind)
LAWS = [
    ("proposal-copy",   "PROPOSAL COPY"),
    ("tool-bootstrap",  "ONE ToolSearch call"),
    ("daw-tools-only",  "ONLY the daw MCP tools"),
    ("read-law",        "get_song_region"),
    ("selection",       "SELECTION = CONTEXT"),
    ("scalpel",         "surgical_edit"),
    ("receipts",        "receipt"),
    ("out-of-scope",    "OUT OF SCOPE"),
    ("trim-zone",       "'level', NOT 'gain'"),
    ("swing-grid",      "SWING-GRID LAW"),
    ("missing-referent","MISSING REFERENT LAW"),
    ("qualifiers",      "EVERY QUALIFIER IS A HARD CONSTRAINT"),
    ("transpose-notes", "TRANSPOSE MEANS NOTES"),
    ("copy-qualifiers", "COPY OPERATIONS RE-APPLY QUALIFIERS"),
    ("scope-match",     "MATCH THE SCOPE OF THE ASK"),
    ("preview-render",  "max_bars=16"),
    ("remove-scoped",   "remove:true"),
]

# compose-only domains that full must keep and slim must drop (the diet itself)
FULL_ONLY = ["THE VOICE", "THE PERFORMANCE", "THE DJ", "THE CHOP",
             "THE LOOP GENERATOR", "LONG-FORM LAW"]

def main():
    full = sidecar.prompt_rules(False)
    slim = sidecar.prompt_rules(True)
    bad = 0
    for name, marker in LAWS:
        for tier, book in (("full", full), ("slim", slim)):
            if marker not in book:
                print(f"FAIL law '{name}' missing from {tier} ('{marker}')")
                bad += 1
    for dom in FULL_ONLY:
        if dom not in full:
            print(f"FAIL full book lost compose domain '{dom}'")
            bad += 1
        if dom in slim:
            print(f"FAIL slim book still carries compose domain '{dom}' (not slim)")
            bad += 1
    ratio = len(slim) / max(1, len(full))
    if ratio > 0.55:
        print(f"FAIL slim/full = {ratio:.2f} (> 0.55) — the diet dissolved")
        bad += 1
    # interpolation seams: full must carry the taste/ghost hooks, slim must not
    withnotes = sidecar.prompt_rules(False, arranged_note="ARR_X\n", ghost_first="GHOST_X\n",
                                     taste_slim="TASTE_X")
    for hook in ("ARR_X", "GHOST_X", "TASTE_X"):
        if hook not in withnotes:
            print(f"FAIL full book dropped its {hook} interpolation seam")
            bad += 1
    # THE CANONICAL PROMPT (pass 5): the stable book must be byte-identical
    # across asks (or the prefix cache silently misses on every request), carry
    # every law, and never leak task content; volatile blocks must land in the
    # TASK message under canon; the legacy kill-switch shape must stay whole.
    b1, t1 = sidecar.assemble_prompt(True, False, "_prop_a", "songA", "ask one",
                                     "\nFB1\n", "\nPERS1\n", "\nCTX1\n", "\nDIG1\n",
                                     arranged_note="ARR_X\n", ghost_first="GHOST_X\n",
                                     taste_slim="TASTE_X", connector_names=("reaper",))
    b2, t2 = sidecar.assemble_prompt(True, False, "_prop_b", "songB", "another ask",
                                     "", "", "\nCTX2\n", "\nDIG2\n",
                                     connector_names=("reaper",))
    if b1 != b2:
        print("FAIL canon book varies across asks — the prefix cache misses on every request")
        bad += 1
    for name, marker in LAWS:
        if marker not in b1:
            print(f"FAIL law '{name}' missing from the canon BOOK ('{marker}')")
            bad += 1
    for leak in ("ask one", "DIG1", "CTX1", "songA"):
        if leak in b1:
            print(f"FAIL canon book leaks task content ('{leak}')")
            bad += 1
    for vol in ("ARR_X", "GHOST_X", "TASTE_X", "ask one", "FB1", "PERS1", "CTX1", "DIG1"):
        if vol not in t1:
            print(f"FAIL canon task lost its volatile block ('{vol}')")
            bad += 1
    lb, lp = sidecar.assemble_prompt(False, False, "_prop_a", "songA", "ask one",
                                     "", "", "", "", connector_names=("reaper",))
    if lb is not None or "PROPOSAL COPY" not in lp or "ask one" not in lp \
            or "EXTERNAL DAW CONNECTORS" not in lp:
        print("FAIL legacy (SOTADAW_CANON=0) shape broken — the kill-switch must stay whole")
        bad += 1
    if bad:
        print(f"== PROMPT LINT: {bad} FAILURE(S) ==")
        return 1
    print(f"== PROMPT LINT GREEN: {len(LAWS)} laws bind in BOTH tiers + the canon BOOK | "
          f"slim = {len(slim)} chars ({ratio:.0%} of full {len(full)}) | "
          f"canon book {len(b1)} chars stable, task-only ask {len(t2)} chars | "
          f"{len(FULL_ONLY)} compose domains full-only ==")
    return 0

if __name__ == "__main__":
    sys.exit(main())
