#!/usr/bin/env python3
"""THE PASTED-ARTIFACT FENCE (2026-08-02, the untitled_65 trace).

An ask is two different things wearing one string: the user's INSTRUCTIONS,
and DATA they pasted for you to use (a tab, a chord chart, a lyric sheet,
a log, a JSON blob). Every word-level court in this codebase used to read
the whole string as instruction — so a 5-string banjo tab of "Journey of
the Sorcerer" produced, in one run:

  CONTRACT UNMET - bars: asked 16, take has 96   ("...repeat of bars 15-16"
                                                  + "\\n\\n  bars 21-22" — the
                                                  bars regex spanned a newline)
  CONTRACT UNMET - element: asked string, take has False   ("5-string banjo")
  ASK-BACK: 'open' is a LOW-agreement word                 ("open-G pedal")

Three nags, zero of them anything the user asked for. The fence is the fix:

  split(text) -> {"instruction", "artifacts", "has_chart", "kinds"}

INSTRUCTION is what the user is telling you to do; ARTIFACTS are the blocks
they pasted. Courts read `instruction`. The model still receives the whole
ask verbatim — fencing scopes the SCANNERS, never the prompt.

has_chart carries the second law (THE TRANSCRIPTION FENCE): when the user
hands over notation, those notes are the deliverable's TRUTH — the key /
melody / pocket heals must not "improve" them (that run re-pitched 92 of
the user's transcribed notes and nudged 831 timings).

Pure, dependency-free, never raises. Proof: tools/ask_fence_battery.py.
"""
import re

# a staff/grid line: "Eb|--0--------2p0----------------|" / "|x---x---|"
_DASHES = "-\u2010\u2011\u2012\u2013\u2014_="
_STEP_GRID = re.compile(r"^[\s|]*[xXoO.\-_*#\u00b7]{8,}[\s|]*$")
_TAB_HEAD = re.compile(r"^\s*(?:[A-Ga-g][#b]?\d?|\d)\s*[|:]")
_FENCE = re.compile(r"^\s*(```|~~~)")
# lines that are chart captions when they sit beside a staff
_CAPTION = re.compile(r"^\s*(?:bars?\b|measures?\b|\||[A-Ga-g][#b]?m?7?\s)", re.I)


def _is_staff(line):
    """True for a tab/step-grid staff line (data, not prose)."""
    s = line.strip()
    if len(s) < 6:
        return False
    if _STEP_GRID.match(s) and s.count("|") <= 4:
        return True               # step grids ("x..x..o..x..") are staves too
    dashes = sum(s.count(c) for c in _DASHES)
    if dashes >= 6 and dashes / len(s) >= 0.35:
        return True
    # "e|3-3-3|" style: short tab with a pitch head and pipes
    if _TAB_HEAD.match(s) and s.count("|") >= 2 and any(c.isdigit() for c in s):
        return True
    return False


def _is_blob(line):
    """A pasted JSON/log line — data by construction."""
    s = line.strip()
    if len(s) < 20:
        return False
    if s[0] in "{[" and s.count('"') >= 4:
        return True
    return bool(re.match(r"^\[?\d{4}-\d\d-\d\d[ T]\d\d:\d\d", s))


def split(text):
    """Split an ask into instruction text + pasted artifact blocks.

    Returns {"instruction": str, "artifacts": [str], "has_chart": bool,
             "kinds": [str], "fenced_lines": int}.
    Fail-open: anything unexpected returns the ask unchanged as instruction.
    """
    out = {"instruction": str(text or ""), "artifacts": [], "has_chart": False,
           "kinds": [], "fenced_lines": 0}
    try:
        raw = str(text or "")
        if not raw.strip():
            return out
        lines = raw.splitlines()
        n = len(lines)
        mark = [False] * n          # True = artifact (data), False = instruction

        # 1. explicit code fences own everything between them
        in_fence = False
        for i, ln in enumerate(lines):
            if _FENCE.match(ln):
                mark[i] = True
                in_fence = not in_fence
                continue
            if in_fence:
                mark[i] = True

        # 2. staff / grid / blob lines are data wherever they sit. Staves are
        #    detected on ALL lines (fenced included): a tab pasted between
        #    ``` fences is still a chart and the verbatim law must trip
        #    however the user wrapped it — but only unfenced staves need
        #    marking + caption absorption (fences already own theirs).
        staff_all = [i for i in range(n) if _is_staff(lines[i])]
        staff = [i for i in staff_all if not mark[i]]
        for i in staff:
            mark[i] = True
        for i in range(n):
            if not mark[i] and _is_blob(lines[i]):
                mark[i] = True

        # 3. a chart's caption rides with its staff. Captions sit ABOVE their
        #    block ("bars 3-4 - main vamp:" describes the staves below it), so
        #    the previous non-blank neighbour is absorbed freely; the line
        #    BELOW a block is only data if it looks like a caption/staff —
        #    prose resuming after a paste is INSTRUCTION ("make it knock"
        #    after a step grid must survive).
        for i in staff:
            j = i - 1
            if 0 <= j < n and not mark[j] and lines[j].strip() and (
                    _CAPTION.match(lines[j]) or _is_staff(lines[j])
                    or len(lines[j].strip()) <= 120):
                mark[j] = True
            j = i + 1
            if 0 <= j < n and not mark[j] and lines[j].strip() and (
                    _CAPTION.match(lines[j]) or _is_staff(lines[j])):
                mark[j] = True

        if not any(mark):
            return out

        # gather artifacts + the surviving instruction
        art, cur = [], []
        for i in range(n):
            if mark[i]:
                cur.append(lines[i])
            elif cur:
                art.append("\n".join(cur))
                cur = []
        if cur:
            art.append("\n".join(cur))

        instruction = "\n".join(lines[i] for i in range(n) if not mark[i])
        # collapse the blank runs the removal leaves behind
        instruction = re.sub(r"\n{3,}", "\n\n", instruction).strip()

        kinds = []
        if len(staff_all) >= 2:
            kinds.append("chart")
        if any(_FENCE.match(l) for l in lines):
            kinds.append("fenced")
        if any(_is_blob(l) for l in lines):
            kinds.append("blob")

        out.update({"instruction": instruction, "artifacts": art,
                    "has_chart": len(staff_all) >= 2, "kinds": kinds,
                    "fenced_lines": sum(1 for m in mark if m)})
        # a paste that leaves nothing behind is still an ask: keep the head
        # line so contracts have SOMETHING honest to read.
        if not out["instruction"]:
            out["instruction"] = (raw.strip().splitlines() or [""])[0][:300]
        return out
    except Exception:
        return out


def instruction_of(text):
    """The ask with pasted data fenced off — what a word-level court reads."""
    return split(text)["instruction"]


def has_chart(text):
    """True when the ask carries notation (tab/grid/chart) as pasted data."""
    return split(text)["has_chart"]


if __name__ == "__main__":       # tiny CLI: fence any ask on stdin
    import sys
    r = split(sys.stdin.read())
    print(f"has_chart={r['has_chart']} kinds={r['kinds']} "
          f"fenced_lines={r['fenced_lines']}\n--- INSTRUCTION ---\n"
          f"{r['instruction']}")
