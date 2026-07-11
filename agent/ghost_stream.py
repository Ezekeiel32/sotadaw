#!/usr/bin/env python3
"""GHOST STREAM AT TOKEN RESOLUTION (pass 5) — notes land on the canvas WHILE
THE MODEL IS STILL TYPING THE TOOL CALL.

The file-watch ghost stream (sidecar _watch_prop) draws the proposal growing
per TOOL EXECUTION: the model finishes generating update_track(...), the MCP
server runs it, the file changes, the watcher snapshots. On a big compose call
that is 10-60s of "composing…" silence before anything appears. But with
--include-partial-messages the CLI forwards the API's input_json_delta chunks
— the tool call's JSON as it is BORN. This kernel tolerantly extracts complete
note objects from that partial JSON and merges them into the ghost snapshot,
so the canvas draws each note roughly when the model conceives it.

LAWS:
- PREVIEW ONLY: the overlay writes the .ghost.json snapshot the UI reads —
  never the proposal file, never anything applied. Execution still buffers the
  FULL tool input (the industry partial-JSON trap: parse-to-preview is fine,
  parse-to-execute is a production bug).
- Tolerant, never wrong: only individually json.loads-able flat note objects
  ship; a mid-token note simply waits for the next delta.
- The file watcher and this overlay both atomic-replace the same ghost path;
  last writer wins and both are valid views (the watcher's is the executed
  truth, ours adds the in-flight tail). Merge dedups notes already landed.

Battery: tools/ghost_stream_battery.py (pure, no processes).
"""
import json
import os
import re

MAX_ACCUM = 2_000_000          # per-block partial-json cap (runaway guard)
MAX_NOTES = 6000               # overlay note cap per merge (pathology guard)

# tool names as the stream sees them (MCP-mounted names carry the mcp__daw__ prefix).
# surgical_edit rides too: its insert/replace ops carry LITERAL note objects and the
# scalpel is the compose workhorse — without it, scalpel takes only paint post-execution.
_NOTE_TOOLS = ("update_track", "write_song", "add_track", "surgical_edit")


def tool_kind(name):
    """the short tool name for note-bearing tools, else None."""
    short = str(name or "").split("__")[-1]
    return short if short in _NOTE_TOOLS else None


class ToolStream:
    """Per-message accumulator for streaming tool_use blocks (index-keyed)."""

    def __init__(self):
        self.blocks = {}

    def start(self, index, name):
        self.blocks[index] = {"name": str(name or ""), "json": [], "n": 0}

    def delta(self, index, partial):
        b = self.blocks.get(index)
        if b is None or b["n"] >= MAX_ACCUM:
            return
        s = str(partial or "")
        b["json"].append(s)
        b["n"] += len(s)

    def snapshot(self, index):
        """-> (tool_name, accumulated_json_str) or (None, '')."""
        b = self.blocks.get(index)
        if b is None:
            return None, ""
        return b["name"], "".join(b["json"])

    def stop(self, index):
        self.blocks.pop(index, None)

    def reset(self):
        self.blocks.clear()


def _scan_flat_objects(s, start):
    """Complete flat {...} objects inside an array starting at s[start]=='['.
    Stops at the array's closing ']' if present. Note objects are flat numeric
    dicts by schema — any nested brace aborts that object (never guess)."""
    out, i, n = [], start + 1, len(s)
    while i < n:
        c = s[i]
        if c == "]":
            break
        if c == "{":
            j = s.find("}", i + 1)
            if j == -1:
                break                      # mid-stream object: wait for more deltas
            frag = s[i:j + 1]
            if "{" in frag[1:]:
                break                      # nested = not a note; abort the scan
            try:
                o = json.loads(frag)
                if isinstance(o, dict) and "start" in o and "pitch" in o:
                    out.append(o)
            except json.JSONDecodeError:
                pass
            i = j + 1
        else:
            i += 1
    return out


def _str_field(s, key):
    m = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)"' % re.escape(key), s)
    return json.loads('"' + m.group(1) + '"') if m else None


def extract_notes(tool_name, partial_json):
    """Best-effort note extraction from a PARTIAL tool_use input JSON.
    -> {"song": str|None, "tracks": [{"track": name, "notes": [...],
        "source": dict|None}]}  (source only for add_track). Never raises."""
    kind = tool_kind(tool_name)
    s = str(partial_json or "")
    out = {"song": _str_field(s, "song"), "tracks": []}
    if not kind or not s:
        return out
    try:
        if kind in ("update_track", "add_track"):
            tname = _str_field(s, "track" if kind == "update_track" else "name")
            m = re.search(r'"notes"\s*:\s*\[', s)
            if tname and m:
                notes = _scan_flat_objects(s, m.end() - 1)
                if notes:
                    t = {"track": tname, "notes": notes, "source": None}
                    if kind == "add_track":
                        sm = re.search(r'"source"\s*:\s*(\{[^{}]*\})', s)
                        if sm:
                            try:
                                t["source"] = json.loads(sm.group(1))
                            except json.JSONDecodeError:
                                pass
                    out["tracks"].append(t)
        elif kind == "surgical_edit":
            # the scalpel: selector {"tracks": "<name>"} routes; insert/replace ops
            # carry notes arrays — collect them ALL (multi-op calls). List-form
            # selectors are skipped (no single home for the notes = never guess).
            tname = _str_field(s, "tracks") or _str_field(s, "track")
            if tname:
                notes = []
                for m in re.finditer(r'"notes"\s*:\s*\[', s):
                    notes.extend(_scan_flat_objects(s, m.end() - 1))
                if notes:
                    out["tracks"].append({"track": tname, "notes": notes,
                                          "source": None})
        elif kind == "write_song":
            # sequential scan: each "name":"X" whose SAME segment (before the
            # next "name") opens a notes array contributes that array's notes
            parts = re.split(r'"name"\s*:\s*', s)
            for seg in parts[1:]:
                nm = re.match(r'"((?:[^"\\]|\\.)*)"', seg)
                if not nm:
                    continue
                m = re.search(r'"notes"\s*:\s*\[', seg)
                if not m:
                    continue
                notes = _scan_flat_objects(seg, m.end() - 1)
                if notes:
                    out["tracks"].append({"track": json.loads('"' + nm.group(1) + '"'),
                                          "notes": notes, "source": None})
    except Exception:
        pass
    return out


def _note_key(n):
    try:
        return (round(float(n.get("start", 0)), 4), int(n.get("pitch", 0)),
                round(float(n.get("len", 0)), 4))
    except Exception:
        return None


def merge_overlay(prop_path, ghost_path, extractions, prop_name=None):
    """Merge streamed note extractions into the ghost snapshot: read the
    proposal file (executed truth), append in-flight notes not yet present,
    atomic-replace ghost. add_track extractions may BIRTH a ghost track (the
    UI materializes added lanes). Returns notes added (0 = no write).
    Extractions naming a different song than prop_name are ignored (loop-lab
    and cross-song calls must never paint this canvas)."""
    try:
        with open(prop_path) as f:
            doc = json.load(f)
    except Exception:
        return 0
    added = 0
    by_name = {t.get("name"): t for t in doc.get("tracks", [])}
    for ex in extractions:
        if prop_name and ex.get("song") and ex["song"] != prop_name:
            continue
        for te in ex.get("tracks", []):
            tr = by_name.get(te["track"])
            if tr is None:
                if te.get("source") is None:
                    continue               # update to an unknown track: skip
                tr = {"name": te["track"], "source": te["source"],
                      "gainDb": 0.0, "notes": []}
                doc.setdefault("tracks", []).append(tr)
                by_name[te["track"]] = tr
            have = {_note_key(n) for n in tr.get("notes", [])}
            room = MAX_NOTES - len(tr.get("notes", []))
            for n in te["notes"]:
                k = _note_key(n)
                if k is None or k in have or room <= 0:
                    continue
                tr.setdefault("notes", []).append(n)
                have.add(k)
                room -= 1
                added += 1
    if not added:
        return 0
    tmp = ghost_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f)
    os.replace(tmp, ghost_path)
    return added
