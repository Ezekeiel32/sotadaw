#!/usr/bin/env python3
"""THE HANDS-KEEP LAW (born 2026-08-02, the two-hands race disaster:
"I did manual edits while the agent was working, pressed Accept even though
the agent didn't do any edits, ALL MY MANUAL EDITS GOT DELETED AND NO
HISTORY WAS STORED").

The race: a proposal is MINTED as a copy of the base at run start; the user
keeps editing the BASE with their hands mid-run (legal — no AI/manual wall);
a verdict then replaces the base with the prop — a snapshot of a world from
before their edits. Three guards, all verdict-side, all pure here:

  1. MINT STAMP     — every prop birth stamps the base's sha (ipc/
                      prop_mint.json). Every later comparison has a truth.
  2. BASE MOVED     — at verdict time, base sha != mint sha means the user's
                      hands worked mid-run: the sidecar MUST commit the live
                      base to git BEFORE anything replaces it ("hands kept").
                      History can never again lose manual work.
  3. EMPTY ACCEPT   — zero agent receipts for the prop = the run landed
                      NOTHING (a failed/tool-less run's stale mint). An
                      accept would only overwrite the user's live state with
                      the past. REFUSE it honestly; the user's work stands.

Receipts are the authority on what the agent did (THE RECEIPT LAW) — hand.*
receipts are the user's own edits and never count as agent work.

Pure + stdlib; every path injectable for the battery.
"""
import hashlib
import json
import os
import time

MINT_FILE = "prop_mint.json"


def sha_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _load(ipc):
    p = os.path.join(ipc, MINT_FILE)
    if os.path.exists(p):
        try:
            d = json.load(open(p))
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    return {}


def _save(ipc, d):
    p = os.path.join(ipc, MINT_FILE)
    tmp = p + ".tmp"
    try:
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, p)
    except Exception:
        pass


def stamp_mint(ipc, song, base_path, now=None):
    """Called at EVERY prop birth. Never raises."""
    try:
        d = _load(ipc)
        d[song] = {"sha": sha_file(base_path), "t": now or time.time()}
        _save(ipc, d)
    except Exception:
        pass


def clear_mint(ipc, song):
    try:
        d = _load(ipc)
        if song in d:
            del d[song]
            _save(ipc, d)
    except Exception:
        pass


def base_moved(ipc, song, base_path):
    """True = the user's hands changed the base since the prop was minted.
    None = no stamp (old run / unknown) — callers fail open."""
    st = _load(ipc).get(song)
    if not st or not st.get("sha"):
        return None
    cur = sha_file(base_path)
    if cur is None:
        return None
    return cur != st["sha"]


def agent_receipts(ipc, prop_name, since_t=0.0):
    """Count of AGENT mutating receipts filed for this prop (hand.* excluded
    — those are the user's own edits on the base). since_t=0 spans the
    prop's whole cumulative ledger (proposal-lifetime law)."""
    p = os.path.join(ipc, "receipts.jsonl")
    n = 0
    if not os.path.exists(p):
        return 0
    try:
        for ln in open(p, errors="replace"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("song") != prop_name:
                continue
            if float(r.get("ts", 0)) < since_t:
                continue
            if str(r.get("tool", "")).startswith("hand."):
                continue
            n += 1
    except Exception:
        return 0
    return n


def verdict_guard(ipc, song, base_path, prop_name):
    """The accept-side decision core:
      refuse_empty — zero agent receipts: accepting replaces the user's live
                     state with a stale mint; refuse.
      base_moved   — the user's hands worked mid-run: commit the live base
                     to history BEFORE any replace (the caller runs git).
    """
    moved = base_moved(ipc, song, base_path)
    n = agent_receipts(ipc, prop_name)
    return {"base_moved": bool(moved) if moved is not None else None,
            "agent_receipts": n,
            "refuse_empty": n == 0}
