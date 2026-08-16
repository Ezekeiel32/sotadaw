#!/usr/bin/env python3
"""CHAT TRUTH battery — the doubled-reply kernel, incl. the live specimen's
exact shape (full card vs a 2000-capped twin cut mid-word)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chat_truth as ct

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def main():
    long_reply = ("Stopped at the landing step - permissions block it. " * 60)
    ok(len(long_reply) > 2400, "specimen is longer than the emit cap")
    # THE SPECIMEN: full card, result capped at 2000 mid-word
    ok(ct.already_carded(long_reply[:2000], long_reply),
       "SPECIMEN: 2000-capped result vs full card = SAME reply")
    ok(ct.already_carded(long_reply, long_reply[:2000]),
       "...and symmetric (either side may be the capped one)")
    ok(ct.already_carded(long_reply, long_reply), "exact match dedups")
    ok(ct.already_carded("done.  \n", "done."),
       "whitespace drift never doubles")
    # genuinely different replies must still card
    ok(not ct.already_carded("the take is ready", "rendering failed"),
       "different short replies both show")
    a = "A" * 700
    b = "A" * 700 + " but then a completely different second half " + "B" * 700
    ok(ct.already_carded(a, b),
       "600+ shared prefix = one reply seen through a cap")
    ok(not ct.already_carded("A" * 300 + "X", "A" * 300 + "Y"),
       "short texts that diverge are different replies")
    ok(not ct.already_carded("", "something"), "empty final never dedups")
    ok(not ct.already_carded("something", ""), "empty card never dedups")
    ok(not ct.already_carded("ok", "o"),
       "tiny prefix overlap is not sameness")
    ok(ct.already_carded("the whole reply here, short and sweet plus enough "
                         "length to clear the eighty character containment "
                         "floor for prefix law",
                         "the whole reply here, short and sweet plus enough "
                         "length to clear the eighty character containment "
                         "floor for prefix law and one more clause the card "
                         "kept but the result dropped"),
       "sub-cap truncation-prefix (>=80 chars) still dedups")

    print(f"\nchat_truth_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
