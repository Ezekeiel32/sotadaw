#!/usr/bin/env python3
"""CHAT TRUTH (2026-08-02, "responses ARE STILL DOUBLED SOMETIMES! WHY?!").

THE DOUBLING MECHANISM, found with a live specimen: the run's final reply
reaches the feed twice —
  copy 1: the streamed assistant text, carded in FULL (last_carded);
  copy 2: the run-end "agent done: <result>" line, capped to [:2000]
          BEFORE the W99 dedup compare.
The dedup was `capped_result == full_card` — so any reply longer than the
cap could NEVER match and ALWAYS doubled (the specimen's second copy cut
mid-word at exactly the cap). "Sometimes" == "whenever the reply is long."

THE LAW: dedup on the RAW result, cap-blind and whitespace-calm —
`already_carded(raw_final, carded)` is the one kernel every rail calls.
A shared 600+-char prefix, or either side being a truncation-prefix of the
other, is the SAME reply; only genuinely different text earns a second
card. Pure, stdlib, battery-proven.
"""

# a shared prefix this long between two agent texts cannot be coincidence —
# it is one reply seen through two caps
PREFIX_SAME = 600


def _norm(s):
    # whitespace-calm: streaming and result payloads may disagree on
    # trailing spaces / newline runs, never on the words
    return " ".join(str(s or "").split())


def already_carded(final_text, carded_text):
    """True = this final is the reply the card already showed — emit the
    short 'agent done.' instead of a twin."""
    f = _norm(final_text)
    c = _norm(carded_text)
    if not f or not c:
        return False
    if f == c:
        return True
    # cap-blind: either side may have been truncated by an emit cap
    shorter, longer = (f, c) if len(f) <= len(c) else (c, f)
    if len(shorter) >= PREFIX_SAME and longer.startswith(shorter[:PREFIX_SAME]):
        return True
    return longer.startswith(shorter) and len(shorter) >= 80
