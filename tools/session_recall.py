#!/usr/bin/env python3
"""SESSION RECALL — the read-only `memory` verb (T2-S3): what this project has
established, answered from the session fact store in milliseconds, zero tokens.

  session_recall.py <song>

Prints the human RECALL block + per-track recent-edit rings; a MEMORY_JSON
machine tail rides last (stripped from chat by the verb bus, like DOCTOR_JSON).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import session_memory as sm  # noqa: E402


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--track", default=None)
    a = ap.parse_args()
    song = a.song
    if song.startswith("_prop_"):          # memory belongs to the BASE song
        song = song[len("_prop_"):]
    facts = sm.read_facts(song)
    blk = sm.recall_block(song, cap=12)
    print(blk.rstrip() if blk else
          "no session facts yet — accepted edits and confirmed names land here.")
    rings = {ent: row["value"] for (ent, rel), row in facts.items()
             if rel == "last_edit" and isinstance(row.get("value"), list)
             and (a.track is None or ent == a.track)}
    if a.track and not rings:
        print(f"\nno edits recorded on '{a.track}' yet.")
    if rings:
        print("\nrecent edits (newest first):")
        for ent in sorted(rings):
            for i, s in enumerate(rings[ent]):
                print(f"  {ent if i == 0 else ' ' * len(ent)}  {s}")
    print("MEMORY_JSON " + json.dumps(
        {"song": song, "n_facts": len(facts),
         "facts": [{"entity": e, "rel": r, "value": row.get("value"),
                    "t": row.get("t")} for (e, r), row in
                   sorted(facts.items(), key=lambda kv: -float(kv[1].get("t", 0)))[:24]]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
