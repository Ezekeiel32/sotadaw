#!/usr/bin/env python3
"""CHRONICLE BACKFILL — give every project its PAST, once.

THE CHRONICLE went live 2026-07-09; everything before it lives only in
telemetry (telemetry/asks.jsonl = every typed ask; telemetry/proposals.jsonl =
every verdict WITH the prompt that made the take). This one-shot migration
folds that history into songs/.chat/<song>.jsonl so the agent's CONVERSATION
MEMORY and the UI replay reach back before the ship.

LAWS:
  - Law-1 faithful: only deterministic telemetry rows are folded (asks,
    verdicts, verdict-attached prompts) — nothing is invented.
  - MERGE-SAFE: only rows STRICTLY OLDER than the song's earliest existing
    chronicle row are inserted (live rows are never reordered or duplicated).
  - IDEMPOTENT: a song whose chronicle already carries a backfill:true row is
    skipped outright; running twice adds nothing.
  - Scratch never enters: songs starting with '_' and songs whose .json no
    longer exists are skipped.

Usage: tools/chronicle_backfill.py [--dry-run]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import chronicle  # noqa: E402


def read_jsonl(path):
    out = []
    try:
        with open(path) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError:
        pass
    return out


def main():
    dry = "--dry-run" in sys.argv
    asks = read_jsonl(os.path.join(ROOT, "telemetry", "asks.jsonl"))
    props = read_jsonl(os.path.join(ROOT, "telemetry", "proposals.jsonl"))
    by_song = {}
    for a in asks:
        s = str(a.get("song", ""))
        if s and a.get("text"):
            by_song.setdefault(s, []).append(
                {"t": float(a.get("t", 0)), "role": "user",
                 "text": str(a["text"]), "backfill": True})
    for p in props:
        s = str(p.get("song", ""))
        if not s:
            continue
        t = float(p.get("t", 0))
        rows = by_song.setdefault(s, [])
        prompt = str(p.get("prompt", "") or "")
        # the verdict knows its ask: synth the user row if asks.jsonl (younger
        # than proposals.jsonl) never logged it — text-dedupe keeps it honest
        if prompt and not any(r["role"] == "user" and r["text"] == prompt[:300]
                              for r in rows):
            rows.append({"t": t - 1.0, "role": "user", "text": prompt[:300],
                         "backfill": True})
        rows.append({"t": t, "role": "verdict", "text": str(p.get("note", "") or ""),
                     "verdict": "accept" if p.get("accepted") else "reject",
                     "backfill": True})
    total_songs, total_rows = 0, 0
    for song, rows in sorted(by_song.items()):
        if song.startswith("_") or not os.path.exists(
                os.path.join(ROOT, "songs", f"{song}.json")):
            continue
        existing = chronicle.read(song)
        if any(r.get("backfill") for r in existing):
            continue                                   # idempotency: once only
        cutoff = min((float(r.get("t", 0)) for r in existing), default=float("inf"))
        add = sorted((r for r in rows if r["t"] < cutoff), key=lambda r: r["t"])
        if not add:
            continue
        total_songs += 1
        total_rows += len(add)
        print(f"  {song}: +{len(add)} rows "
              f"({sum(1 for r in add if r['role'] == 'user')} asks, "
              f"{sum(1 for r in add if r['role'] == 'verdict')} verdicts)"
              + (" [dry]" if dry else ""))
        if dry:
            continue
        os.makedirs(chronicle.chat_dir(), exist_ok=True)
        path = chronicle._path(song)
        merged = add + existing
        with open(path + ".tmp", "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in merged)
        os.replace(path + ".tmp", path)
    print(f"== CHRONICLE BACKFILL: {total_rows} rows into {total_songs} project(s)"
          + (" (dry run)" if dry else "") + " ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
