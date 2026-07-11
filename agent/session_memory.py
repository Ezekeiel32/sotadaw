#!/usr/bin/env python3
"""THE SESSION FACT STORE (T2, ZPE_TRANSFER_ROADMAP §5) — v17-shape memory.

Entity-key + DISCRETE relation tag + HARD-overwrite revision + honest miss,
implemented symbolically (jsonl): the DAW is symbolic — it needs the measured
discipline, not the neural heads. This is the organ the constitution names as
missing ("recent-edit digest ✗") and the healer of verified finding B: model
routing fragments resident memory, so "do that to the snare too" lands on a
process with zero context. A RECALL block rebuilt from disk into EVERY prompt
makes continuity model- and process-independent.

THE TWO WRITE LAWS (measured, ZPE rungs 1-8):
  LAW 1 — facts are written ONLY from deterministic events: accept/reject
  verdicts, filed receipts, locate-resolutions an accepted edit confirmed, and
  explicit user words. NEVER from model free text; an LLM sentence is not
  evidence. (This kernel cannot enforce the caller's oath — S2's hooks live
  only at those event sites.)
  LAW 2 — same (entity, rel) = HARD overwrite; the old value rides the new row
  as a tombstone. No fuzzy merge, no similarity thresholds: soft matching at
  overwrite time is the measured 0.9875 -> 0.8500 revision crash.

Store shape: one file per song under songs/.memory/ (gitignored, never
uplinked), append-only jsonl, LAST WRITE WINS per (entity, rel) at read time —
the tombstones ARE the audit trail. `SOTADAW_IPC` set = the store namespaces
under that dir instead (the isolation recipe: test rigs cannot pollute live
memory). `_project` is the cross-song namespace for explicit preferences only.

rel enum v1 (discrete tags = damage isolation, ZPE Track 5):
  refers_to   "squelchy one" -> track "reese"   (established by a CONFIRMED edit)
  alias       "the drop" -> {"bars": [32, 48]}  (locate confirmations)
  prefers     "crash cymbals" -> "avoid" wording lives in `avoid`; taste kept
  avoid       "no crash cymbals" (reject notes / explicit words)
  sweet_spot  "lead.fx_filter.cutoff" -> 780    (from an ACCEPTED take's receipt)
  last_edit   track -> ring of the last 3 receipt summaries (the digest, literally)

Deps: stdlib only. Battery: tools/session_memory_battery.py.
"""
import json, os, re, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELS = ("refers_to", "alias", "prefers", "avoid", "sweet_spot", "last_edit",
        "last_plan")   # last_plan: the parse lane's re-executable last hit
                       # (entity "_session"; written by the sidecar at HIT time —
                       # a compiler event, Law-1 lawful; hidden from RECALL)
PROJECT = "_project"
LAST_EDIT_KEEP = 3
RECALL_CAP = 8


def memory_dir():
    """Live default songs/.memory; SOTADAW_IPC override = isolated instance."""
    ipc = os.environ.get("SOTADAW_IPC")
    return os.path.join(ipc, "memory") if ipc else os.path.join(ROOT, "songs", ".memory")


def _path(song):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(song).strip()) or "_unnamed"
    return os.path.join(memory_dir(), f"{safe}.jsonl")


def read_facts(song):
    """Fold the jsonl: LAST WRITE WINS per (entity, rel); `gone` rows delete.
    -> {(entity, rel): row}. Garbage lines are skipped, never fatal."""
    out = {}
    try:
        with open(_path(song)) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                k = (str(row.get("entity", "")), str(row.get("rel", "")))
                if not k[0] or k[1] not in RELS:
                    continue
                if row.get("gone"):
                    out.pop(k, None)
                else:
                    out[k] = row
    except FileNotFoundError:
        pass
    return out


def write_fact(song, entity, rel, value, prov="", t=None, gone=False):
    """LAW 2 lives here: same (entity, rel) = hard overwrite, old value
    tombstoned onto the new row as `replaced`. Returns the written row.
    LAW 1 is the caller's oath — call this ONLY from deterministic events."""
    if rel not in RELS:
        raise ValueError(f"unknown rel '{rel}' (enum: {', '.join(RELS)})")
    entity = str(entity).strip()
    if not entity:
        raise ValueError("empty entity")
    json.dumps(value)                       # values must be plain data, fail loud
    row = {"entity": entity, "rel": rel, "value": value,
           "prov": str(prov)[:200],
           "t": round(float(time.time() if t is None else t), 2)}
    if gone:
        row["gone"] = True
    else:
        old = read_facts(song).get((entity, rel))
        if old is not None and old.get("value") != value:
            row["replaced"] = {"value": old["value"], "t": old["t"]}
    os.makedirs(memory_dir(), exist_ok=True)
    with open(_path(song), "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def retract(song, entity, rel, prov="", t=None):
    """Hard delete (a `gone` tombstone) — wrong facts die, they don't decay."""
    return write_fact(song, entity, rel, None, prov=prov, t=t, gone=True)


def remember_edit(song, track, summary, t=None):
    """The recent-edit digest: per-track ring of the last LAST_EDIT_KEEP receipt
    summaries, newest first. The ring itself hard-overwrites (LAW 2)."""
    cur = read_facts(song).get((str(track).strip(), "last_edit"))
    ring = [str(summary)[:160]]
    if cur and isinstance(cur.get("value"), list):
        ring += [str(v) for v in cur["value"]][:LAST_EDIT_KEEP - 1]
    return write_fact(song, track, "last_edit", ring, prov="receipt", t=t)


def alias_facts(song):
    """-> {phrase: track_name} for parse_lane.compile(facts=...): only string-
    valued refers_to/alias facts (bars-dict aliases are the locate lane's)."""
    out = {}
    for (ent, rel), row in read_facts(song).items():
        if rel in ("refers_to", "alias") and isinstance(row.get("value"), str):
            out[ent.lower()] = row["value"]
    return out


def history(song):
    """What the retarget grammar consumes: the last parse HIT's re-executable
    plan (or None). Kept separate from alias_facts — different consumers."""
    row = read_facts(song).get(("_session", "last_plan"))
    return {"last_plan": row.get("value") if row else None}


def confirm_verdict(song, surgical_rep, resolutions=None, prompt="", t=None):
    """T2-S2, the ACCEPT hook (a LAW-1 site): the user's accept is the
    deterministic event that confirms this run's links. Writes last_edit rings
    for the take's touched tracks (digest = the scope report's receipt
    summaries) and refers_to facts for the parse lane's non-trivial
    phrase->track resolutions. Never raises — a memory hiccup must not block
    an accept."""
    try:
        srep = surgical_rep or {}
        digest = "; ".join(srep.get("receipts") or [])[:160] \
            or str(prompt or "accepted take")[:160]
        for tn in (srep.get("touched_tracks") or [])[:8]:
            remember_edit(song, tn, digest, t=t)
        for phrase, track in (resolutions or {}).items():
            write_fact(song, str(phrase), "refers_to", str(track),
                       prov=f"accepted: {str(prompt)[:60]}", t=t)
        return True
    except Exception:
        return False


def avoid_from_reject(song, why, t=None):
    """T2 REJECT hook (pass 5, a LAW-1 site): the user's reject WHY is
    deterministic evidence of taste. Entity = the SAME complaint bucket the KG
    ingests (one kernel: tools/kg_ingest_telemetry.complaint_bucket), value =
    the verbatim words — LAW 2 keeps the newest per bucket, so RECALL carries
    the standing objection ("busy [avoid] -> 'too many hats'") long after the
    30-min feedback window closes. Empty why = no fact. Never raises."""
    try:
        why = str(why or "").strip()
        if not why:
            return False
        import sys as _sys
        _tools = os.path.join(ROOT, "tools")
        if _tools not in _sys.path:
            _sys.path.insert(0, _tools)
        from kg_ingest_telemetry import complaint_bucket
        b = complaint_bucket(why)
        if not b:
            return False
        write_fact(song, b, "avoid", why[:160], prov="reject verdict", t=t)
        return True
    except Exception:
        return False


def _age(secs):
    secs = max(0.0, float(secs))
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)}m"
    if secs < 86400:
        return f"{int(secs // 3600)}h"
    return f"{int(secs // 86400)}d"


def recall_block(song, cap=RECALL_CAP, now=None):
    """The <=cap-line RECALL block for the prompt: newest-confirmed first, every
    line carries provenance age. NO facts -> empty string (honest miss — the
    block is OMITTED, never a filler line). Project prefs ride the tail."""
    now = time.time() if now is None else float(now)
    proj = []
    if song != PROJECT:                      # project prefs get RESERVED tail slots
        proj = sorted((r for r in read_facts(PROJECT).values()
                       if r.get("rel") != "last_plan"),
                      key=lambda r: -float(r.get("t", 0)))[:2]
    rows = sorted((r for r in read_facts(song).values()
                   if r.get("rel") != "last_plan"),   # machinery, not a user fact
                  key=lambda r: -float(r.get("t", 0)))[:max(0, cap - len(proj))]
    rows += proj
    if not rows:
        return ""
    lines = ["RECALL (this project's established facts — newest confirmed first):"]
    for r in rows:
        v = r["value"]
        vs = v if isinstance(v, str) else json.dumps(v)
        age = _age(now - float(r.get("t", now)))
        age = age if age == "just now" else age + " ago"
        lines.append(f"- {r['entity']} [{r['rel']}] -> {vs[:90]} "
                     f"({age}; {r.get('prov') or 'event'})")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: session_memory.py <song> [entity rel value [prov]]")
        sys.exit(2)
    if len(sys.argv) >= 5:
        print(json.dumps(write_fact(sys.argv[1], sys.argv[2], sys.argv[3],
                                    sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "cli")))
    print(recall_block(sys.argv[1]) or "(no facts)")
