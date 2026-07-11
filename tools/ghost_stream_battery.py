#!/usr/bin/env python3
"""ghost_stream_battery.py — proof of TOKEN-RESOLUTION GHOSTS + LIVE TYPING
(pass 5). Pure: no claude, no engine — the extractor/merge kernel is exercised
directly and StreamState is fed synthetic stream_event lines through an
ISOLATED SOTADAW_IPC (events land in a temp events.jsonl, never the live one).

Exit 0 = all green.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))

TMP = tempfile.mkdtemp(prefix="ghoststream_")
os.environ["SOTADAW_IPC"] = TMP                 # isolation BEFORE sidecar import
import ghost_stream  # noqa: E402
import sidecar  # noqa: E402

fails = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"{tag} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)


N1 = '{"start": 0.0, "len": 0.5, "pitch": 36, "vel": 0.9}'
N2 = '{"start": 1.0, "len": 0.25, "pitch": 42, "vel": 0.6}'
N3 = '{"start": 2.0, "len": 0.5, "pitch": 38, "vel": 0.8}'

# 1: complete update_track
ex = ghost_stream.extract_notes(
    "mcp__daw__update_track",
    f'{{"song": "_prop_x", "track": "hats", "notes": [{N1}, {N2}]}}')
check("update_track complete: 2 notes on 'hats'",
      ex["song"] == "_prop_x" and len(ex["tracks"]) == 1
      and ex["tracks"][0]["track"] == "hats" and len(ex["tracks"][0]["notes"]) == 2)

# 2: cut MID-NOTE — only the complete one ships
ex = ghost_stream.extract_notes(
    "update_track", f'{{"track": "kick", "notes": [{N1}, {{"start": 1.0, "le')
check("mid-note cut: 1 complete note only",
      len(ex["tracks"]) == 1 and len(ex["tracks"][0]["notes"]) == 1
      and ex["tracks"][0]["notes"][0]["pitch"] == 36)

# 3: note split ACROSS deltas via ToolStream accumulation
ts = ghost_stream.ToolStream()
ts.start(1, "update_track")
whole = f'{{"track": "bass", "notes": [{N1}, {N2}, {N3}]}}'
a, b = whole[:len(whole) // 2], whole[len(whole) // 2:]
ts.delta(1, a)
name, acc = ts.snapshot(1)
n_half = len(ghost_stream.extract_notes(name, acc)["tracks"][0]["notes"]) \
    if ghost_stream.extract_notes(name, acc)["tracks"] else 0
ts.delta(1, b)
name, acc = ts.snapshot(1)
ex = ghost_stream.extract_notes(name, acc)
check("split across deltas: half<3 then all 3",
      n_half < 3 and len(ex["tracks"][0]["notes"]) == 3, f"half={n_half}")

# 4: escaped track name
ex = ghost_stream.extract_notes("update_track",
                                f'{{"track": "ha\\"ts", "notes": [{N1}]}}')
check("escaped track name unescapes", ex["tracks"][0]["track"] == 'ha"ts')

# 5: write_song — 2 note tracks + a sections list with names (no phantoms)
doc = ('{"song": "_prop_x", "doc": {"sections": [{"name": "intro", "startBar": 0},'
       f' {{"name": "drop", "startBar": 8}}], "tracks": [{{"name": "kick", "notes": [{N1}]}},'
       f' {{"name": "hats", "notes": [{N2}, {N3}]}}')
ex = ghost_stream.extract_notes("write_song", doc)
names = [t["track"] for t in ex["tracks"]]
check("write_song: exactly the 2 note tracks",
      names == ["kick", "hats"] and len(ex["tracks"][1]["notes"]) == 2, str(names))

# 6: add_track with source
ex = ghost_stream.extract_notes(
    "mcp__daw__add_track",
    f'{{"song": "_prop_x", "name": "lead", "source": {{"kind": "faust", "id": "saw_lead"}}, "notes": [{N1}]}}')
check("add_track: source + notes",
      ex["tracks"] and ex["tracks"][0]["source"] == {"kind": "faust", "id": "saw_lead"}
      and len(ex["tracks"][0]["notes"]) == 1)

# 6b: surgical_edit insert — selector routes, op notes stream (the scalpel composes)
ex = ghost_stream.extract_notes(
    "mcp__daw__surgical_edit",
    f'{{"song": "_prop_x", "selector": {{"tracks": "keys"}}, "ops": [{{"op": "insert", "notes": [{N1}, {N2}]}}]}}')
check("surgical_edit insert: 2 notes on 'keys'",
      len(ex["tracks"]) == 1 and ex["tracks"][0]["track"] == "keys"
      and len(ex["tracks"][0]["notes"]) == 2 and ex["tracks"][0]["source"] is None)

# 6c: surgical_edit multi-op — every op's notes array collected
ex = ghost_stream.extract_notes(
    "surgical_edit",
    f'{{"selector": {{"tracks": "bass"}}, "ops": [{{"op": "insert", "notes": [{N1}]}},'
    f' {{"op": "replace", "notes": [{N2}, {N3}]}}]}}')
check("surgical_edit multi-op: 3 notes total",
      ex["tracks"] and len(ex["tracks"][0]["notes"]) == 3)

# 6d: list-form selector = no single home -> never guess, no extraction
ex = ghost_stream.extract_notes(
    "surgical_edit", f'{{"selector": {{"tracks": ["a", "b"]}}, "ops": [{{"op": "insert", "notes": [{N1}]}}]}}')
check("surgical_edit list selector: skipped (never guess)", ex["tracks"] == [])

# 6e: surgical_edit cut mid-note — only the complete note ships
ex = ghost_stream.extract_notes(
    "surgical_edit", f'{{"selector": {{"tracks": "keys"}}, "ops": [{{"op": "insert", "notes": [{N1}, {{"start": 4.0, "pi')
check("surgical_edit mid-note cut: 1 complete note",
      ex["tracks"] and len(ex["tracks"][0]["notes"]) == 1)

# 7: nested brace in the notes region aborts cleanly
ex = ghost_stream.extract_notes(
    "update_track", '{"track": "x", "notes": [{"start": 0, "weird": {"a": 1}}, ' + N1 + ']}')
check("nested-brace note: no crash, no garbage",
      isinstance(ex["tracks"], list)
      and all("weird" not in n for t in ex["tracks"] for n in t["notes"]))

# 8/9: tool_kind gates
check("tool_kind gates non-note tools",
      ghost_stream.tool_kind("mcp__daw__set_track_fx") is None
      and ghost_stream.tool_kind("mcp__daw__update_track") == "update_track"
      and ghost_stream.tool_kind("write_song") == "write_song")

# 10: garbage never raises
for junk in ("", None, "{{{", '"notes": ['):
    ghost_stream.extract_notes("update_track", junk)
check("garbage partials never raise", True)

# ---- merge_overlay ----
prop = os.path.join(TMP, "_prop_t.json")
ghost = os.path.join(TMP, "_prop_t.ghost.json")
base_doc = {"bpm": 120, "lengthBars": 4,
            "tracks": [{"name": "hats", "source": {"kind": "faust", "id": "hat_metal"},
                        "notes": [json.loads(N1)]}]}
json.dump(base_doc, open(prop, "w"))

# 11: merge streamed notes into existing track
exts = [ghost_stream.extract_notes(
    "update_track", f'{{"song": "_prop_t", "track": "hats", "notes": [{N1}, {N2}]}}')]
added = ghost_stream.merge_overlay(prop, ghost, exts, prop_name="_prop_t")
g = json.load(open(ghost))
check("merge: 1 new note (N1 deduped), ghost valid",
      added == 1 and len(g["tracks"][0]["notes"]) == 2, f"added={added}")

# 12: all-dup merge = 0 and no write
os.remove(ghost)
added = ghost_stream.merge_overlay(
    prop, ghost,
    [ghost_stream.extract_notes("update_track", f'{{"track": "hats", "notes": [{N1}]}}')],
    prop_name="_prop_t")
check("all-dup merge: added=0, no ghost write",
      added == 0 and not os.path.exists(ghost))

# 13: add_track births a ghost lane
exts = [ghost_stream.extract_notes(
    "add_track",
    f'{{"song": "_prop_t", "name": "lead", "source": {{"kind": "faust", "id": "saw_lead"}}, "notes": [{N3}]}}')]
added = ghost_stream.merge_overlay(prop, ghost, exts, prop_name="_prop_t")
g = json.load(open(ghost))
check("add_track births ghost lane",
      added == 1 and any(t["name"] == "lead" and t["notes"] for t in g["tracks"]))

# 14: unknown track (no source) skipped
added = ghost_stream.merge_overlay(
    prop, ghost,
    [ghost_stream.extract_notes("update_track", f'{{"track": "nope", "notes": [{N2}]}}')],
    prop_name="_prop_t")
check("update to unknown track skipped", added == 0)

# 15: song mismatch ignored
added = ghost_stream.merge_overlay(
    prop, ghost,
    [ghost_stream.extract_notes(
        "update_track", f'{{"song": "_loop_1", "track": "hats", "notes": [{N3}]}}')],
    prop_name="_prop_t")
check("cross-song extraction ignored", added == 0)

# ---- StreamState through synthetic stream_event lines ----
sidecar.StreamState.TEXT_EVERY = 0.0
sidecar.StreamState.TEXT_MIN_CHARS = 1
sidecar.StreamState.GHOST_EVERY = 0.0
sidecar.SONGS = TMP                   # the isolated songs dir for this rig
stt = sidecar.StreamState("rq1", "agent", "t")


def sev(e):
    stt.on_stream_event({"type": "stream_event", "event": e})


sev({"type": "message_start"})
sev({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})
sev({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Adding a "}})
sev({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "hat groove now."}})
sev({"type": "content_block_stop", "index": 0})
sev({"type": "content_block_start", "index": 1,
     "content_block": {"type": "tool_use", "name": "mcp__daw__update_track", "id": "tu1"}})
half = f'{{"song": "_prop_t", "track": "hats", "notes": [{N3}, '
sev({"type": "content_block_delta", "index": 1,
     "delta": {"type": "input_json_delta", "partial_json": half}})
sev({"type": "content_block_delta", "index": 1,
     "delta": {"type": "input_json_delta", "partial_json": N2 + "]}"}})
sev({"type": "content_block_stop", "index": 1})

evl = os.path.join(TMP, "events.jsonl")
lines = [json.loads(x) for x in open(evl)] if os.path.exists(evl) else []
streams = [e for e in lines if e.get("kind") == "activity_stream"]
progress = [e for e in lines if e.get("kind") == "proposal_progress"]
check("StreamState: activity_stream events grow the text",
      len(streams) >= 2 and streams[-1]["text"] == "Adding a hat groove now."
      and streams[0]["text"] != streams[-1]["text"],
      f"n={len(streams)}")
check("StreamState: proposal_progress fired for token ghosts", len(progress) >= 1)
g = json.load(open(ghost))
hat_notes = next(t["notes"] for t in g["tracks"] if t["name"] == "hats")
check("StreamState: ghost carries the streamed notes",
      {36, 42, 38} <= {n["pitch"] for n in hat_notes},
      str(sorted(n["pitch"] for n in hat_notes)))

# 19: kill-switch honored at spawn level (flag helper)
os.environ["SOTADAW_TOKEN_STREAM"] = "0"
off = not sidecar.token_stream_on()
os.environ.pop("SOTADAW_TOKEN_STREAM")
check("kill-switch: SOTADAW_TOKEN_STREAM=0 turns the lane off",
      off and sidecar.token_stream_on())

print(f"\nGHOST STREAM BATTERY: {'ALL GREEN' if not fails else str(len(fails)) + ' FAIL(S): ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
