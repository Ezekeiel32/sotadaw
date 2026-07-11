#!/usr/bin/env python3
"""CHRONICLE BATTERY — proof for agent/chronicle.py (per-project conversation
memory). Pure, isolated (SOTADAW_IPC temp = the store namespaces away from live
chat), zero tokens.

Proves the claimed laws: write caps + role validation + never-raises, sanitize,
honest miss, kill switch, newest-LAST ordering, verdict folding (accept/reject
WHY verbatim, held-back count), note subsumption (a final eats its run's notes;
trailing in-flight notes survive, capped), the char-budget cut with a count-
exact aggregate line, standalone verdicts, garbage tolerance, the byte trim law
(hysteresis, newest survive), and read(limit).
"""
import json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = tempfile.mkdtemp(prefix="chronicle_ipc_")
os.environ["SOTADAW_IPC"] = IPC
os.environ.pop("SOTADAW_CHRONICLE", None)
sys.path.insert(0, os.path.join(ROOT, "agent"))
import chronicle as ch                        # noqa: E402

FAILS = []


def check(cond, label):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        FAILS.append(label)


def main():
    S = "unit_song"
    T0 = 1_000_000.0
    NOW = T0 + 7200.0

    # -------- namespacing + round trip
    check(ch.chat_dir().startswith(IPC), "store namespaces under SOTADAW_IPC")
    r = ch.append(S, "user", "make it darker", t=T0, revise=False)
    check(r and r["role"] == "user" and r["revise"] is False, "append returns the row")
    got = ch.read(S)
    check(len(got) == 1 and got[0]["text"] == "make it darker", "write -> read round trip")

    # -------- validation: bad role / empty text / unserializable extra never raise
    check(ch.append(S, "vibes", "x") is None, "unknown role rejected (None, no raise)")
    check(ch.append(S, "user", "   ") is None, "blank text rejected")
    check(ch.append(S, "user", "x", blob=object()) is None,
          "unserializable extra rejected without raising")
    check(len(ch.read(S)) == 1, "rejected writes left no rows")

    # -------- caps + sanitize
    ch.append(S, "note", "n" * 9999, t=T0 + 1)
    check(len(ch.read(S)[-1]["text"]) == ch.WRITE_CAPS["note"], "note capped at write")
    ch.append(S, "agent", "line one\n\n  line   two\ttabbed", t=T0 + 2)
    check(ch.read(S)[-1]["text"] == "line one line two tabbed",
          "whitespace/newlines sanitized to single spaces")

    # -------- kill switch
    os.environ["SOTADAW_CHRONICLE"] = "0"
    check(ch.append(S, "user", "ghost write") is None, "kill switch blocks writes")
    check(ch.conversation_block(S) == "", "kill switch blocks the block")
    os.environ.pop("SOTADAW_CHRONICLE")

    # -------- honest miss
    check(ch.conversation_block("never_spoken") == "", "no chat -> empty block (honest miss)")

    # -------- the canonical conversation: ask -> notes -> final -> verdict
    S2 = "story"
    ch.append(S2, "user", "make a dark acid drop", t=T0)
    ch.append(S2, "note", "reading the song structure", t=T0 + 10)
    ch.append(S2, "note", "the bass is a static A1 pedal", t=T0 + 20)
    ch.append(S2, "agent", "Built an 8-bar acid drop: 303 lead + A1 pedal.", t=T0 + 30)
    ch.append(S2, "verdict", "", verdict="accept", held=0, t=T0 + 40)
    ch.append(S2, "user", "now the arp sounds off-key in the drop", t=T0 + 100)
    ch.append(S2, "note", "pitch tally: fully diatonic A minor", t=T0 + 110)
    ch.append(S2, "note", "suspect: 303 resonance smearing inharmonic content", t=T0 + 120)
    blk = ch.conversation_block(S2, now=NOW)
    check(blk.startswith(ch.HEADER) and blk.endswith("\n"), "block: header + trailing newline")
    check('user: "make a dark acid drop"' in blk, "user ask quoted")
    check("-> ACCEPTED" in blk, "accept verdict decorates the agent line")
    check("reading the song structure" not in blk
          and "static A1 pedal" not in blk.split("you:")[0],
          "notes subsumed by their run's final are dropped")
    check("resonance smearing" in blk and "fully diatonic" in blk,
          "trailing in-flight notes survive (the died/streaming run's findings)")
    lines = blk.strip().splitlines()
    check(lines[-1].endswith("resonance smearing inharmonic content")
          and 'off-key' in lines[-3], "newest last, nearest the ask")

    # -------- reject WHY verbatim + held-back count
    S3 = "why"
    ch.append(S3, "user", "brighter hats", t=T0)
    ch.append(S3, "agent", "Opened the hat filter to 9k.", t=T0 + 5)
    ch.append(S3, "verdict", "way too bright, hurts", verdict="reject", t=T0 + 9)
    ch.append(S3, "user", "double the hook", t=T0 + 20)
    ch.append(S3, "agent", "Doubled it an octave up, quieter.", t=T0 + 25)
    ch.append(S3, "verdict", "", verdict="accept", held=3, t=T0 + 30)
    b3 = ch.conversation_block(S3, now=NOW)
    check('REJECTED: "way too bright, hurts"' in b3, "reject WHY rides verbatim")
    check("held back 3 notes" in b3, "held-back count rides the accept")

    # -------- standalone verdict (no agent row before it)
    S4 = "orphan_verdict"
    ch.append(S4, "user", "drop a groove on the drums", t=T0)
    ch.append(S4, "verdict", "", verdict="accept", t=T0 + 5)
    b4 = ch.conversation_block(S4, now=NOW)
    check("user ACCEPTED the take" in b4, "verdict with no agent line stands alone")

    # -------- stale orphan notes (older run died, newer run completed) stay hidden
    S5 = "stale_notes"
    ch.append(S5, "user", "first ask", t=T0)
    ch.append(S5, "note", "half-finished thought from a dead run", t=T0 + 5)
    ch.append(S5, "user", "second ask", t=T0 + 60)
    ch.append(S5, "agent", "Done.", t=T0 + 70)
    b5 = ch.conversation_block(S5, now=NOW)
    check("half-finished thought" not in b5, "stale orphan note hidden")
    check('"first ask"' in b5 and '"second ask"' in b5, "both asks present")

    # -------- budget cut + count-exact aggregate line
    S6 = "long_history"
    t = T0
    for i in range(30):
        ch.append(S6, "user", f"ask number {i} with some padding words to eat budget", t=t)
        ch.append(S6, "agent", f"Did edit {i}: moved the thing, rendered clean.", t=t + 5)
        ch.append(S6, "verdict", "" if i % 3 else "meh",
                  verdict="accept" if i % 3 else "reject", t=t + 9)
        t += 100
    b6 = ch.conversation_block(S6, now=NOW + 3600)
    check(len(b6) < ch.BLOCK_CAP + len(ch.HEADER) + 160, "block obeys the char budget")
    check("ask number 29" in b6, "newest turn always present")
    check("(+" in b6 and "earlier messages" in b6, "aggregate line for the cut history")
    import re as _re
    m = _re.search(r"\(\+(\d+) earlier messages: (\d+) asks, (\d+) accepted, (\d+) rejected",
                   b6)
    shown_users = b6.count('user: "')
    shown_acc = b6.count("-> ACCEPTED")
    shown_rej = b6.count("-> REJECTED")
    check(m and int(m.group(2)) + shown_users == 30, "aggregate ask count is exact")
    check(m and int(m.group(3)) + shown_acc == 20, "aggregate accept count is exact")
    check(m and int(m.group(4)) + shown_rej == 10, "aggregate reject count is exact")

    # -------- garbage tolerance
    with open(os.path.join(ch.chat_dir(), "story.jsonl"), "a") as f:
        f.write("NOT JSON {{{\n")
        f.write(json.dumps({"role": "user"}) + "\n")            # no text
        f.write(json.dumps({"role": "martian", "text": "x"}) + "\n")
    n_before = len(ch.read(S2))
    ch.append(S2, "user", "still alive?", t=T0 + 200)
    check(len(ch.read(S2)) == n_before + 1, "garbage lines skipped, file still appends")

    # -------- read(limit)
    tail2 = ch.read(S6, limit=2)
    check(len(tail2) == 2 and tail2[0]["text"].startswith("Did edit 29")
          and tail2[1]["role"] == "verdict", "read(limit) = newest N")

    # -------- trim law: bytes-bounded with hysteresis, newest survive
    S7 = "big"
    for i in range(900):
        ch.append(S7, "agent", f"row {i} " + "x" * 640, t=T0 + i)
    sz = os.path.getsize(os.path.join(ch.chat_dir(), "big.jsonl"))
    rows7 = ch.read(S7)
    check(sz <= ch.TRIM_BYTES and len(rows7) < 900,
          f"trim law: file bounded + a trim actually fired ({sz}B, {len(rows7)} rows)")
    check(rows7 and rows7[-1]["text"].startswith("row 899"), "trim keeps the newest rows")
    check(rows7[0]["text"].startswith("row ") and len(rows7) < 900, "oldest rows trimmed")

    # -------- event role renders as studio line
    S8 = "events"
    ch.append(S8, "event", "MAKE: psytrance track landed (seed 7)", t=T0)
    check("(studio) MAKE: psytrance" in ch.conversation_block(S8, now=NOW),
          "event rows render as (studio) lines")

    n = len(FAILS)
    print(f"\n== CHRONICLE BATTERY: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} ==")
    for f in FAILS:
        print("  - " + f)
    return 1 if n else 0


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        shutil.rmtree(IPC, ignore_errors=True)
    sys.exit(rc)
