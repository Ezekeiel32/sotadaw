#!/usr/bin/env python3
"""THE CHRONICLE — per-project conversation memory (the organ Chezy indicted on
2026-07-09: "the agent has no memory of convs nor no chat history per project").

One jsonl per song, two consumers:
  1. THE PROMPT: conversation_block() distills the project's prior chat into a
     bounded CONVERSATION MEMORY block that rides EVERY cloud prompt — the T2
     RECALL law applied to NARRATIVE (what was asked, what the agent did and
     found, what the user ruled). Continuity becomes model- and process-
     independent: residents recycle on song-switch/budget/staleness and asks
     route across three model lanes; the cold rail forgets everything. Disk is
     the one memory that survives all of it.
  2. THE CHAT: the UI replays the tail of the same file on song open — the
     conversation is PROJECT STATE, not session ephemera.

WRITE LAWS (sibling of session_memory.py, same discipline):
  - rows are written ONLY at deterministic sidecar sites: request consumption
    (user), result events (agent), streamed text blocks (note), consumed
    verdicts (verdict, WHY verbatim), zero-token lane completions (event).
  - append() NEVER raises into a run — a memory hiccup must not cost a take.
  - text is capped AT WRITE (per role) and the file self-trims past TRIM_BYTES
    to its newest half-budget of rows — the chronicle cannot eat the disk.

BLOCK LAWS:
  - honest miss: no rows -> empty string, the block is OMITTED (never filler).
  - newest LAST (closest to the ask), whole rows only, hard char budget; older
    history collapses into one aggregate line (asks/accepts/rejects counted).
  - verdicts decorate the agent line they judged (-> ACCEPTED / -> REJECTED:
    "why" verbatim); `note` rows ride only while no final follows them (the
    in-flight or died run's freshest findings — a final subsumes its notes).

Store: songs/.chat/<song>.jsonl (gitignored, never uplinked). SOTADAW_IPC set
= the store namespaces under that dir (the isolation recipe: test rigs cannot
pollute live memory). Kill switch: SOTADAW_CHRONICLE=0 (no writes, no block).

Deps: stdlib only. Battery: tools/chronicle_battery.py (pure).
E2E: tools/chronicle_e2e.py (mock sidecar through the real protocol seam).
"""
import json, os, re, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = ("user", "agent", "note", "verdict", "event")
WRITE_CAPS = {"user": 700, "agent": 2000, "note": 500, "verdict": 300, "event": 300}
LINE_CAPS = {"user": 240, "agent": 360, "note": 240, "verdict": 200, "event": 160}
TRIM_BYTES = 512 * 1024   # file past this -> trim to newest TRIM_BYTES//2 (hysteresis: no thrash)
BLOCK_CAP = 2400          # hard char budget for the prompt block (prompt-diet law)
BLOCK_NOTES = 3           # max trailing in-flight notes carried into the block
HEADER = ("CONVERSATION MEMORY (this project's chat so far — you are the same "
          "producer continuing it; newest last):")


def enabled():
    return os.environ.get("SOTADAW_CHRONICLE", "1") != "0"


def chat_dir():
    """Live default songs/.chat; SOTADAW_IPC override = isolated instance."""
    ipc = os.environ.get("SOTADAW_IPC")
    return os.path.join(ipc, "chat") if ipc else os.path.join(ROOT, "songs", ".chat")


def _safe(song):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(song).strip()) or "_unnamed"


def active_conv(song):
    """THE CONVERSATIONS LAW (Chezy 2026-07-11): each project owns MANY chats.
    The UI writes songs/.chat/<song>.conv = the id of the OPEN conversation;
    every append/read/block routes to that conversation's own file. Missing,
    empty or "main" = the legacy single file (old projects need no migration)."""
    try:
        with open(os.path.join(chat_dir(), f"{_safe(song)}.conv")) as f:
            cid = f.read().strip()
        return cid if cid and re.fullmatch(r"[A-Za-z0-9_-]{1,48}", cid) else "main"
    except OSError:
        return "main"


def _path(song, conv=None):
    safe = _safe(song)
    cid = conv or active_conv(song)
    return os.path.join(chat_dir(),
                        f"{safe}.jsonl" if cid == "main" else f"{safe}~{cid}.jsonl")


def _clean(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def append(song, role, text, t=None, **extra):
    """File one chronicle row. Returns the row, or None (bad input / disabled /
    IO trouble). NEVER raises — the chronicle is memory, not a gate."""
    try:
        if not enabled() or role not in ROLES:
            return None
        text = _clean(text)[:WRITE_CAPS[role]]
        if not text and role != "verdict":    # accepts legitimately carry no note
            return None
        json.dumps(extra)                     # extras must be plain data
        row = {"t": round(float(time.time() if t is None else t), 2),
               "role": role, "text": text, **extra}
        os.makedirs(chat_dir(), exist_ok=True)
        p = _path(song)
        with open(p, "a") as f:
            f.write(json.dumps(row) + "\n")
        try:                                  # trim law: bounded on-disk footprint
            if os.path.getsize(p) > TRIM_BYTES:
                keep, total = [], 0
                for r in reversed(read(song)):
                    s = json.dumps(r) + "\n"
                    if total + len(s) > TRIM_BYTES // 2:
                        break
                    keep.append(s)
                    total += len(s)
                with open(p + ".tmp", "w") as f:
                    f.writelines(reversed(keep))
                os.replace(p + ".tmp", p)
        except Exception:
            pass
        return row
    except Exception:
        return None


def read(song, limit=None):
    """All parseable rows, file order (oldest first). Garbage lines are
    skipped, never fatal. limit = keep only the newest N."""
    out = []
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
                if isinstance(row, dict) and row.get("role") in ROLES \
                        and (str(row.get("text", "")).strip()
                             or row.get("role") == "verdict"):
                    out.append(row)
    except OSError:
        pass
    return out[-int(limit):] if limit else out


def _age(secs):
    secs = max(0.0, float(secs))
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


def _line(row, now):
    age = _age(now - float(row.get("t", now)))
    text = _clean(row.get("text", ""))[:LINE_CAPS[row["role"]]]
    if row["role"] == "user":
        return f'[{age}] user: "{text}"'
    if row["role"] == "agent":
        return f"[{age}] you: {text}"
    if row["role"] == "note":
        return f"[{age}] you (mid-run): {text}"
    if row["role"] == "event":
        return f"[{age}] (studio) {text}"
    v = str(row.get("verdict", "")).upper() or "VERDICT"
    return f"[{age}] user {v}ED the take" + (f': "{text}"' if text else "")


def _verdict_suffix(row):
    v = str(row.get("verdict", "")).lower()
    why = _clean(row.get("text", ""))[:LINE_CAPS["verdict"]]
    if v == "accept":
        held = int(row.get("held", 0) or 0)
        return " -> ACCEPTED" + (f" (user held back {held} notes)" if held else "")
    if v == "reject":
        return ' -> REJECTED' + (f': "{why}"' if why else " (no reason given)")
    return ""


def _items(rows, now):
    """Fold chronicle rows (oldest-first) into display items, NEWEST FIRST.
    Each item = (line, [rows it represents]); a prefix of items always covers a
    contiguous newest slice of rows, so budget cuts stay count-exact.
    Folding laws: a verdict decorates the agent line it judged; a run's notes
    fold silently into that run's final (the final subsumes them); only
    trailing notes with no final yet (in-flight / died run) get their own
    lines, capped at BLOCK_NOTES; stale orphans ride as hidden items."""
    items, pending_verdict, agent_item = [], None, None
    seen_final, notes_kept = False, 0
    for row in reversed(rows):
        role = row["role"]
        if role == "verdict":
            if pending_verdict is not None:       # two verdicts, no agent between
                items.append((_line(pending_verdict, now), [pending_verdict]))
            pending_verdict = row
            agent_item = None
            continue
        if role == "agent":
            ln, rep = _line(row, now), [row]
            if pending_verdict is not None:
                ln += _verdict_suffix(pending_verdict)
                rep.append(pending_verdict)
                pending_verdict = None
            items.append((ln, rep))
            agent_item, seen_final = items[-1], True
            continue
        if role == "note":
            if agent_item is not None:
                agent_item[1].append(row)         # subsumed by its run's final
            elif not seen_final and notes_kept < BLOCK_NOTES:
                notes_kept += 1
                items.append((_line(row, now), [row]))
            else:
                items.append(("", [row]))         # hidden: counted, not shown
            continue
        if pending_verdict is not None:           # verdict with no agent line
            items.append((_line(pending_verdict, now), [pending_verdict]))
            pending_verdict = None
        items.append((_line(row, now), [row]))    # user / event
        if role == "user":
            agent_item = None                     # run boundary crossed
    if pending_verdict is not None:
        items.append((_line(pending_verdict, now), [pending_verdict]))
    return items


def conversation_block(song, cap=BLOCK_CAP, now=None):
    """The bounded CONVERSATION MEMORY block for the prompt. Empty string when
    the project has no chat (honest miss) or the chronicle is disabled."""
    if not enabled():
        return ""
    rows = read(song)
    if not rows:
        return ""
    now = time.time() if now is None else float(now)
    take, used = [], 0
    for ln, rep in _items(rows, now):             # newest first; whole items only
        if ln and used + len(ln) + 1 > cap:
            break
        take.append((ln, rep))
        used += (len(ln) + 1) if ln else 0
    shown = sum(len(rep) for _, rep in take)
    older = rows[:max(0, len(rows) - shown)]
    out = [HEADER]
    if older:
        asks = sum(1 for r in older if r["role"] == "user")
        acc = sum(1 for r in older if r["role"] == "verdict"
                  and str(r.get("verdict", "")).lower() == "accept")
        rej = sum(1 for r in older if r["role"] == "verdict"
                  and str(r.get("verdict", "")).lower() == "reject")
        out.append(f"(+{len(older)} earlier messages: {asks} asks, {acc} accepted, "
                   f"{rej} rejected — full transcript in songs/.chat/)")
    out.extend(ln for ln, _ in reversed(take) if ln)   # newest LAST, nearest the ask
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: chronicle.py <song> [role text...]")
        sys.exit(2)
    if len(sys.argv) >= 4:
        print(json.dumps(append(sys.argv[1], sys.argv[2], " ".join(sys.argv[3:]))))
    print(conversation_block(sys.argv[1]) or "(no chat history)")
