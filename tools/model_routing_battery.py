#!/usr/bin/env python3
"""Zero-token checks for selector -> sidecar provider routing."""

import json
import os
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(ok, message):
    if not ok:
        raise AssertionError(message)
    print("  PASS", message)


with tempfile.TemporaryDirectory(prefix="sotadaw_model_route_") as td:
    os.environ["SOTADAW_IPC"] = os.path.join(td, "ipc")
    sys.path.insert(0, os.path.join(ROOT, "agent"))
    import codex_agent
    import sidecar

    check(sidecar.provider_kind("codex:gpt-5.6-sol") == "codex"
          and sidecar.provider_kind("claude-sonnet-5") == "claude"
          and sidecar.provider_kind("x-ai/grok-4.3") == "openrouter",
          "namespaced GPT, Claude, and OpenRouter ids choose distinct providers")
    check(sidecar.routed_model_for("make a track", "codex:gpt-5.6-luna")
          == "codex:gpt-5.6-luna",
          "telemetry/provenance records the explicit Codex model")
    check(sidecar.parse_lane_skip_reason("codex:gpt-5.6-sol") == "model_override"
          and sidecar.parse_lane_skip_reason() == "",
          "explicit picks bypass AUTO parse while AUTO keeps its zero-token lane")

    songs = os.path.join(td, "songs")
    os.makedirs(songs)
    with open(os.path.join(songs, "fixture.json"), "w") as fh:
        json.dump({"version": 2, "bpm": 120, "lengthBars": 4, "tracks": []}, fh)
    old_songs, old_run = sidecar.SONGS, codex_agent.run
    sidecar.SONGS = songs
    seen = {}
    def canceled_run(prompt, model, **kwargs):
        seen["model"] = model
        with open(os.path.join(songs, "_loop_1.json"), "w") as fh:
            json.dump({"version": 2, "bpm": 120, "lengthBars": 2,
                       "tracks": [{"name": "partial", "notes": []}]}, fh)
        return {"ok": False, "canceled": True, "final": "", "returncode": -15}
    codex_agent.run = canceled_run
    try:
        loops = sidecar.real_loops(7, "one loop", "fixture", 2, 1,
                                   model="codex:gpt-5.6-sol")
    finally:
        sidecar.SONGS, codex_agent.run = old_songs, old_run
    check(loops is None and seen.get("model") == "codex:gpt-5.6-sol",
          "Loop Lab dispatches the selected GPT through Codex")
    check(not os.path.exists(os.path.join(songs, "_loop_1.json")),
          "Loop Lab Stop is terminal and discards unpublished partial loops")

    def write_doc(path, notes):
        with open(path, "w") as fh:
            json.dump({"version": 2, "bpm": 120, "lengthBars": 4,
                       "tracks": [{"name": "lead", "notes": notes}]}, fh)

    base_path = os.path.join(songs, "state_base.json")
    write_doc(base_path, [])
    base_data = open(base_path, "rb").read()

    # Failed revision: exact pending bytes, ghost, and pre-run receipts return.
    prop = "_prop_restore"
    prop_path = os.path.join(songs, prop + ".json")
    prior_notes = [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}]
    write_doc(prop_path, prior_notes)
    prior_data = open(prop_path, "rb").read()
    sidecar.surgical.clear_receipts(prop)
    sidecar.surgical.append_receipt(prop, {"tool": "prior", "fields": ["track:lead:notes"]})
    prior_receipts = sidecar.surgical.read_receipts(prop)
    write_doc(prop_path, prior_notes + [{"start": 1, "len": 1, "pitch": 62, "vel": 0.8}])
    sidecar.surgical.append_receipt(prop, {"tool": "failed-revision", "fields": ["*"]})
    outcome = sidecar.resolve_failed_codex_take(
        8, prop, prop_path, base_path, True, prior_data, prior_receipts)
    restored_receipts = sidecar.surgical.read_receipts(prop)
    check(outcome == "restored" and open(prop_path, "rb").read() == prior_data
          and open(prop_path.replace(".json", ".ghost.json"), "rb").read() == prior_data
          and [r["tool"] for r in restored_receipts] == ["prior"],
          "failed Codex revision restores pending file, ghost, and receipt scope")

    # Fresh failure with a tiny change: nothing hidden remains to block AUTO.
    prop = "_prop_discard"
    prop_path = os.path.join(songs, prop + ".json")
    write_doc(prop_path, [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}])
    write_doc(prop_path.replace(".json", ".ghost.json"), [])
    sidecar.surgical.clear_receipts(prop)
    sidecar.surgical.append_receipt(prop, {"tool": "tiny", "fields": ["track:lead:notes"]})
    outcome = sidecar.resolve_failed_codex_take(
        9, prop, prop_path, base_path, False, base_data, [])
    check(outcome == "discarded" and not os.path.exists(prop_path)
          and not os.path.exists(prop_path.replace(".json", ".ghost.json"))
          and not sidecar.surgical.read_receipts(prop),
          "fresh insubstantial failure removes prop, ghost, and receipts")

    # Fresh failure after real composition: use the established substantial law.
    prop = "_prop_salvage"
    prop_path = os.path.join(songs, prop + ".json")
    eight = [{"start": i * 0.5, "len": 0.25, "pitch": 60 + i, "vel": 0.8}
             for i in range(8)]
    write_doc(prop_path, eight)
    sidecar.surgical.clear_receipts(prop)
    sidecar.surgical.append_receipt(prop, {"tool": "compose", "track_wild": ["lead"]})
    outcome = sidecar.resolve_failed_codex_take(
        10, prop, prop_path, base_path, False, base_data, [])
    check(outcome == "salvaged" and os.path.exists(prop_path)
          and [r["tool"] for r in sidecar.surgical.read_receipts(prop)] == ["compose"],
          "fresh substantial failure stays as a visible salvage with receipts")

print("MODEL ROUTING BATTERY GREEN")
